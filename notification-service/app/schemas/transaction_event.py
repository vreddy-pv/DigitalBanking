from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any


class TransactionCreatedEvent(BaseModel):
    """Event published by Transaction Service via RabbitMQ.

    Accepts both Java camelCase keys (after normalisation in transaction_listener)
    and Python snake_case keys.  All notification fields are Optional so the
    service degrades gracefully when the Java side doesn't supply them yet.
    """
    transaction_id: str = Field(..., description="Unique transaction ID")
    transaction_type: str = Field(..., description="DEPOSIT, WITHDRAWAL, or TRANSFER")
    amount: float = Field(..., description="Transaction amount")
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None

    # Enrichment fields — populated by Transaction Service (or left empty for MVP)
    recipient_email: Optional[str] = None
    customer_name: Optional[str] = None
    account_number: Optional[str] = None

    @field_validator("transaction_type")
    @classmethod
    def normalise_type(cls, v: str) -> str:
        return v.upper() if v else v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("amount must be positive")
        return val

    model_config = {"from_attributes": True, "populate_by_name": True}
