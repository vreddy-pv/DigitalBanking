import json
import logging
import asyncio
from typing import Callable
import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from app.config import settings
from app.schemas.transaction_event import TransactionCreatedEvent

logger = logging.getLogger(__name__)


class TransactionEventListener:
    """Listen for TransactionCreatedEvent from RabbitMQ and trigger notifications"""

    def __init__(self, on_event_callback: Callable):
        """
        Initialize event listener

        Args:
            on_event_callback: Async callback function to handle events
        """
        self.on_event_callback = on_event_callback
        self.connection = None
        self.channel = None
        self.is_listening = False

    async def connect(self) -> None:
        """Connect to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials("guest", "guest")
            parameters = pika.ConnectionParameters(
                host="localhost",  # Will be 'rabbitmq' in Docker
                port=5672,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )

            # Create async connection
            self.connection = await AsyncioConnection(parameters).open()
            self.channel = await self.connection.channel()

            logger.info("Connected to RabbitMQ")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    async def start_listening(self, queue_name: str = "transaction_events") -> None:
        """
        Start listening for transaction events

        Args:
            queue_name: RabbitMQ queue name
        """
        try:
            if not self.connection or not self.channel:
                await self.connect()

            # Declare queue
            await self.channel.queue_declare(queue=queue_name, durable=True)

            logger.info(f"Listening on queue: {queue_name}")

            # Set up consumer
            await self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message_callback,
                auto_ack=False,
            )

            self.is_listening = True
            logger.info("Transaction event listener started")

            # Keep consuming messages
            await self.channel.start_consuming()

        except Exception as e:
            logger.error(f"Error starting listener: {str(e)}")
            self.is_listening = False
            raise

    def _on_message_callback(self, channel, method, properties, body):
        """
        Handle incoming RabbitMQ message

        Args:
            channel: RabbitMQ channel
            method: Method frame
            properties: Message properties
            body: Message body (JSON)
        """
        try:
            # Parse event
            event_data = json.loads(body.decode("utf-8"))
            logger.info(f"Received transaction event: {event_data.get('transaction_id')}")

            # Convert to TransactionCreatedEvent schema
            event = TransactionCreatedEvent(**event_data)

            # Schedule async callback
            asyncio.create_task(self._handle_event(event, channel, method))

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse event JSON: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.error(f"Error processing transaction event: {str(e)}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def _handle_event(self, event: TransactionCreatedEvent, channel, method):
        """
        Handle transaction event asynchronously

        Args:
            event: Parsed transaction event
            channel: RabbitMQ channel
            method: Method frame (for acknowledgement)
        """
        try:
            # Call the registered callback
            await self.on_event_callback(event)

            # Acknowledge message after successful processing
            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Event processed successfully: {event.transaction_id}")

        except Exception as e:
            logger.error(f"Error handling event {event.transaction_id}: {str(e)}")
            # Reject and requeue on error
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    async def disconnect(self) -> None:
        """Disconnect from RabbitMQ"""
        try:
            if self.channel:
                await self.channel.stop_consuming()
                await self.channel.close()

            if self.connection:
                await self.connection.close()

            self.is_listening = False
            logger.info("Disconnected from RabbitMQ")

        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
