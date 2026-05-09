import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models.compliance_alert import ComplianceAlert, CustomerRiskProfile  # noqa: F401 — register models
from app.schemas.compliance_schema import TransactionCreatedEvent
from app.services import compliance_service
from app.events.transaction_listener import TransactionEventListener
from app.controllers.health_controller import health_router
from app.controllers.compliance_controller import compliance_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_listener: TransactionEventListener | None = None


async def _on_transaction_event(event_data: dict) -> None:
    """Process an incoming transaction event — run AML checks."""
    try:
        event = TransactionCreatedEvent(**event_data)
    except Exception as exc:
        logger.warning("Could not parse event: %s — %s", event_data, exc)
        return

    db = SessionLocal()
    try:
        result = compliance_service.process_transaction_event(db, event)
        if result.alerts_raised:
            logger.warning(
                "AML ALERT: txn=%s raised %d alert(s) — highest severity: %s types: %s",
                result.transaction_id, result.alerts_raised,
                result.highest_severity, result.alert_types,
            )
        else:
            logger.debug("AML clean: txn=%s", result.transaction_id)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _listener
    # Startup
    Base.metadata.create_all(bind=engine)
    logger.info("Compliance Service starting on port %d", settings.service_port)

    _listener = TransactionEventListener(on_event_callback=_on_transaction_event)
    asyncio.create_task(_listener.start_listening(settings.rabbitmq_queue))

    yield

    # Shutdown
    if _listener:
        await _listener.disconnect()
    logger.info("Compliance Service stopped")


app = FastAPI(
    title="Compliance Service",
    description="AML/KYC rule engine, suspicious transaction detection, customer risk scoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(compliance_router)


@app.get("/")
def root():
    return {"service": "compliance-service", "version": "1.0.0", "status": "running"}
