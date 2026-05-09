import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.controllers.health_controller import health_router
from app.controllers.analytics_controller import analytics_router

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


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
