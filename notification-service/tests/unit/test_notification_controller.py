import pytest
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models.notification import Notification


def _make_notification(status="SENT", attempts=1):
    """Helper: build a minimal Notification ORM-like object."""
    n = Notification(
        id=str(uuid.uuid4()),
        transaction_id=str(uuid.uuid4()),
        notification_type="EMAIL",
        recipient="user@example.com",
        subject="Test Subject",
        body="<p>Test body</p>",
        status=status,
        attempts=attempts,
        max_attempts=3,
        error_message=None,
        sent_at=datetime.now(timezone.utc) if status == "SENT" else None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return n


class TestNotificationController:
    """Tests for /api/v1/notifications endpoints."""

    # ------------------------------------------------------------------
    # GET /api/v1/notifications
    # ------------------------------------------------------------------

    def test_get_notifications_success(self):
        """Returns list of notifications."""
        n = _make_notification()

        def override():
            db = MagicMock(spec=Session)
            # list_notifications calls db.query(Notification) once; the resulting
            # query object is reused for both count() and the chained all() call.
            query_mock = MagicMock()
            query_mock.filter.return_value = query_mock
            query_mock.count.return_value = 1
            query_mock.order_by.return_value = query_mock
            query_mock.offset.return_value = query_mock
            query_mock.limit.return_value = query_mock
            query_mock.all.return_value = [n]
            db.query.return_value = query_mock
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            response = client.get("/api/v1/notifications")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["notifications"]) == 1
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_get_notifications_empty(self):
        """Returns empty list when no notifications exist."""
        def override():
            db = MagicMock(spec=Session)
            query_mock = MagicMock()
            query_mock.filter.return_value = query_mock
            query_mock.count.return_value = 0
            query_mock.order_by.return_value = query_mock
            query_mock.offset.return_value = query_mock
            query_mock.limit.return_value = query_mock
            query_mock.all.return_value = []
            db.query.return_value = query_mock
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            response = client.get("/api/v1/notifications")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["notifications"] == []
        finally:
            app.dependency_overrides.pop(get_db, None)

    # ------------------------------------------------------------------
    # GET /api/v1/notifications/{id}
    # ------------------------------------------------------------------

    def test_get_notification_by_id_success(self):
        """Returns 200 with notification data when found."""
        n = _make_notification()

        def override():
            db = MagicMock(spec=Session)
            db.query.return_value.filter.return_value.first.return_value = n
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            response = client.get(f"/api/v1/notifications/{n.id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == n.id
            assert data["status"] == "SENT"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_get_notification_by_id_not_found(self):
        """Returns 404 when notification does not exist."""
        def override():
            db = MagicMock(spec=Session)
            db.query.return_value.filter.return_value.first.return_value = None
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            random_id = str(uuid.uuid4())
            response = client.get(f"/api/v1/notifications/{random_id}")

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.pop(get_db, None)

    # ------------------------------------------------------------------
    # POST /api/v1/notifications/{id}/retry
    # ------------------------------------------------------------------

    def test_retry_notification_success(self):
        """Resets FAILED notification to PENDING and returns 200."""
        n = _make_notification(status="FAILED", attempts=3)

        def override():
            db = MagicMock(spec=Session)
            db.query.return_value.filter.return_value.first.return_value = n
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            response = client.post(f"/api/v1/notifications/{n.id}/retry")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "PENDING"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_retry_notification_not_found(self):
        """Returns 404 when notification to retry does not exist."""
        def override():
            db = MagicMock(spec=Session)
            db.query.return_value.filter.return_value.first.return_value = None
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            random_id = str(uuid.uuid4())
            response = client.post(f"/api/v1/notifications/{random_id}/retry")

            assert response.status_code == 404
        finally:
            app.dependency_overrides.pop(get_db, None)

    # ------------------------------------------------------------------
    # GET /api/v1/notifications/stats
    # Note: this route is defined AFTER /{notification_id} in the router,
    # but FastAPI resolves "stats" as a literal path segment correctly.
    # ------------------------------------------------------------------

    def test_get_notification_stats(self):
        """Returns counts and success rate."""
        def override():
            db = MagicMock(spec=Session)
            # The stats endpoint calls db.query(...).filter(...).scalar() three times.
            # Each call to db.query() returns a new mock chain; we use side_effect on
            # the top-level db.query so that successive calls return independent mocks.
            scalar_values = iter([10, 2, 3])

            def make_chain():
                m = MagicMock()
                m.filter.return_value.scalar.return_value = next(scalar_values)
                return m

            db.query.side_effect = lambda *a, **kw: make_chain()
            yield db

        app.dependency_overrides[get_db] = override
        try:
            client = TestClient(app, raise_server_exceptions=True)
            response = client.get("/api/v1/notifications/stats")

            assert response.status_code == 200
            data = response.json()
            assert "total_sent" in data
            assert "total_failed" in data
            assert "total_pending" in data
            assert "success_rate" in data
        finally:
            app.dependency_overrides.pop(get_db, None)
