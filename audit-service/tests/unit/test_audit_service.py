"""Unit tests for AuditService.

8 tests covering: create, validation, query, stats, and append-only guarantee.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.schemas.audit_schema import AuditEventCreate
from app.services.audit_service import AuditService, AuditServiceError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def audit_service() -> AuditService:
    return AuditService()


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock(spec=Session)


def _make_event(**kwargs) -> AuditEvent:
    """Helper to build an AuditEvent ORM object with sensible defaults."""
    defaults = dict(
        id=uuid4(),
        event_type="TRANSACTION_CREATED",
        actor="system",
        resource_type="TRANSACTION",
        resource_id=str(uuid4()),
        action="CREATE",
        description="DEPOSIT of 500.0",
        metadata={"amount": 500.0},
        source_service="transaction-service",
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    obj = AuditEvent()
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


# ---------------------------------------------------------------------------
# 1. test_create_audit_event_success
# ---------------------------------------------------------------------------

def test_create_audit_event_success(audit_service, mock_db):
    """Happy-path: valid payload inserts a row and returns the event."""
    payload = AuditEventCreate(
        event_type="TRANSACTION_CREATED",
        actor="system",
        resource_type="TRANSACTION",
        resource_id=str(uuid4()),
        action="CREATE",
        description="DEPOSIT of 200.0",
        source_service="transaction-service",
    )

    # mock_db.refresh should set the id on the object passed to it
    def side_refresh(obj):
        obj.id = uuid4()
        obj.created_at = datetime.now(timezone.utc)

    mock_db.refresh.side_effect = side_refresh

    result = audit_service.create_event(mock_db, payload)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


# ---------------------------------------------------------------------------
# 2. test_create_audit_event_invalid_type
# ---------------------------------------------------------------------------

def test_create_audit_event_invalid_type(audit_service, mock_db):
    """Supplying an unknown event_type must raise AuditServiceError."""
    payload = AuditEventCreate(
        event_type="TOTALLY_INVALID_TYPE",
        actor="hacker",
        resource_type="THING",
        resource_id="abc-123",
        action="DELETE",
    )

    with pytest.raises(AuditServiceError, match="Invalid event_type"):
        audit_service.create_event(mock_db, payload)

    # Nothing should be written to the database
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# 3. test_query_events_by_resource
# ---------------------------------------------------------------------------

def test_query_events_by_resource(audit_service, mock_db):
    """Filtering by resource_type + resource_id applies the right WHERE clauses."""
    resource_id = str(uuid4())
    fake_event = _make_event(resource_type="TRANSACTION", resource_id=resource_id)

    # Build a chainable mock for db.query(...).filter(...).count() / .all()
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [fake_event]
    mock_db.query.return_value = mock_query

    events, total = audit_service.query_events(
        mock_db,
        resource_type="TRANSACTION",
        resource_id=resource_id,
    )

    assert total == 1
    assert len(events) == 1
    assert events[0].resource_id == resource_id


# ---------------------------------------------------------------------------
# 4. test_query_events_by_actor
# ---------------------------------------------------------------------------

def test_query_events_by_actor(audit_service, mock_db):
    """Filtering by actor returns only events for that actor."""
    fake_event = _make_event(actor="admin-user")

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 1
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [fake_event]
    mock_db.query.return_value = mock_query

    events, total = audit_service.query_events(mock_db, actor="admin-user")

    assert total == 1
    assert events[0].actor == "admin-user"


# ---------------------------------------------------------------------------
# 5. test_query_events_with_date_filter
# ---------------------------------------------------------------------------

def test_query_events_with_date_filter(audit_service, mock_db):
    """start_date and end_date filters are forwarded to the query."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=1)
    end = now

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.count.return_value = 0
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []
    mock_db.query.return_value = mock_query

    events, total = audit_service.query_events(
        mock_db, start_date=start, end_date=end
    )

    assert total == 0
    assert events == []
    # filter should have been called at least twice (for start_date and end_date)
    assert mock_query.filter.call_count >= 2


# ---------------------------------------------------------------------------
# 6. test_get_single_event
# ---------------------------------------------------------------------------

def test_get_single_event(audit_service, mock_db):
    """get_event_by_id returns the event when it exists."""
    event_id = uuid4()
    fake_event = _make_event(id=event_id)

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = fake_event
    mock_db.query.return_value = mock_query

    result = audit_service.get_event_by_id(mock_db, event_id)

    assert result is not None
    assert result.id == event_id


# ---------------------------------------------------------------------------
# 7. test_get_stats
# ---------------------------------------------------------------------------

def test_get_stats(audit_service, mock_db):
    """get_stats returns total_events, event_counts_by_type, recent_activity."""
    # Mock db.query(func.count(AuditEvent.id)).scalar() → 42
    # Mock group_by query → [("TRANSACTION_CREATED", 30), ("USER_REGISTERED", 12)]
    # Mock recent activity count → 5

    call_count = [0]

    def query_side_effect(*args, **kwargs):
        mock_q = MagicMock()
        call_count[0] += 1
        n = call_count[0]
        if n == 1:
            # total count
            mock_q.scalar.return_value = 42
        elif n == 2:
            # group_by query
            mock_q.group_by.return_value = mock_q
            mock_q.all.return_value = [
                ("TRANSACTION_CREATED", 30),
                ("USER_REGISTERED", 12),
            ]
        else:
            # recent activity count
            mock_q.filter.return_value = mock_q
            mock_q.scalar.return_value = 5
        mock_q.filter.return_value = mock_q
        return mock_q

    mock_db.query.side_effect = query_side_effect

    stats = audit_service.get_stats(mock_db)

    assert "total_events" in stats
    assert "event_counts_by_type" in stats
    assert "recent_activity" in stats


# ---------------------------------------------------------------------------
# 8. test_append_only_no_update
# ---------------------------------------------------------------------------

def test_append_only_no_update(audit_service):
    """AuditService must not expose any update or delete methods.

    This test enforces the core design constraint: the audit trail is
    immutable.  If someone adds an update() or delete() method in the future,
    this test will catch it and force a conscious design review.
    """
    forbidden_methods = [
        "update", "update_event", "delete", "delete_event",
        "patch", "modify", "edit", "remove",
    ]
    for method_name in forbidden_methods:
        assert not hasattr(audit_service, method_name), (
            f"AuditService must not have a '{method_name}' method — "
            "the audit trail is append-only."
        )
