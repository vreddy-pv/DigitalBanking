import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.template_service import TemplateService
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Custom exception for notification service errors"""
    pass


class NotificationService:
    """Main service for notification creation and delivery"""

    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.template_service = TemplateService()

    async def create_notification(
        self,
        db: Session,
        transaction_id: UUID,
        notification_type: str,
        recipient: str,
        subject: str,
        body: str
    ) -> Notification:
        """
        Create a notification record in database

        Args:
            db: Database session
            transaction_id: Transaction ID
            notification_type: EMAIL or SMS
            recipient: Email or phone number
            subject: Notification subject
            body: Notification body

        Returns:
            Created Notification object
        """
        try:
            notification = Notification(
                transaction_id=transaction_id,
                notification_type=notification_type,
                recipient=recipient,
                subject=subject,
                body=body,
                status="PENDING",
                attempts=0,
                max_attempts=settings.max_retry_attempts
            )

            db.add(notification)
            db.commit()
            db.refresh(notification)

            logger.info(f"Notification created: {notification.id} for transaction {transaction_id}")
            return notification

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise NotificationServiceError(f"Failed to create notification: {str(e)}")

    async def send_notification(
        self,
        db: Session,
        notification_id: UUID
    ) -> bool:
        """
        Send a notification and update status

        Args:
            db: Database session
            notification_id: Notification ID to send

        Returns:
            True if successful, False otherwise
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                logger.error(f"Notification not found: {notification_id}")
                return False

            # Check max attempts
            if notification.attempts >= notification.max_attempts:
                notification.status = "FAILED"
                notification.error_message = "Max retry attempts exceeded"
                db.commit()
                logger.error(f"Max attempts exceeded for notification {notification_id}")
                return False

            success = False

            # Send based on notification type
            if notification.notification_type == "EMAIL":
                success = await self.email_service.send_email(
                    to_address=notification.recipient,
                    subject=notification.subject,
                    html_body=notification.body
                )

            elif notification.notification_type == "SMS":
                success = await self.sms_service.send_sms(
                    to_number=notification.recipient,
                    message_body=notification.body
                )

            else:
                logger.error(f"Unknown notification type: {notification.notification_type}")
                return False

            # Update notification status
            notification.attempts += 1

            if success:
                notification.status = "SENT"
                notification.sent_at = datetime.now(timezone.utc)
                logger.info(f"Notification sent successfully: {notification_id}")

            else:
                # Failed delivery
                if notification.attempts >= notification.max_attempts:
                    notification.status = "FAILED"
                    logger.error(f"Notification delivery failed after {notification.attempts} attempts: {notification_id}")
                else:
                    notification.status = "PENDING"
                    logger.warning(f"Notification delivery attempt {notification.attempts} failed: {notification_id}")

            db.commit()
            return success

        except Exception as e:
            db.rollback()
            logger.error(f"Error sending notification {notification_id}: {str(e)}")
            return False

    async def handle_transaction_event(
        self,
        db: Session,
        transaction_id: UUID,
        transaction_type: str,
        amount: float,
        from_account_id: str,
        to_account_id: str,
        description: str,
        recipient_email: str,
        customer_name: str,
        account_number: str,
        timestamp: str
    ) -> Notification:
        """
        Handle transaction event and create notification

        Args:
            db: Database session
            transaction_id: Transaction ID
            transaction_type: DEPOSIT, WITHDRAWAL, TRANSFER
            amount: Transaction amount
            from_account_id: Sender account ID
            to_account_id: Recipient account ID
            description: Transaction description
            recipient_email: Recipient email address
            customer_name: Customer name
            account_number: Account number
            timestamp: Transaction timestamp

        Returns:
            Created Notification object
        """
        try:
            # Prepare notification content based on transaction type
            if transaction_type == "DEPOSIT":
                subject = "Deposit Received"
                html_body, plain_body = await self.template_service.render_deposit_notification(
                    customer_name=customer_name,
                    amount=amount,
                    account_number=account_number,
                    transaction_id=str(transaction_id),
                    timestamp=timestamp
                )

            elif transaction_type == "WITHDRAWAL":
                subject = "Withdrawal Processed"
                html_body, plain_body = await self.template_service.render_withdrawal_notification(
                    customer_name=customer_name,
                    amount=amount,
                    account_number=account_number,
                    transaction_id=str(transaction_id),
                    timestamp=timestamp
                )

            elif transaction_type == "TRANSFER":
                subject = "Transfer Completed"
                # For transfer, we'd need recipient name from Account Service
                recipient_name = "Recipient"  # TODO: Fetch from Account Service
                html_body, plain_body = await self.template_service.render_transfer_notification(
                    customer_name=customer_name,
                    amount=amount,
                    from_account=from_account_id or "N/A",
                    to_account=to_account_id or "N/A",
                    recipient_name=recipient_name,
                    transaction_id=str(transaction_id),
                    timestamp=timestamp
                )

            else:
                logger.error(f"Unknown transaction type: {transaction_type}")
                raise NotificationServiceError(f"Unknown transaction type: {transaction_type}")

            # Create notification
            notification = await self.create_notification(
                db=db,
                transaction_id=transaction_id,
                notification_type="EMAIL",
                recipient=recipient_email,
                subject=subject,
                body=html_body
            )

            # Send notification immediately (synchronous for MVP, async in production)
            await self.send_notification(db, notification.id)

            return notification

        except Exception as e:
            logger.error(f"Error handling transaction event: {str(e)}")
            raise

    async def retry_notification(
        self,
        db: Session,
        notification_id: UUID
    ) -> bool:
        """
        Retry sending a failed notification

        Args:
            db: Database session
            notification_id: Notification ID to retry

        Returns:
            True if successful, False otherwise
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                logger.error(f"Notification not found: {notification_id}")
                return False

            if notification.status == "SENT":
                logger.warning(f"Cannot retry already sent notification: {notification_id}")
                return False

            # Reset attempts for retry
            notification.attempts = 0
            notification.status = "PENDING"
            notification.error_message = None
            db.commit()

            logger.info(f"Notification reset for retry: {notification_id}")

            # Send again
            return await self.send_notification(db, notification_id)

        except Exception as e:
            db.rollback()
            logger.error(f"Error retrying notification {notification_id}: {str(e)}")
            return False
