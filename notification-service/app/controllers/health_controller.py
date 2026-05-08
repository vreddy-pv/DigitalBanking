from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.notification_schema import HealthResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for the notification service"""

    database_status = "UP"
    event_listener_status = "LISTENING"

    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        database_status = "DOWN"

    return HealthResponse(
        status="UP",
        database=database_status,
        event_listener=event_listener_status,
        service="notification-service"
    )
