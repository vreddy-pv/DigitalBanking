import pytest
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models.notification import Notification


# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def sample_notification(db_session):
    """Create a sample notification for testing"""
    notification = Notification(
        transaction_id=str(uuid4()),
        notification_type="EMAIL",
        recipient="test@example.com",
        subject="Test Notification",
        body="<h1>Test</h1>",
        status="SENT",
        attempts=1
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification


@pytest.fixture
def db_session():
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


class TestNotificationAPI:
    """Integration tests for Notification API"""

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "database" in data
        assert "event_listener" in data

    def test_get_notification_success(self, sample_notification):
        """Test retrieving a notification"""
        response = client.get(f"/api/v1/notifications/{sample_notification.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_notification.id)
        assert data["notification_type"] == "EMAIL"
        assert data["recipient"] == "test@example.com"
        assert data["status"] == "SENT"

    def test_get_notification_not_found(self):
        """Test retrieving non-existent notification"""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/notifications/{fake_id}")

        assert response.status_code == 404

    def test_list_notifications_empty(self):
        """Test listing notifications when empty"""
        response = client.get("/api/v1/notifications")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["notifications"] == []

    def test_list_notifications_with_filter_status(self, sample_notification):
        """Test listing notifications with status filter"""
        response = client.get("/api/v1/notifications?status=SENT")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["status"] == "SENT"

    def test_list_notifications_with_filter_transaction_id(self, sample_notification):
        """Test listing notifications with transaction_id filter"""
        response = client.get(
            f"/api/v1/notifications?transaction_id={sample_notification.transaction_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_list_notifications_pagination(self, db_session):
        """Test notification pagination"""
        # Create multiple notifications
        for i in range(25):
            notification = Notification(
                transaction_id=str(uuid4()),
                notification_type="EMAIL",
                recipient=f"test{i}@example.com",
                subject=f"Test {i}",
                body="Test",
                status="PENDING"
            )
            db_session.add(notification)
        db_session.commit()

        # Get first page (default limit 20)
        response = client.get("/api/v1/notifications")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["notifications"]) == 20

        # Get second page
        response = client.get("/api/v1/notifications?offset=20&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 5

    def test_retry_notification_success(self, db_session):
        """Test retrying a failed notification"""
        # Create a failed notification
        notification = Notification(
            transaction_id=uuid4(),
            notification_type="EMAIL",
            recipient="test@example.com",
            subject="Failed",
            body="Failed",
            status="FAILED",
            attempts=3,
            error_message="SMTP Error"
        )
        db_session.add(notification)
        db_session.commit()

        # Retry
        response = client.post(f"/api/v1/notifications/{notification.id}/retry")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["attempts"] == 0
        assert data["error_message"] is None

    def test_retry_notification_already_sent(self, sample_notification):
        """Test retrying a notification that was already sent"""
        response = client.post(
            f"/api/v1/notifications/{sample_notification.id}/retry"
        )

        assert response.status_code == 400

    def test_retry_notification_not_found(self):
        """Test retrying non-existent notification"""
        fake_id = uuid4()
        response = client.post(f"/api/v1/notifications/{fake_id}/retry")

        assert response.status_code == 404

    def test_notification_stats_empty(self):
        """Test notification stats when no notifications exist"""
        response = client.get("/api/v1/notifications/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_sent"] == 0
        assert data["total_failed"] == 0
        assert data["total_pending"] == 0
        assert data["success_rate"] == 0

    def test_notification_stats_with_data(self, db_session):
        """Test notification stats with various notification statuses"""
        # Create notifications with different statuses
        for i in range(10):
            status = "SENT" if i < 8 else "FAILED"
            notification = Notification(
                transaction_id=str(uuid4()),
                notification_type="EMAIL",
                recipient=f"test{i}@example.com",
                subject=f"Test {i}",
                body="Test",
                status=status
            )
            db_session.add(notification)
        db_session.commit()

        response = client.get("/api/v1/notifications/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_sent"] == 8
        assert data["total_failed"] == 2
        assert data["success_rate"] == 80.0
