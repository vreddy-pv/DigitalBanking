import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.events.transaction_listener import TransactionEventListener
from app.schemas.transaction_event import TransactionCreatedEvent


@pytest.fixture
def mock_callback():
    """Fixture for mock event callback"""
    return AsyncMock()


@pytest.fixture
def event_listener(mock_callback):
    """Fixture for TransactionEventListener"""
    return TransactionEventListener(on_event_callback=mock_callback)


@pytest.fixture
def sample_event_data():
    """Fixture for sample event data"""
    return {
        "transaction_id": str(uuid4()),
        "transaction_type": "DEPOSIT",
        "amount": 1000.00,
        "from_account_id": None,
        "to_account_id": "ACC-002",
        "description": "Deposit transaction",
        "recipient_email": "customer@example.com",
        "customer_name": "John Doe",
        "account_number": "ACC-002",
        "timestamp": "2026-05-08T10:30:00Z"
    }


class TestTransactionEventListener:
    """Test suite for TransactionEventListener"""

    def test_event_listener_initialization(self, mock_callback):
        """Test event listener initialization"""
        listener = TransactionEventListener(on_event_callback=mock_callback)

        assert listener.on_event_callback == mock_callback
        assert listener.connection is None
        assert listener.channel is None
        assert listener.is_listening is False

    def test_message_parsing_success(self, event_listener, sample_event_data):
        """Test successful message parsing"""
        # Create mock RabbitMQ objects
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        # Encode event data as JSON bytes
        body = json.dumps(sample_event_data).encode("utf-8")

        # Mock asyncio.create_task to avoid async handling issues in sync callback
        with patch("asyncio.create_task") as mock_create_task:
            # Parse should succeed
            event_listener._on_message_callback(mock_channel, mock_method, None, body)

            # Should create async task for event handling
            mock_create_task.assert_called_once()

    def test_message_parsing_invalid_json(self, event_listener):
        """Test parsing invalid JSON"""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        # Invalid JSON body
        body = b"invalid json {{"

        event_listener._on_message_callback(mock_channel, mock_method, None, body)

        # Should nack (negative acknowledge) the message
        mock_channel.basic_nack.assert_called_once()
        call_kwargs = mock_channel.basic_nack.call_args[1]
        assert call_kwargs["delivery_tag"] == 1
        assert call_kwargs["requeue"] is False

    def test_message_parsing_invalid_event_structure(self, event_listener):
        """Test parsing event with invalid structure"""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        # Valid JSON but missing required fields
        invalid_event = {"transaction_id": "123"}
        body = json.dumps(invalid_event).encode("utf-8")

        event_listener._on_message_callback(mock_channel, mock_method, None, body)

        # Should nack the message
        mock_channel.basic_nack.assert_called_once()

    def test_event_callback_invoked(self, event_listener, sample_event_data):
        """Test that callback is invoked for valid events"""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        body = json.dumps(sample_event_data).encode("utf-8")

        with patch("asyncio.create_task") as mock_create_task:
            event_listener._on_message_callback(mock_channel, mock_method, None, body)

            # Verify task was created
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_success(self, event_listener, sample_event_data):
        """Test successful event handling"""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        event = TransactionCreatedEvent(**sample_event_data)

        await event_listener._handle_event(event, mock_channel, mock_method)

        # Should acknowledge message
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
        # Should call the callback
        event_listener.on_event_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_callback_error(self, event_listener, sample_event_data):
        """Test event handling with callback error"""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        # Mock callback to raise error
        event_listener.on_event_callback.side_effect = Exception("Processing error")

        event = TransactionCreatedEvent(**sample_event_data)

        await event_listener._handle_event(event, mock_channel, mock_method)

        # Should nack (negative acknowledge) the message for retry
        mock_channel.basic_nack.assert_called_once()
        call_kwargs = mock_channel.basic_nack.call_args[1]
        assert call_kwargs["delivery_tag"] == 1
        assert call_kwargs["requeue"] is True  # Requeue for retry
