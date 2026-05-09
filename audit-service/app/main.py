"""Audit Service — FastAPI application entry point.

Uses the modern lifespan context manager (NOT the deprecated @app.on_event).
On startup:
  1. Creates DB tables (idempotent via SQLAlchemy metadata.create_all)
  2. Starts the RabbitMQ listener as a background asyncio task
On shutdown:
  1. Signals the listener to stop and cancels the background task
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['endpoint']
)

from app.config import settings
from app.database import engine, Base
from app.controllers.health_controller import router as health_router
from app.controllers.audit_controller import router as audit_router
from app.events.transaction_listener import TransactionEventListener
from app.schemas.audit_schema import AuditEventCreate
from app.services.audit_service import AuditService, AuditServiceError
from app.database import SessionLocal

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("audit-service")

# Module-level listener state (read by health controller)
event_listener: TransactionEventListener | None = None
listener_task: asyncio.Task | None = None

_audit_service = AuditService()


# ---------------------------------------------------------------------------
# RabbitMQ event → audit record
# ---------------------------------------------------------------------------

async def _handle_transaction_event(event) -> None:
    """Convert a TransactionCreatedEvent into an audit record."""
    db = SessionLocal()
    try:
        description = (
            f"{event.transaction_type} of {event.amount}"
            + (f" — {event.description}" if event.description else "")
        )
        payload = AuditEventCreate(
            event_type="TRANSACTION_CREATED",
            actor="system",
            resource_type="TRANSACTION",
            resource_id=event.transaction_id,
            action="CREATE",
            description=description,
            metadata={
                "transaction_type": event.transaction_type,
                "amount": event.amount,
                "from_account_id": event.from_account_id,
                "to_account_id": event.to_account_id,
                "timestamp": event.timestamp,
            },
            source_service="transaction-service",
        )
        _audit_service.create_event(db, payload)
        logger.info("Audit record created for transaction: %s", event.transaction_id)
    except AuditServiceError as exc:
        logger.error("Failed to create audit record for transaction %s: %s", event.transaction_id, exc)
    except Exception as exc:
        logger.error("Unexpected error auditing transaction %s: %s", event.transaction_id, exc)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_listener, listener_task

    # Startup
    logger.info(
        "Audit Service starting on %s:%s",
        settings.service_host,
        settings.service_port,
    )

    # Initialise DB tables (idempotent)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured")

    try:
        event_listener = TransactionEventListener(
            on_event_callback=_handle_transaction_event
        )
        listener_task = asyncio.create_task(
            event_listener.start_listening(queue_name=settings.rabbitmq_queue)
        )
        logger.info("RabbitMQ listener task started")
    except Exception as exc:
        logger.error("Failed to start RabbitMQ listener: %s", exc)
        # Don't abort startup — service can still handle REST requests

    yield  # Application runs here

    # Shutdown
    logger.info("Audit Service shutting down")
    try:
        if event_listener and event_listener.is_listening:
            await event_listener.disconnect()
        if listener_task and not listener_task.done():
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                logger.info("RabbitMQ listener task cancelled")
    except Exception as exc:
        logger.error("Error during shutdown: %s", exc)


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Audit Service",
    description="Immutable append-only audit trail for the Digital Banking Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router, tags=["Health"])
app.include_router(audit_router, prefix="/api/v1/audit", tags=["Audit"])


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower(),
    )
