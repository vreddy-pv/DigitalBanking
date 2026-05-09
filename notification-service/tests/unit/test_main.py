import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestAppStartup:
    """Tests for FastAPI app startup event."""

    @pytest.mark.asyncio
    async def test_app_startup_success(self):
        """
        Startup creates TransactionEventConsumer + TransactionEventListener
        and schedules a background listener task.
        """
        mock_consumer = MagicMock()
        mock_consumer.handle_transaction_created = AsyncMock()

        mock_listener = MagicMock()
        mock_listener.start_listening = AsyncMock()

        # We patch at the module level so the startup event sees the mocks.
        with patch(
            "app.main.TransactionEventConsumer",
            return_value=mock_consumer,
        ) as MockConsumer, patch(
            "app.main.TransactionEventListener",
            return_value=mock_listener,
        ) as MockListener, patch(
            "app.main.asyncio.create_task",
        ) as mock_create_task:
            # Import startup function after patching
            from app.main import startup_event

            await startup_event()

            MockConsumer.assert_called_once()
            MockListener.assert_called_once()
            mock_create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_app_startup_listener_failure(self):
        """
        When TransactionEventListener raises during construction,
        startup_event catches the exception and does not re-raise it.
        The service continues to start normally.
        """
        with patch(
            "app.main.TransactionEventConsumer",
            side_effect=Exception("RabbitMQ not available"),
        ):
            from app.main import startup_event

            # Must NOT raise
            await startup_event()


class TestAppShutdown:
    """Tests for FastAPI app shutdown event."""

    @pytest.mark.asyncio
    async def test_app_shutdown(self):
        """
        Shutdown calls disconnect on a listening event_listener
        and cancels the listener_task.
        """
        mock_listener = MagicMock()
        mock_listener.is_listening = True
        mock_listener.disconnect = AsyncMock()

        # Create a real task that can be cancelled (must be created inside the
        # running event loop, which asyncio.create_task() guarantees).
        async def _dummy():
            await asyncio.sleep(100)

        dummy_task = asyncio.create_task(_dummy())

        with patch("app.main.event_listener", mock_listener), patch(
            "app.main.listener_task", dummy_task
        ):
            from app.main import shutdown_event

            await shutdown_event()

        mock_listener.disconnect.assert_called_once()
        assert dummy_task.cancelled()

    @pytest.mark.asyncio
    async def test_app_shutdown_no_listener(self):
        """
        Shutdown is graceful when event_listener is None.
        """
        with patch("app.main.event_listener", None), patch(
            "app.main.listener_task", None
        ):
            from app.main import shutdown_event

            # Should complete without errors
            await shutdown_event()
