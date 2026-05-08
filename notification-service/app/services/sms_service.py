import logging
import re

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications (Twilio stub for MVP)"""

    def __init__(self):
        # Placeholder for real Twilio credentials
        # self.twilio_account_sid = settings.twilio_account_sid
        # self.twilio_auth_token = settings.twilio_auth_token
        # self.twilio_from_number = settings.twilio_from_number
        self.is_mock = True  # MVP uses mock implementation

    async def send_sms(
        self,
        to_number: str,
        message_body: str
    ) -> bool:
        """
        Send SMS notification (mock implementation for MVP)

        Args:
            to_number: Recipient phone number
            message_body: SMS message content

        Returns:
            True if successful (or mocked successfully), False otherwise
        """
        try:
            # Validate phone number
            if not self.validate_phone_number(to_number):
                logger.error(f"Invalid phone number format: {to_number}")
                return False

            # Validate message length (SMS typically 160 chars)
            if len(message_body) > 160:
                logger.warning(f"Message exceeds 160 chars, will be split: {len(message_body)}")

            if self.is_mock:
                # MVP: Mock implementation (log and return success)
                logger.info(f"[MOCK SMS] To: {to_number}, Message: {message_body[:50]}...")
                return True
            else:
                # Real Twilio implementation (not used in MVP)
                # from twilio.rest import Client
                # client = Client(self.twilio_account_sid, self.twilio_auth_token)
                # message = client.messages.create(
                #     body=message_body,
                #     from_=self.twilio_from_number,
                #     to=to_number
                # )
                # logger.info(f"SMS sent with SID: {message.sid}")
                # return True
                pass

        except Exception as e:
            logger.error(f"Error sending SMS to {to_number}: {str(e)}")
            return False

    def validate_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format

        Args:
            phone: Phone number to validate

        Returns:
            True if valid format, False otherwise
        """
        # Accept formats: +1234567890, 1234567890, +1 (123) 456-7890, etc.
        # Reject malformed numbers like ++1234567890
        if phone.count('+') > 1:
            return False

        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

        # Should be 10-15 digits (international standard)
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15

    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number to E.164 format (+1234567890)

        Args:
            phone: Phone number in any format

        Returns:
            Formatted phone number
        """
        # Handle +1 prefix (US country code) - only remove if followed by space/formatting
        # This distinguishes between "+1 (" and "+1234567890"
        if phone.startswith('+1') and len(phone) > 2 and phone[2] in ' (-':
            phone = phone[2:]
        # Remove just leading + for other country codes
        elif phone.startswith('+'):
            phone = phone[1:]

        # Remove all non-digit characters
        cleaned = re.sub(r'[^\d]', '', phone)

        # Add + prefix (includes country code for US: 1)
        return '+' + cleaned
