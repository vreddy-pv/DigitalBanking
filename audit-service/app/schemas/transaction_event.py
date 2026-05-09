"""Transaction event schema — reused from notification-service pattern.

This schema mirrors the TransactionCreatedEvent published by the Java
Transaction Service via RabbitMQ.  Field names are normalised from Java
camelCase to Python snake_case by the listener before the model is
instantiated.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional


class TransactionCreatedEvent(BaseModel):
    """Event published by Transaction Service via RabbitMQ."""

    transaction_id: str = Field(..., description="Unique transaction ID")
    transaction_type: str = Field(..., description="DEPOSIT, WITHDRAWAL, or TRANSFER")
    amount: float = Field(..., description="Transaction amount")
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[str] = None

    # Enrichment fields — populated by Transaction Service or left empty for MVP
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
