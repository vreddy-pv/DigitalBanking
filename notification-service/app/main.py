from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
import asyncio
from app.config import settings
from app.database import engine, Base
from app.controllers import health_controller, notification_controller
from app.events.transaction_listener import TransactionEventListener
from app.events.event_consumer import TransactionEventConsumer

# Create tables
Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.service_name,
    version="1.0.0",
    description="Notification Service for Digital Banking Platform"
)

# Include routers
app.include_router(health_controller.router, prefix="", tags=["Health"])
app.include_router(notification_controller.router, prefix="/api/v1", tags=["Notifications"])

# Event listener state
event_consumer = None
event_listener = None
listener_task = None


@app.on_event("startup")
async def startup_event():
    global event_consumer, event_listener, listener_task

    logger.info(f"{settings.service_name} started on {settings.service_host}:{settings.service_port}")

    try:
        # Initialize event consumer and listener
        event_consumer = TransactionEventConsumer()
        event_listener = TransactionEventListener(
            on_event_callback=event_consumer.handle_transaction_created
        )

        # Start listening for transaction events in background
        listener_task = asyncio.create_task(
            event_listener.start_listening(queue_name="transaction_events")
        )

        logger.info("Transaction event listener initialized")

    except Exception as e:
        logger.error(f"Failed to initialize event listener: {str(e)}")
        # Don't fail startup, just log the error
        # Service can still handle API requests


@app.on_event("shutdown")
async def shutdown_event():
    global event_listener, listener_task

    logger.info(f"{settings.service_name} shutting down")

    try:
        # Stop event listener
        if event_listener and event_listener.is_listening:
            await event_listener.disconnect()

        # Cancel listener task
        if listener_task and not listener_task.done():
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                logger.info("Event listener task cancelled")

        logger.info("Event listener shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower()
    )
