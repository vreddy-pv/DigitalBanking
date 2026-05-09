"""Audit REST API endpoints.

IMPORTANT — route ordering:
  /events/stats        must be declared BEFORE /events/{event_id}
  /events/resource/... must be declared BEFORE /events/{event_id}
to avoid FastAPI treating "stats" or "resource" as an event_id path param.
"""
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.audit_schema import (
    AuditEventCreate,
    AuditEventListResponse,
    AuditEventResponse,
    AuditStatsResponse,
)
from app.services.audit_service import AuditService, AuditServiceError

router = APIRouter()
logger = logging.getLogger(__name__)

_audit_service = AuditService()


# ---------------------------------------------------------------------------
# POST /events  — create an audit event
# ---------------------------------------------------------------------------

@router.post(
    "/events",
    response_model=AuditEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_event(
    payload: AuditEventCreate,
    db: Session = Depends(get_db),
) -> AuditEventResponse:
    """Record a new audit event (append-only)."""
    try:
        event = _audit_service.create_event(db, payload)
        return AuditEventResponse.model_validate(event)
    except AuditServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


# ---------------------------------------------------------------------------
# GET /events/stats  — MUST be before /events/{event_id}
# ---------------------------------------------------------------------------

@router.get("/events/stats", response_model=AuditStatsResponse)
async def get_audit_stats(db: Session = Depends(get_db)) -> AuditStatsResponse:
    """Return aggregate statistics about the audit trail."""
    stats = _audit_service.get_stats(db)
    return AuditStatsResponse(**stats)


# ---------------------------------------------------------------------------
# GET /events/resource/{resource_type}/{resource_id}  — MUST be before /{event_id}
# ---------------------------------------------------------------------------

@router.get(
    "/events/resource/{resource_type}/{resource_id}",
    response_model=list[AuditEventResponse],
)
async def get_events_for_resource(
    resource_type: str,
    resource_id: str,
    db: Session = Depends(get_db),
) -> list[AuditEventResponse]:
    """Return all audit events for a specific resource (e.g. a transaction UUID)."""
    events = _audit_service.get_events_for_resource(db, resource_type, resource_id)
    return [AuditEventResponse.model_validate(e) for e in events]


# ---------------------------------------------------------------------------
# GET /events  — paginated list with optional filters
# ---------------------------------------------------------------------------

@router.get("/events", response_model=AuditEventListResponse)
async def list_audit_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    actor: Optional[str] = Query(None, description="Filter by actor"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Filter events on or after this datetime"),
    end_date: Optional[datetime] = Query(None, description="Filter events on or before this datetime"),
    limit: int = Query(50, ge=1, le=500, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> AuditEventListResponse:
    """Return a paginated list of audit events with optional filters."""
    events, total = _audit_service.query_events(
        db,
        event_type=event_type,
        actor=actor,
        resource_type=resource_type,
        resource_id=resource_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return AuditEventListResponse(
        total=total,
        limit=limit,
        offset=offset,
        events=[AuditEventResponse.model_validate(e) for e in events],
    )


# ---------------------------------------------------------------------------
# GET /events/{event_id}  — MUST be declared last
# ---------------------------------------------------------------------------

@router.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: UUID,
    db: Session = Depends(get_db),
) -> AuditEventResponse:
    """Return a single audit event by ID."""
    event = _audit_service.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event {event_id} not found",
        )
    return AuditEventResponse.model_validate(event)
