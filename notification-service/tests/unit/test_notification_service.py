import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.notification_service import NotificationService, NotificationServiceError
from app.models.notification import Notification


@pytest.fixture
def notification_service():
    """Fixture for NotificationService"""
    return NotificationService()


@pytest.fixture
def mock_db():
    """Fixture for mock database session"""
    return MagicMock(spec=Session)


@pytest.fixture
def sample_notification():
    """Fixture for sample notification"""
    return Notification(
        id=str(uuid4()),
        transaction_id=str(uuid4()),
        notification_type="EMAIL",
        recipient="test@example.com",
        subject="Test Notification",
        body="<h1>Test</h1>",
        status="PENDING",
        attempts=0,
        max_attempts=3
    )


class TestNotificationService:
    """Test suite for NotificationService"""

    @pytest.mark.asyncio
    async def test_create_notification_success(self, notification_service, mock_db):
        """Test creating notification successfully"""
        transaction_id = uuid4()

        notification = await notification_service.create_notification(
            db=mock_db,
            transaction_id=transaction_id,
            notification_type="EMAIL",
            recipient="test@example.com",
            subject="Test",
            body="Test body"
        )

        # Verify database calls
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_notification_db_error(self, notification_service, mock_db):
        """Test notification creation with database error"""
        mock_db.add.side_effect = Exception("DB Error")

        with pytest.raises(NotificationServiceError):
            await notification_service.create_notification(
                db=mock_db,
                transaction_id=uuid4(),
                notification_type="EMAIL",
                recipient="test@example.com",
                subject="Test",
                body="Test body"
            )

        mock_db.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_email_success(
        self, notification_service, mock_db, sample_notification
    ):
        """Test sending email notification successfully"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification

        with patch.object(
            notification_service.email_service,
            "send_email",
            return_value=True
        ):
            result = await notification_service.send_notification(
                db=mock_db,
                notification_id=sample_notification.id
            )

        assert result is True
        assert sample_notification.status == "SENT"
        assert sample_notification.attempts == 1
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_not_found(self, notification_service, mock_db):
        """Test sending notification that doesn't exist"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await notification_service.send_notification(
            db=mock_db,
            notification_id=uuid4()
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_max_attempts_exceeded(
        self, notification_service, mock_db
    ):
        """Test sending notification when max attempts exceeded"""
        notification = Notification(
            id=uuid4(),
            transaction_id=uuid4(),
            notification_type="EMAIL",
            recipient="test@example.com",
            subject="Test",
            body="Test",
            status="PENDING",
            attempts=3,  # Already at max
            max_attempts=3
        )
        mock_db.query.return_value.filter.return_value.first.return_value = notification

        result = await notification_service.send_notification(
            db=mock_db,
            notification_id=notification.id
        )

        assert result is False
        assert notification.status == "FAILED"

    @pytest.mark.asyncio
    async def test_send_notification_sms_success(
        self, notification_service, mock_db
    ):
        """Test sending SMS notification successfully"""
        notification = Notification(
            id=uuid4(),
            transaction_id=uuid4(),
            notification_type="SMS",
            recipient="+1234567890",
            subject="",
            body="Test SMS",
            status="PENDING",
            attempts=0,
            max_attempts=3
        )
        mock_db.query.return_value.filter.return_value.first.return_value = notification

        with patch.object(
            notification_service.sms_service,
            "send_sms",
            return_value=True
        ):
            result = await notification_service.send_notification(
                db=mock_db,
                notification_id=notification.id
            )

        assert result is True
        assert notification.status == "SENT"

    @pytest.mark.asyncio
    async def test_send_notification_unknown_type(
        self, notification_service, mock_db
    ):
        """Test sending notification with unknown type"""
        notification = Notification(
            id=uuid4(),
            transaction_id=uuid4(),
            notification_type="UNKNOWN",
            recipient="test@example.com",
            subject="Test",
            body="Test",
            status="PENDING",
            attempts=0,
            max_attempts=3
        )
        mock_db.query.return_value.filter.return_value.first.return_value = notification

        result = await notification_service.send_notification(
            db=mock_db,
            notification_id=notification.id
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_email_failure_retryable(
        self, notification_service, mock_db
    ):
        """Test email sending failure with retry available"""
        notification = Notification(
            id=uuid4(),
            transaction_id=uuid4(),
            notification_type="EMAIL",
            recipient="test@example.com",
            subject="Test",
            body="Test",
            status="PENDING",
            attempts=1,
            max_attempts=3
        )
        mock_db.query.return_value.filter.return_value.first.return_value = notification

        with patch.object(
            notification_service.email_service,
            "send_email",
            return_value=False
        ):
            result = await notification_service.send_notification(
                db=mock_db,
                notification_id=notification.id
            )

        assert result is False
        assert notification.status == "PENDING"  # Still pending, can retry
        assert notification.attempts == 2

    @pytest.mark.asyncio
    async def test_retry_notification_success(
        self, notification_service, mock_db, sample_notification
    ):
        """Test retrying a failed notification"""
        sample_notification.status = "FAILED"
        sample_notification.attempts = 3
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification

        with patch.object(
            notification_service,
            "send_notification",
            return_value=True
        ):
            result = await notification_service.retry_notification(
                db=mock_db,
                notification_id=sample_notification.id
            )

        assert result is True
        assert sample_notification.status == "PENDING"
        assert sample_notification.attempts == 0
        assert sample_notification.error_message is None

    @pytest.mark.asyncio
    async def test_retry_notification_already_sent(
        self, notification_service, mock_db, sample_notification
    ):
        """Test retrying a notification that was already sent"""
        sample_notification.status = "SENT"
        mock_db.query.return_value.filter.return_value.first.return_value = sample_notification

        result = await notification_service.retry_notification(
            db=mock_db,
            notification_id=sample_notification.id
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_retry_notification_not_found(self, notification_service, mock_db):
        """Test retrying notification that doesn't exist"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await notification_service.retry_notification(
            db=mock_db,
            notification_id=uuid4()
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_handle_transaction_event_deposit(
        self, notification_service, mock_db
    ):
        """Test handling deposit transaction event"""
        transaction_id = uuid4()

        with patch.object(
            notification_service,
            "create_notification",
            return_value=MagicMock()
        ), patch.object(
            notification_service,
            "send_notification",
            return_value=True
        ):
            notification = await notification_service.handle_transaction_event(
                db=mock_db,
                transaction_id=transaction_id,
                transaction_type="DEPOSIT",
                amount=1000.00,
                from_account_id=None,
                to_account_id="ACC-002",
                description="Deposit",
                recipient_email="test@example.com",
                customer_name="John Doe",
                account_number="ACC-002",
                timestamp="2026-05-08T10:30:00Z"
            )

        assert notification is not None

    @pytest.mark.asyncio
    async def test_handle_transaction_event_withdrawal(
        self, notification_service, mock_db
    ):
        """Test handling withdrawal transaction event"""
        with patch.object(
            notification_service,
            "create_notification",
            return_value=MagicMock()
        ), patch.object(
            notification_service,
            "send_notification",
            return_value=True
        ):
            notification = await notification_service.handle_transaction_event(
                db=mock_db,
                transaction_id=uuid4(),
                transaction_type="WITHDRAWAL",
                amount=500.00,
                from_account_id="ACC-001",
                to_account_id=None,
                description="Withdrawal",
                recipient_email="test@example.com",
                customer_name="John Doe",
                account_number="ACC-001",
                timestamp="2026-05-08T10:30:00Z"
            )

        assert notification is not None

    @pytest.mark.asyncio
    async def test_handle_transaction_event_invalid_type(
        self, notification_service, mock_db
    ):
        """Test handling transaction with invalid type"""
        with pytest.raises(NotificationServiceError):
            await notification_service.handle_transaction_event(
                db=mock_db,
                transaction_id=uuid4(),
                transaction_type="INVALID",
                amount=100.00,
                from_account_id=None,
                to_account_id="ACC-001",
                description="Invalid",
                recipient_email="test@example.com",
                customer_name="John Doe",
                account_number="ACC-001",
                timestamp="2026-05-08T10:30:00Z"
            )
