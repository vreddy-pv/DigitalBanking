import logging

from fastapi import APIRouter
from app.schemas.audit_schema import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for the audit service."""
    return HealthResponse(
        status="healthy",
        service="audit-service",
        version="1.0.0",
    )
