from fastapi import APIRouter
from app.schemas.analytics_schema import HealthResponse

health_router = APIRouter()


@health_router.get("/api/v1/analytics/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="healthy",
        service="analytics-service",
        version="1.0.0",
    )
