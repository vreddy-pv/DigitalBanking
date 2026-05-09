import json
import logging
import asyncio
import threading
from typing import Callable
from urllib.parse import urlparse
import pika
from app.config import settings
from app.schemas.transaction_event import TransactionCreatedEvent

logger = logging.getLogger(__name__)


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


class TransactionEventListener:
    """Listen for TransactionCreatedEvent from RabbitMQ and trigger notifications.

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
    # Public async API (called from FastAPI lifecycle hooks)
    # ------------------------------------------------------------------

    async def start_listening(self, queue_name: str = "transaction_events") -> None:
        """Start the blocking RabbitMQ consumer in a thread executor."""
        self._loop = asyncio.get_event_loop()
        self._stop_event.clear()

        # Run blocking consumer in a thread so we don't block the event loop
        await self._loop.run_in_executor(
            None, self._blocking_consume, queue_name
        )

    async def disconnect(self) -> None:
        """Signal the consumer thread to stop."""
        self._stop_event.set()
        self.is_listening = False
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            logger.warning(f"Error closing RabbitMQ connection: {e}")

    # ------------------------------------------------------------------
    # Blocking consumer (runs in a thread executor)
    # ------------------------------------------------------------------

    def _blocking_consume(self, queue_name: str) -> None:
        """Connect to RabbitMQ and start blocking consume loop."""
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

            # Fair dispatch — process one message at a time
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message,
            )

            self.is_listening = True
            logger.info(f"RabbitMQ listener started on queue '{queue_name}'")

            # Blocking loop — exits when stop_consuming() is called
            while not self._stop_event.is_set():
                self.connection.process_data_events(time_limit=1)

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection failed: {e}")
            self.is_listening = False
        except Exception as e:
            logger.error(f"Unexpected error in RabbitMQ consumer: {e}")
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
            logger.info(
                f"Received TransactionCreatedEvent: {event_data.get('transactionId') or event_data.get('transaction_id')}"
            )

            # Normalise Java camelCase → Python snake_case field names
            normalised = _normalise_event(event_data)
            event = TransactionCreatedEvent(**normalised)

            # Schedule the async callback back onto the FastAPI event loop
            if self._loop and not self._loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(
                    self._handle_event(event), self._loop
                )
                # Wait (with timeout) so we ack only after processing
                try:
                    future.result(timeout=30)
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    logger.info(f"Acknowledged event: {event.transaction_id}")
                except Exception as e:
                    logger.error(f"Event processing failed: {e}")
                    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                logger.error("Event loop not available — nacking message")
                channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def _handle_event(self, event: TransactionCreatedEvent) -> None:
        """Invoke the registered async callback with the parsed event."""
        await self.on_event_callback(event)


# ------------------------------------------------------------------
# Helper — normalise Java camelCase event fields to Python snake_case
# ------------------------------------------------------------------

def _normalise_event(data: dict) -> dict:
    """Map Java-serialised camelCase field names to Python snake_case equivalents.

    Java TransactionCreatedEvent fields (Jackson default serialisation):
        transactionId, fromAccountId, toAccountId, type, amount,
        description, timestamp (long ms), recipientEmail, customerName, accountNumber
    """
    mapping = {
        "transactionId": "transaction_id",
        "fromAccountId": "from_account_id",
        "toAccountId": "to_account_id",
        "type": "transaction_type",          # Java field is "type", not "transactionType"
        "transactionType": "transaction_type",  # Also accept snake/camel variant
        "recipientEmail": "recipient_email",
        "customerName": "customer_name",
        "accountNumber": "account_number",
    }
    result = {}
    for key, value in data.items():
        snake_key = mapping.get(key, key)
        # Convert epoch-ms timestamp to ISO string for the Python schema
        if snake_key == "timestamp" and isinstance(value, (int, float)):
            from datetime import datetime, timezone
            value = datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
        result[snake_key] = value
    return result
