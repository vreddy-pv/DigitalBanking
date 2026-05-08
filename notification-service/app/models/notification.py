import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, Index
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(36), nullable=False, index=True)
    notification_type = Column(String(20), nullable=False)  # EMAIL, SMS
    recipient = Column(String(255), nullable=False)
    subject = Column(String(255))  # For email
    body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, SENT, FAILED
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_notifications_transaction_id", "transaction_id"),
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, transaction_id={self.transaction_id}, status={self.status})>"
