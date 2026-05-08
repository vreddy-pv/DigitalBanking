from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from app.config import settings
from app.database import engine, Base
from app.controllers import health_controller, notification_controller

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


@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.service_name} started on {settings.service_host}:{settings.service_port}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port,
        log_level=settings.log_level.lower()
    )
