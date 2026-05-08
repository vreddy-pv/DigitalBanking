from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class NotificationResponse(BaseModel):
    id: uuid.UUID
    transaction_id: uuid.UUID
    notification_type: str
    recipient: str
    subject: Optional[str] = None
    body: str
    status: str
    attempts: int
    max_attempts: int
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    total: int
    notifications: list[NotificationResponse]


class HealthResponse(BaseModel):
    status: str
    database: str
    event_listener: str
    service: str


class NotificationStatsResponse(BaseModel):
    total_sent: int
    total_failed: int
    total_pending: int
    retry_queue: int
    success_rate: float
