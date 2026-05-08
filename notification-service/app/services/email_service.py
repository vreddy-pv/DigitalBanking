import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SMTP with retry logic"""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from

    async def send_email(
        self,
        to_address: str,
        subject: str,
        html_body: str,
        plain_body: str = None
    ) -> bool:
        """
        Send email via SMTP with error handling

        Args:
            to_address: Recipient email address
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text fallback (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_from
            message["To"] = to_address

            # Add plain text part (fallback)
            if plain_body:
                message.attach(MIMEText(plain_body, "plain"))

            # Add HTML part (preferred)
            message.attach(MIMEText(html_body, "html"))

            # Connect and send
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=True
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(f"Email sent successfully to {to_address}")
            return True

        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            return False

        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_address}: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_address}: {str(e)}")
            return False

    def validate_email(self, email: str) -> bool:
        """
        Basic email validation

        Args:
            email: Email address to validate

        Returns:
            True if valid format, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
