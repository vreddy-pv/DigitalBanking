import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.database import Base


class AuditEvent(Base):
    """Immutable append-only audit event record.

    No UPDATE or DELETE operations are ever performed on this table at the
    application level.  Rows are inserted once and never modified.
    """

    __tablename__ = "audit_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_type = Column(String(100), nullable=False)
    actor = Column(String(255), nullable=True)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(255), nullable=True)
    action = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    event_metadata = Column("metadata", JSONB, nullable=True)
    source_service = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_audit_events_event_type", "event_type"),
        Index("idx_audit_events_resource", "resource_type", "resource_id"),
        Index("idx_audit_events_created_at", "created_at"),
        Index("idx_audit_events_actor", "actor"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditEvent(id={self.id}, event_type={self.event_type}, "
            f"resource_type={self.resource_type}, resource_id={self.resource_id})>"
        )
