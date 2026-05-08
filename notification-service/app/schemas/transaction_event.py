from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class TransactionCreatedEvent(BaseModel):
    """Event published by Transaction Service"""
    transaction_id: uuid.UUID
    from_account_id: Optional[uuid.UUID] = None
    to_account_id: Optional[uuid.UUID] = None
    type: str  # DEPOSIT, WITHDRAWAL, TRANSFER
    amount: float
    description: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
