import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.events.event_consumer import TransactionEventConsumer
from app.schemas.transaction_event import TransactionCreatedEvent


@pytest.fixture
def event_consumer():
    """Fixture for TransactionEventConsumer"""
    return TransactionEventConsumer()


@pytest.fixture
def sample_deposit_event():
    """Fixture for sample deposit event"""
    return TransactionCreatedEvent(
        transaction_id=str(uuid4()),
        transaction_type="DEPOSIT",
        amount=1000.00,
        from_account_id=None,
        to_account_id="ACC-002",
        description="Deposit to account",
        recipient_email="customer@example.com",
        customer_name="John Doe",
        account_number="ACC-002",
        timestamp="2026-05-08T10:30:00Z"
    )


@pytest.fixture
def sample_withdrawal_event():
    """Fixture for sample withdrawal event"""
    return TransactionCreatedEvent(
        transaction_id=str(uuid4()),
        transaction_type="WITHDRAWAL",
        amount=500.00,
        from_account_id="ACC-001",
        to_account_id=None,
        description="Withdrawal from account",
        recipient_email="customer@example.com",
        customer_name="Jane Smith",
        account_number="ACC-001",
        timestamp="2026-05-08T11:00:00Z"
    )


@pytest.fixture
def sample_transfer_event():
    """Fixture for sample transfer event"""
    return TransactionCreatedEvent(
        transaction_id=str(uuid4()),
        transaction_type="TRANSFER",
        amount=250.00,
        from_account_id="ACC-001",
        to_account_id="ACC-002",
        description="Transfer between accounts",
        recipient_email="sender@example.com",
        customer_name="John Doe",
        account_number="ACC-001",
        timestamp="2026-05-08T11:30:00Z"
    )


class TestTransactionEventConsumer:
    """Test suite for TransactionEventConsumer"""

    @pytest.mark.asyncio
    async def test_handle_deposit_event(self, event_consumer, sample_deposit_event):
        """Test handling deposit transaction event"""
        with patch.object(
            event_consumer.notification_service,
            "handle_transaction_event",
            return_value=MagicMock()
        ) as mock_handle:
            await event_consumer.handle_transaction_created(sample_deposit_event)

            mock_handle.assert_called_once()
            call_kwargs = mock_handle.call_args[1]
            assert call_kwargs["transaction_type"] == "DEPOSIT"
            assert call_kwargs["amount"] == 1000.00
            assert call_kwargs["to_account_id"] == "ACC-002"

    @pytest.mark.asyncio
    async def test_handle_withdrawal_event(self, event_consumer, sample_withdrawal_event):
        """Test handling withdrawal transaction event"""
        with patch.object(
            event_consumer.notification_service,
            "handle_transaction_event",
            return_value=MagicMock()
        ) as mock_handle:
            await event_consumer.handle_transaction_created(sample_withdrawal_event)

            mock_handle.assert_called_once()
            call_kwargs = mock_handle.call_args[1]
            assert call_kwargs["transaction_type"] == "WITHDRAWAL"
            assert call_kwargs["amount"] == 500.00
            assert call_kwargs["from_account_id"] == "ACC-001"

    @pytest.mark.asyncio
    async def test_handle_transfer_event(self, event_consumer, sample_transfer_event):
        """Test handling transfer transaction event"""
        with patch.object(
            event_consumer.notification_service,
            "handle_transaction_event",
            return_value=MagicMock()
        ) as mock_handle:
            await event_consumer.handle_transaction_created(sample_transfer_event)

            mock_handle.assert_called_once()
            call_kwargs = mock_handle.call_args[1]
            assert call_kwargs["transaction_type"] == "TRANSFER"
            assert call_kwargs["from_account_id"] == "ACC-001"
            assert call_kwargs["to_account_id"] == "ACC-002"

    @pytest.mark.asyncio
    async def test_handle_invalid_transaction_type(self, event_consumer):
        """Test handling invalid transaction type"""
        invalid_event = TransactionCreatedEvent(
            transaction_id=str(uuid4()),
            transaction_type="INVALID",
            amount=100.00,
            from_account_id=None,
            to_account_id="ACC-001",
            description="Invalid transaction",
            recipient_email="test@example.com",
            customer_name="Test User",
            account_number="ACC-001",
            timestamp="2026-05-08T12:00:00Z"
        )

        # Should handle gracefully without raising
        await event_consumer.handle_transaction_created(invalid_event)

    @pytest.mark.asyncio
    async def test_handle_notification_service_error(self, event_consumer, sample_deposit_event):
        """Test handling notification service error"""
        with patch.object(
            event_consumer.notification_service,
            "handle_transaction_event",
            side_effect=Exception("Service error")
        ):
            with pytest.raises(Exception):
                await event_consumer.handle_transaction_created(sample_deposit_event)
