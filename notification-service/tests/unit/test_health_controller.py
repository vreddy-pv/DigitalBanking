import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db


def make_db_override(raises=False):
    """Factory: returns a get_db override that either works or raises."""
    def override():
        db = MagicMock(spec=Session)
        if raises:
            db.execute.side_effect = Exception("DB connection error")
        yield db
    return override


class TestHealthController:
    """Tests for GET /health"""

    def test_health_check_all_up(self):
        """DB works + listener.is_listening=True → status UP, database UP, event_listener LISTENING"""
        app.dependency_overrides[get_db] = make_db_override(raises=False)
        try:
            mock_listener = MagicMock()
            mock_listener.is_listening = True

            with patch("app.main.event_listener", mock_listener):
                client = TestClient(app, raise_server_exceptions=True)
                response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "UP"
            assert data["database"] == "UP"
            assert data["event_listener"] == "LISTENING"
            assert data["service"] == "notification-service"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_health_check_db_down(self):
        """db.execute raises → database DOWN, overall status still UP (service responds)"""
        app.dependency_overrides[get_db] = make_db_override(raises=True)
        try:
            mock_listener = MagicMock()
            mock_listener.is_listening = True

            with patch("app.main.event_listener", mock_listener):
                client = TestClient(app, raise_server_exceptions=True)
                response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["database"] == "DOWN"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_health_check_listener_not_connected(self):
        """event_listener is None → NOT_CONNECTED"""
        app.dependency_overrides[get_db] = make_db_override(raises=False)
        try:
            with patch("app.main.event_listener", None):
                client = TestClient(app, raise_server_exceptions=True)
                response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["event_listener"] == "NOT_CONNECTED"
        finally:
            app.dependency_overrides.pop(get_db, None)

    def test_health_check_listener_not_listening(self):
        """event_listener.is_listening=False → NOT_CONNECTED"""
        app.dependency_overrides[get_db] = make_db_override(raises=False)
        try:
            mock_listener = MagicMock()
            mock_listener.is_listening = False

            with patch("app.main.event_listener", mock_listener):
                client = TestClient(app, raise_server_exceptions=True)
                response = client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["event_listener"] == "NOT_CONNECTED"
        finally:
            app.dependency_overrides.pop(get_db, None)
