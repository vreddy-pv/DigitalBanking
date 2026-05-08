from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification_schema import (
    NotificationResponse,
    NotificationListResponse,
    NotificationStatsResponse
)
from typing import Optional
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieve a specific notification by ID"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return notification


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    transaction_id: Optional[uuid.UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List notifications with optional filtering"""
    query = db.query(Notification)

    if transaction_id:
        query = query.filter(Notification.transaction_id == transaction_id)

    if status:
        query = query.filter(Notification.status == status)

    total = query.count()
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    return NotificationListResponse(
        total=total,
        notifications=notifications
    )


@router.post("/notifications/{notification_id}/retry")
async def retry_notification(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retry sending a failed notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.status == "SENT":
        raise HTTPException(status_code=400, detail="Cannot retry a successfully sent notification")

    # Reset for retry
    notification.status = "PENDING"
    notification.attempts = 0
    notification.error_message = None

    db.commit()
    db.refresh(notification)

    return NotificationResponse.from_orm(notification)


@router.get("/notifications/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(db: Session = Depends(get_db)):
    """Get notification statistics"""
    total_sent = db.query(func.count(Notification.id)).filter(
        Notification.status == "SENT"
    ).scalar() or 0

    total_failed = db.query(func.count(Notification.id)).filter(
        Notification.status == "FAILED"
    ).scalar() or 0

    total_pending = db.query(func.count(Notification.id)).filter(
        Notification.status == "PENDING"
    ).scalar() or 0

    total = total_sent + total_failed + total_pending or 1
    success_rate = (total_sent / total * 100) if total > 0 else 0

    return NotificationStatsResponse(
        total_sent=total_sent,
        total_failed=total_failed,
        total_pending=total_pending,
        retry_queue=total_pending,
        success_rate=success_rate
    )
