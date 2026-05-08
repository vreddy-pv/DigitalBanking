import logging
from uuid import UUID
from sqlalchemy.orm import Session
from app.schemas.transaction_event import TransactionCreatedEvent
from app.services.notification_service import NotificationService
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class TransactionEventConsumer:
    """Consume TransactionCreatedEvent and create notifications"""

    def __init__(self):
        """Initialize consumer with notification service"""
        self.notification_service = NotificationService()

    async def handle_transaction_created(self, event: TransactionCreatedEvent) -> None:
        """
        Handle TransactionCreatedEvent by creating notifications

        Args:
            event: TransactionCreatedEvent from RabbitMQ
        """
        db: Session = SessionLocal()

        try:
            logger.info(
                f"Processing transaction event: {event.transaction_id} "
                f"({event.transaction_type})"
            )

            # Handle different transaction types
            if event.transaction_type == "DEPOSIT":
                await self._handle_deposit(db, event)

            elif event.transaction_type == "WITHDRAWAL":
                await self._handle_withdrawal(db, event)

            elif event.transaction_type == "TRANSFER":
                await self._handle_transfer(db, event)

            else:
                logger.error(f"Unknown transaction type: {event.transaction_type}")

        except Exception as e:
            logger.error(
                f"Error processing transaction {event.transaction_id}: {str(e)}"
            )
            raise

        finally:
            db.close()

    async def _handle_deposit(self, db: Session, event: TransactionCreatedEvent) -> None:
        """
        Handle deposit transaction - notify recipient

        Args:
            db: Database session
            event: Transaction event
        """
        try:
            notification = await self.notification_service.handle_transaction_event(
                db=db,
                transaction_id=event.transaction_id,
                transaction_type="DEPOSIT",
                amount=event.amount,
                from_account_id=None,
                to_account_id=event.to_account_id,
                description=event.description,
                recipient_email=event.recipient_email,
                customer_name=event.customer_name,
                account_number=event.account_number,
                timestamp=event.timestamp,
            )

            logger.info(f"Deposit notification created: {notification.id}")

        except Exception as e:
            logger.error(f"Error handling deposit notification: {str(e)}")
            raise

    async def _handle_withdrawal(
        self, db: Session, event: TransactionCreatedEvent
    ) -> None:
        """
        Handle withdrawal transaction - notify account holder

        Args:
            db: Database session
            event: Transaction event
        """
        try:
            notification = await self.notification_service.handle_transaction_event(
                db=db,
                transaction_id=event.transaction_id,
                transaction_type="WITHDRAWAL",
                amount=event.amount,
                from_account_id=event.from_account_id,
                to_account_id=None,
                description=event.description,
                recipient_email=event.recipient_email,
                customer_name=event.customer_name,
                account_number=event.account_number,
                timestamp=event.timestamp,
            )

            logger.info(f"Withdrawal notification created: {notification.id}")

        except Exception as e:
            logger.error(f"Error handling withdrawal notification: {str(e)}")
            raise

    async def _handle_transfer(
        self, db: Session, event: TransactionCreatedEvent
    ) -> None:
        """
        Handle transfer transaction - notify both sender and recipient

        Args:
            db: Database session
            event: Transaction event
        """
        try:
            # Notify sender (from account)
            sender_notification = (
                await self.notification_service.handle_transaction_event(
                    db=db,
                    transaction_id=event.transaction_id,
                    transaction_type="TRANSFER",
                    amount=event.amount,
                    from_account_id=event.from_account_id,
                    to_account_id=event.to_account_id,
                    description=event.description,
                    recipient_email=event.recipient_email,  # Sender's email
                    customer_name=event.customer_name,
                    account_number=event.account_number,  # Sender's account
                    timestamp=event.timestamp,
                )
            )

            logger.info(f"Transfer notification (sender) created: {sender_notification.id}")

            # Notify recipient (to account) - TODO: Get recipient email from Account Service
            # For MVP, we're only notifying the sender
            # In Phase 2, we'll call Account Service to get recipient details

        except Exception as e:
            logger.error(f"Error handling transfer notification: {str(e)}")
            raise
