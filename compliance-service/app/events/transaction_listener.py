"""
RabbitMQ consumer for TransactionCreatedEvent.
Same pika.BlockingConnection + asyncio bridge pattern as notification-service.
"""

import json
import logging
import asyncio
import threading
from typing import Callable
from urllib.parse import urlparse

import pika

from app.config import settings

logger = logging.getLogger(__name__)


def _parse_rabbitmq_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5672,
        "username": parsed.username or "guest",
        "password": parsed.password or "guest",
        "virtual_host": parsed.path.lstrip("/") or "/",
    }


def _camel_to_snake(d: dict) -> dict:
    """Normalise Java camelCase keys to Python snake_case."""
    mapping = {
        "transactionId": "transaction_id",
        "transactionType": "transaction_type",
        "fromAccountId": "from_account_id",
        "toAccountId": "to_account_id",
        "recipientEmail": "recipient_email",
        "customerName": "customer_name",
        "accountNumber": "account_number",
    }
    return {mapping.get(k, k): v for k, v in d.items()}


class TransactionEventListener:
    def __init__(self, on_event_callback: Callable):
        self.on_event_callback = on_event_callback
        self.connection = None
        self.channel = None
        self.is_listening = False
        self._stop_event = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None

    async def start_listening(self, queue_name: str = "transaction_events") -> None:
        self._loop = asyncio.get_event_loop()
        self._stop_event.clear()
        await self._loop.run_in_executor(None, self._blocking_consume, queue_name)

    async def disconnect(self) -> None:
        self._stop_event.set()
        self.is_listening = False
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Internal — runs in thread executor
    # ------------------------------------------------------------------

    def _blocking_consume(self, queue_name: str) -> None:
        params = _parse_rabbitmq_url(settings.rabbitmq_url)
        credentials = pika.PlainCredentials(params["username"], params["password"])
        connection_params = pika.ConnectionParameters(
            host=params["host"],
            port=params["port"],
            virtual_host=params["virtual_host"],
            credentials=credentials,
            heartbeat=60,
            blocked_connection_timeout=300,
        )

        exchange_name = settings.rabbitmq_exchange
        routing_key = settings.rabbitmq_routing_key

        max_retries = 10
        retry_delay = 5

        for attempt in range(max_retries):
            if self._stop_event.is_set():
                return
            try:
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()
                # Declare the exchange (idempotent — safe if already exists)
                self.channel.exchange_declare(
                    exchange=exchange_name, exchange_type="topic", durable=True
                )
                # Declare this service's own dedicated queue
                self.channel.queue_declare(queue=queue_name, durable=True)
                # Bind this queue to the exchange so it receives a copy of every event
                self.channel.queue_bind(
                    queue=queue_name, exchange=exchange_name, routing_key=routing_key
                )
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=self._on_message,
                )
                self.is_listening = True
                logger.info(
                    "[Compliance] Listening on queue '%s' bound to exchange '%s' key '%s'",
                    queue_name, exchange_name, routing_key,
                )
                while not self._stop_event.is_set():
                    self.connection.process_data_events(time_limit=1)
                return
            except Exception as exc:
                logger.warning(
                    "[Compliance] RabbitMQ connect attempt %d/%d failed: %s",
                    attempt + 1, max_retries, exc,
                )
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
        logger.error("[Compliance] Could not connect to RabbitMQ after %d attempts", max_retries)

    def _on_message(self, ch, method, properties, body: bytes) -> None:
        try:
            raw = json.loads(body.decode("utf-8"))
            normalised = _camel_to_snake(raw)
            if self._loop and not self._loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(
                    self._handle_event(normalised), self._loop
                )
                future.result(timeout=30)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            logger.error("[Compliance] Error processing message: %s", exc, exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    async def _handle_event(self, event_data: dict) -> None:
        try:
            await self.on_event_callback(event_data)
        except Exception as exc:
            logger.error("[Compliance] Callback error: %s", exc, exc_info=True)
