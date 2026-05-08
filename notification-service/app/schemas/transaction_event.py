from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class TransactionCreatedEvent(BaseModel):
    """Event published by Transaction Service"""
    transaction_id: str = Field(..., description="Unique transaction ID")
    transaction_type: str = Field(..., description="DEPOSIT, WITHDRAWAL, or TRANSFER")
    amount: float = Field(..., gt=0, description="Transaction amount")
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: str = Field(..., description="ISO 8601 timestamp")

    # Notification fields
    recipient_email: Optional[str] = None
    customer_name: Optional[str] = None
    account_number: Optional[str] = None

    class Config:
        from_attributes = True
