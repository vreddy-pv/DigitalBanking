from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime


class TransactionCreatedEvent(BaseModel):
    """Incoming RabbitMQ event from Transaction Service."""
    transaction_id: str
    transaction_type: str
    amount: float
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[Any] = None   # int (ms epoch) or ISO string from Java
    recipient_email: Optional[str] = None
    customer_name: Optional[str] = None
    account_number: Optional[str] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class AmlCheckResult(BaseModel):
    """Result of running AML rules against a transaction."""
    transaction_id: str
    alerts_raised: int
    alert_types: List[str]
    highest_severity: str  # LOW, MEDIUM, HIGH, CRITICAL, NONE


class AlertResponse(BaseModel):
    id: str
    transaction_id: str
    account_id: str
    customer_name: Optional[str]
    amount: float
    transaction_type: str
    alert_type: str
    severity: str
    description: str
    status: str
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertResponse]


class ReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(REVIEWED|CLEARED|ESCALATED)$")
    reviewed_by: str = Field(..., min_length=1)
    review_notes: Optional[str] = None


class RiskProfileResponse(BaseModel):
    customer_id: str
    risk_score: int
    risk_level: str
    alert_count: int
    high_alert_count: int
    last_assessed_at: datetime

    model_config = {"from_attributes": True}


class ComplianceStats(BaseModel):
    total_alerts: int
    pending_alerts: int
    cleared_alerts: int
    escalated_alerts: int
    high_risk_customers: int
    alerts_by_severity: dict
    alerts_by_type: dict


class ManualCheckRequest(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    transaction_type: str
    customer_name: Optional[str] = None
