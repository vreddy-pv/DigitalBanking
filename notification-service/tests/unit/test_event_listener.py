import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.events.transaction_listener import TransactionEventListener, _normalise_event
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
    """Fixture for sample event data (Python snake_case, as already normalised)"""
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
        "timestamp": "2026-05-08T10:30:00Z",
    }


@pytest.fixture
def java_event_data():
    """Fixture for Java-style camelCase event data (as published by Transaction Service)"""
    return {
        "transaction_id": str(uuid4()),   # already annotated with @JsonProperty
        "transaction_type": "DEPOSIT",    # @JsonProperty("transaction_type")
        "amount": 1000.00,
        "from_account_id": None,
        "to_account_id": "ACC-002",
        "description": "Deposit transaction",
        "recipient_email": "customer@example.com",
        "customer_name": "John Doe",
        "account_number": "ACC-002",
        "timestamp": 1715161800000,       # epoch-ms from Java long
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
        """Valid JSON message → basic_ack called, future resolved."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        body = json.dumps(sample_event_data).encode("utf-8")

        # _on_message calls run_coroutine_threadsafe; mock both the loop and the future
        mock_future = MagicMock()
        mock_future.result.return_value = None  # successful processing

        mock_loop = MagicMock()
        mock_loop.is_closed.return_value = False
        event_listener._loop = mock_loop

        with patch("asyncio.run_coroutine_threadsafe", return_value=mock_future):
            event_listener._on_message(mock_channel, mock_method, None, body)

        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
        mock_channel.basic_nack.assert_not_called()

    def test_message_parsing_invalid_json(self, event_listener):
        """Invalid JSON → basic_nack with requeue=False (dead-letter)."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        body = b"invalid json {{"

        event_listener._on_message(mock_channel, mock_method, None, body)

        mock_channel.basic_nack.assert_called_once()
        call_kwargs = mock_channel.basic_nack.call_args[1]
        assert call_kwargs["delivery_tag"] == 1
        assert call_kwargs["requeue"] is False

    def test_message_parsing_invalid_event_structure(self, event_listener):
        """Valid JSON but missing required fields → basic_nack."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        # Missing required 'amount' and 'transaction_type'
        invalid_event = {"transaction_id": "123"}
        body = json.dumps(invalid_event).encode("utf-8")

        event_listener._on_message(mock_channel, mock_method, None, body)

        mock_channel.basic_nack.assert_called_once()

    def test_event_callback_invoked(self, event_listener, sample_event_data):
        """Valid message → run_coroutine_threadsafe invoked with _handle_event."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 1

        body = json.dumps(sample_event_data).encode("utf-8")

        mock_future = MagicMock()
        mock_future.result.return_value = None

        mock_loop = MagicMock()
        mock_loop.is_closed.return_value = False
        event_listener._loop = mock_loop

        with patch("asyncio.run_coroutine_threadsafe", return_value=mock_future) as mock_rcts:
            event_listener._on_message(mock_channel, mock_method, None, body)

        # Coroutine was scheduled
        mock_rcts.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_event_success(self, event_listener, sample_event_data):
        """_handle_event delegates to the registered async callback."""
        event = TransactionCreatedEvent(**sample_event_data)

        await event_listener._handle_event(event)

        event_listener.on_event_callback.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_handle_event_callback_error(self, event_listener, sample_event_data):
        """_handle_event propagates exceptions raised by the callback."""
        event_listener.on_event_callback.side_effect = Exception("Processing error")

        event = TransactionCreatedEvent(**sample_event_data)

        with pytest.raises(Exception, match="Processing error"):
            await event_listener._handle_event(event)


class TestNormaliseEvent:
    """Unit tests for the camelCase → snake_case normaliser."""

    def test_java_camel_to_python_snake(self):
        data = {
            "transactionId": "abc",
            "fromAccountId": "f1",
            "toAccountId": "t1",
            "type": "DEPOSIT",
            "amount": 100,
            "recipientEmail": "a@b.com",
            "customerName": "Alice",
            "accountNumber": "ACC-1",
        }
        result = _normalise_event(data)
        assert result["transaction_id"] == "abc"
        assert result["from_account_id"] == "f1"
        assert result["to_account_id"] == "t1"
        assert result["transaction_type"] == "DEPOSIT"
        assert result["recipient_email"] == "a@b.com"
        assert result["customer_name"] == "Alice"
        assert result["account_number"] == "ACC-1"

    def test_epoch_ms_timestamp_converted_to_iso(self):
        data = {"timestamp": 1715161800000}
        result = _normalise_event(data)
        # Should be an ISO string, not an int
        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"]

    def test_snake_case_passthrough(self):
        """Already-normalised fields are left unchanged."""
        data = {"transaction_id": "xyz", "transaction_type": "TRANSFER", "amount": 50}
        result = _normalise_event(data)
        assert result["transaction_id"] == "xyz"
        assert result["transaction_type"] == "TRANSFER"
