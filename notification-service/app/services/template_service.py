from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging
import os

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for rendering email templates with Jinja2"""

    def __init__(self):
        # Load templates from app/templates directory
        template_dir = os.path.join(
            os.path.dirname(__file__),
            "..",
            "templates"
        )

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

    async def render_deposit_notification(
        self,
        customer_name: str,
        amount: float,
        account_number: str,
        transaction_id: str,
        timestamp: str
    ) -> tuple[str, str]:
        """
        Render deposit notification template

        Args:
            customer_name: Customer name
            amount: Deposit amount
            account_number: Account number
            transaction_id: Transaction ID
            timestamp: Transaction timestamp

        Returns:
            Tuple of (html_body, plain_text_body)
        """
        try:
            template = self.env.get_template("deposit_notification.html")
            html_body = template.render(
                customer_name=customer_name,
                amount=f"₹{amount:,.2f}",
                account_number=account_number,
                transaction_id=transaction_id,
                timestamp=timestamp
            )

            # Plain text version
            plain_text = f"""
Dear {customer_name},

Your deposit of ₹{amount:,.2f} has been received successfully.

Transaction ID: {transaction_id}
Date & Time: {timestamp}
Account: {account_number}

Thank you for using Digital Banking!

Best regards,
Digital Banking Team
            """.strip()

            return html_body, plain_text

        except TemplateNotFound:
            logger.error("Deposit notification template not found")
            raise
        except Exception as e:
            logger.error(f"Error rendering deposit template: {str(e)}")
            raise

    async def render_withdrawal_notification(
        self,
        customer_name: str,
        amount: float,
        account_number: str,
        transaction_id: str,
        timestamp: str
    ) -> tuple[str, str]:
        """
        Render withdrawal notification template

        Args:
            customer_name: Customer name
            amount: Withdrawal amount
            account_number: Account number
            transaction_id: Transaction ID
            timestamp: Transaction timestamp

        Returns:
            Tuple of (html_body, plain_text_body)
        """
        try:
            template = self.env.get_template("withdrawal_notification.html")
            html_body = template.render(
                customer_name=customer_name,
                amount=f"₹{amount:,.2f}",
                account_number=account_number,
                transaction_id=transaction_id,
                timestamp=timestamp
            )

            # Plain text version
            plain_text = f"""
Dear {customer_name},

Your withdrawal of ₹{amount:,.2f} has been processed successfully.

Transaction ID: {transaction_id}
Date & Time: {timestamp}
Account: {account_number}

Thank you for using Digital Banking!

Best regards,
Digital Banking Team
            """.strip()

            return html_body, plain_text

        except TemplateNotFound:
            logger.error("Withdrawal notification template not found")
            raise
        except Exception as e:
            logger.error(f"Error rendering withdrawal template: {str(e)}")
            raise

    async def render_transfer_notification(
        self,
        customer_name: str,
        amount: float,
        from_account: str,
        to_account: str,
        recipient_name: str,
        transaction_id: str,
        timestamp: str
    ) -> tuple[str, str]:
        """
        Render transfer notification template

        Args:
            customer_name: Sender name
            amount: Transfer amount
            from_account: Sender account number
            to_account: Recipient account number
            recipient_name: Recipient name
            transaction_id: Transaction ID
            timestamp: Transaction timestamp

        Returns:
            Tuple of (html_body, plain_text_body)
        """
        try:
            template = self.env.get_template("transfer_notification.html")
            html_body = template.render(
                customer_name=customer_name,
                amount=f"₹{amount:,.2f}",
                from_account=from_account,
                to_account=to_account,
                recipient_name=recipient_name,
                transaction_id=transaction_id,
                timestamp=timestamp
            )

            # Plain text version
            plain_text = f"""
Dear {customer_name},

Your transfer of ₹{amount:,.2f} to {recipient_name} has been completed successfully.

Transaction ID: {transaction_id}
Date & Time: {timestamp}
From Account: {from_account}
To Account: {to_account}

Thank you for using Digital Banking!

Best regards,
Digital Banking Team
            """.strip()

            return html_body, plain_text

        except TemplateNotFound:
            logger.error("Transfer notification template not found")
            raise
        except Exception as e:
            logger.error(f"Error rendering transfer template: {str(e)}")
            raise
