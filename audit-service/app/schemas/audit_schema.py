from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional
from datetime import datetime
from uuid import UUID

# ---------------------------------------------------------------------------
# Valid event types
# ---------------------------------------------------------------------------

VALID_EVENT_TYPES = {
    "TRANSACTION_CREATED",
    "USER_REGISTERED",
    "ACCOUNT_CREATED",
    "KYC_DOCUMENT_SUBMITTED",
    "COMPLIANCE_ALERT_RAISED",
    "ADMIN_ACTION",
}


# ---------------------------------------------------------------------------
# Request / Response DTOs
# ---------------------------------------------------------------------------

class AuditEventCreate(BaseModel):
    """Payload accepted by POST /api/v1/audit/events."""

    event_type: str = Field(..., description="One of the defined event type constants")
    actor: Optional[str] = Field(None, description="Who performed the action")
    resource_type: Optional[str] = Field(None, description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of the affected resource")
    action: Optional[str] = Field(None, description="Action performed (e.g. CREATE)")
    description: Optional[str] = Field(None, description="Human-readable description")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional context")
    source_service: Optional[str] = Field(None, description="Service that raised the event")

    model_config = {"from_attributes": True}


class AuditEventResponse(BaseModel):
    """Full audit event returned in responses."""

    id: UUID
    event_type: str
    actor: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    action: Optional[str] = None
    description: Optional[str] = None
    # ORM model stores this as `event_metadata` to avoid the SQLAlchemy reserved name.
    # We read it via the field name, then serialize it as `metadata` in the JSON output.
    event_metadata: Optional[dict[str, Any]] = Field(
        None, serialization_alias="metadata"
    )
    source_service: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "serialize_by_alias": True,  # always output `metadata` not `event_metadata`
    }


class AuditEventListResponse(BaseModel):
    """Paginated list of audit events."""

    total: int
    limit: int
    offset: int
    events: list[AuditEventResponse]


class AuditStatsResponse(BaseModel):
    """Aggregate statistics about the audit trail."""

    total_events: int
    event_counts_by_type: dict[str, int]
    recent_activity: int  # events in the last 24 hours


class HealthResponse(BaseModel):
    """Simple health check response."""

    status: str
    service: str
    version: str
