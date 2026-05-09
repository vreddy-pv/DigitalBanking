"""Business logic for the audit trail.

DESIGN RULE: This service is APPEND-ONLY.  There are intentionally no
update() or delete() methods.  The audit_events table must never be
mutated after a row is inserted.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.schemas.audit_schema import AuditEventCreate, VALID_EVENT_TYPES

logger = logging.getLogger(__name__)


class AuditServiceError(Exception):
    """Raised when an unrecoverable error occurs inside AuditService."""


class AuditService:
    """Append-only audit event service."""

    # ------------------------------------------------------------------
    # Write — create only, never update or delete
    # ------------------------------------------------------------------

    def create_event(self, db: Session, payload: AuditEventCreate) -> AuditEvent:
        """Persist a new audit event.

        Raises:
            AuditServiceError: if event_type is not in VALID_EVENT_TYPES or
                               if the database insert fails.
        """
        if payload.event_type not in VALID_EVENT_TYPES:
            raise AuditServiceError(
                f"Invalid event_type '{payload.event_type}'. "
                f"Must be one of: {sorted(VALID_EVENT_TYPES)}"
            )

        try:
            event = AuditEvent(
                event_type=payload.event_type,
                actor=payload.actor,
                resource_type=payload.resource_type,
                resource_id=payload.resource_id,
                action=payload.action,
                description=payload.description,
                event_metadata=payload.metadata,
                source_service=payload.source_service,
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            logger.info(
                "Audit event created: id=%s event_type=%s resource=%s/%s",
                event.id,
                event.event_type,
                event.resource_type,
                event.resource_id,
            )
            return event
        except AuditServiceError:
            raise
        except Exception as exc:
            db.rollback()
            logger.error("Failed to persist audit event: %s", exc)
            raise AuditServiceError(f"Database error: {exc}") from exc

    # ------------------------------------------------------------------
    # Read — query helpers
    # ------------------------------------------------------------------

    def get_event_by_id(self, db: Session, event_id: UUID) -> Optional[AuditEvent]:
        """Return a single audit event by primary key, or None."""
        return db.query(AuditEvent).filter(AuditEvent.id == event_id).first()

    def query_events(
        self,
        db: Session,
        *,
        event_type: Optional[str] = None,
        actor: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditEvent], int]:
        """Return (events, total_count) matching the given filters.

        All filters are optional and are AND-ed together when provided.
        """
        query = db.query(AuditEvent)

        if event_type:
            query = query.filter(AuditEvent.event_type == event_type)
        if actor:
            query = query.filter(AuditEvent.actor == actor)
        if resource_type:
            query = query.filter(AuditEvent.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditEvent.resource_id == resource_id)
        if start_date:
            query = query.filter(AuditEvent.created_at >= start_date)
        if end_date:
            query = query.filter(AuditEvent.created_at <= end_date)

        total = query.count()
        events = (
            query.order_by(AuditEvent.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return events, total

    def get_events_for_resource(
        self, db: Session, resource_type: str, resource_id: str
    ) -> list[AuditEvent]:
        """Return all audit events for a specific resource, newest first."""
        return (
            db.query(AuditEvent)
            .filter(
                AuditEvent.resource_type == resource_type,
                AuditEvent.resource_id == resource_id,
            )
            .order_by(AuditEvent.created_at.desc())
            .all()
        )

    def get_stats(self, db: Session) -> dict[str, Any]:
        """Return aggregate statistics about the audit trail."""
        total_events = db.query(func.count(AuditEvent.id)).scalar() or 0

        # Count by event_type
        counts_query = (
            db.query(AuditEvent.event_type, func.count(AuditEvent.id))
            .group_by(AuditEvent.event_type)
            .all()
        )
        event_counts_by_type = {row[0]: row[1] for row in counts_query}

        # Recent activity: events in the last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_activity = (
            db.query(func.count(AuditEvent.id))
            .filter(AuditEvent.created_at >= cutoff)
            .scalar()
            or 0
        )

        return {
            "total_events": total_events,
            "event_counts_by_type": event_counts_by_type,
            "recent_activity": recent_activity,
        }
