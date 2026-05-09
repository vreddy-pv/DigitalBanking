"""RabbitMQ consumer for TransactionCreatedEvent.

Uses the exact same pattern as notification-service:
  - pika.BlockingConnection running in a thread executor
  - asyncio bridge via run_coroutine_threadsafe
  - Ack only after the async callback succeeds; Nack+requeue on failure
"""
import asyncio
import json
import logging
import threading
from datetime import datetime, timezone
from typing import Callable
from urllib.parse import urlparse

import pika

from app.config import settings
from app.schemas.transaction_event import TransactionCreatedEvent

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# URL parsing helper
# ---------------------------------------------------------------------------

def _parse_rabbitmq_url(url: str) -> dict:
    """Parse amqp://user:pass@host:port/vhost into pika connection params."""
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5672,
        "username": parsed.username or "guest",
        "password": parsed.password or "guest",
        "virtual_host": parsed.path.lstrip("/") or "/",
    }


# ---------------------------------------------------------------------------
# Normalise Java camelCase → Python snake_case
# ---------------------------------------------------------------------------

def _normalise_event(data: dict) -> dict:
    """Map Java-serialised camelCase field names to Python snake_case equivalents."""
    mapping = {
        "transactionId": "transaction_id",
        "fromAccountId": "from_account_id",
        "toAccountId": "to_account_id",
        "type": "transaction_type",
        "transactionType": "transaction_type",
        "recipientEmail": "recipient_email",
        "customerName": "customer_name",
        "accountNumber": "account_number",
    }
    result = {}
    for key, value in data.items():
        snake_key = mapping.get(key, key)
        if snake_key == "timestamp" and isinstance(value, (int, float)):
            value = datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
        result[snake_key] = value
    return result


# ---------------------------------------------------------------------------
# Listener class
# ---------------------------------------------------------------------------

class TransactionEventListener:
    """Listen for TransactionCreatedEvent from RabbitMQ and create audit records.

    Uses pika.BlockingConnection in a background thread so the FastAPI
    async event loop is not blocked.
    """

    def __init__(self, on_event_callback: Callable):
        self.on_event_callback = on_event_callback
        self.connection: pika.BlockingConnection | None = None
        self.channel = None
        self.is_listening = False
        self._stop_event = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None

    # ------------------------------------------------------------------
    # Public async API (called from FastAPI lifespan)
    # ------------------------------------------------------------------

    async def start_listening(self, queue_name: str = "transaction_events") -> None:
        """Start the blocking RabbitMQ consumer in a thread executor."""
        self._loop = asyncio.get_event_loop()
        self._stop_event.clear()
        await self._loop.run_in_executor(None, self._blocking_consume, queue_name)

    async def disconnect(self) -> None:
        """Signal the consumer thread to stop."""
        self._stop_event.set()
        self.is_listening = False
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as exc:
            logger.warning("Error closing RabbitMQ connection: %s", exc)

    # ------------------------------------------------------------------
    # Blocking consumer (runs in a thread executor)
    # ------------------------------------------------------------------

    def _blocking_consume(self, queue_name: str) -> None:
        params = _parse_rabbitmq_url(settings.rabbitmq_url)
        credentials = pika.PlainCredentials(params["username"], params["password"])
        connection_params = pika.ConnectionParameters(
            host=params["host"],
            port=params["port"],
            virtual_host=params["virtual_host"],
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=5,
            retry_delay=2,
        )

        try:
            self.connection = pika.BlockingConnection(connection_params)
            self.channel = self.connection.channel()

            # Declare exchange + queue + binding (idempotent)
            self.channel.exchange_declare(
                exchange="banking.events",
                exchange_type="topic",
                durable=True,
            )
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.queue_bind(
                queue=queue_name,
                exchange="banking.events",
                routing_key="transaction.created",
            )

            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message,
            )

            self.is_listening = True
            logger.info("RabbitMQ audit listener started on queue '%s'", queue_name)

            while not self._stop_event.is_set():
                self.connection.process_data_events(time_limit=1)

        except pika.exceptions.AMQPConnectionError as exc:
            logger.error("RabbitMQ connection failed: %s", exc)
            self.is_listening = False
        except Exception as exc:
            logger.error("Unexpected error in RabbitMQ audit consumer: %s", exc)
            self.is_listening = False
        finally:
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
            except Exception:
                pass

    def _on_message(self, channel, method, properties, body: bytes) -> None:
        """Callback invoked by pika for each incoming message."""
        try:
            event_data = json.loads(body.decode("utf-8"))
            tx_id = event_data.get("transactionId") or event_data.get("transaction_id")
            logger.info("Received TransactionCreatedEvent: %s", tx_id)

            normalised = _normalise_event(event_data)
            event = TransactionCreatedEvent(**normalised)

            if self._loop and not self._loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(
                    self._handle_event(event), self._loop
                )
                try:
                    future.result(timeout=30)
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info("Acknowledged audit event for transaction: %s", event.transaction_id)
                except Exception as exc:
                    logger.error("Audit event processing failed: %s", exc)
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.error("Event loop not available — nacking message")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in message: %s", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as exc:
            logger.error("Error handling RabbitMQ message: %s", exc)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def _handle_event(self, event: TransactionCreatedEvent) -> None:
        """Invoke the registered async callback with the parsed event."""
        await self.on_event_callback(event)
