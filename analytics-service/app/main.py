import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import settings
from app.controllers.health_controller import health_router
from app.controllers.analytics_controller import analytics_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("analytics-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analytics Service starting on port %s", settings.service_port)
    yield
    logger.info("Analytics Service shutting down")


app = FastAPI(
    title="Analytics Service",
    description="Read-only CQRS analytics service for the Digital Banking platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(analytics_router, prefix="/api/v1/analytics")
