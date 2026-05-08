import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.email_service import EmailService


@pytest.fixture
def email_service():
    """Fixture for EmailService"""
    return EmailService()


class TestEmailService:
    """Test suite for EmailService"""

    @pytest.mark.asyncio
    async def test_send_email_success(self, email_service):
        """Test successful email sending"""
        with patch("app.services.email_service.aiosmtplib.SMTP") as mock_smtp_class:
            # Setup mock instance
            mock_instance = AsyncMock()
            mock_smtp_class.return_value.__aenter__.return_value = mock_instance
            mock_smtp_class.return_value.__aexit__.return_value = None

            # Call send_email
            result = await email_service.send_email(
                to_address="test@example.com",
                subject="Test Subject",
                html_body="<h1>Test</h1>",
                plain_body="Test"
            )

            # Assertions
            assert result is True
            mock_instance.login.assert_called_once()
            mock_instance.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_invalid_recipient(self, email_service):
        """Test sending email to invalid recipient"""
        result = await email_service.send_email(
            to_address="invalid-email",
            subject="Test Subject",
            html_body="<h1>Test</h1>"
        )

        # Should handle error gracefully
        assert result is False

    @pytest.mark.asyncio
    async def test_send_email_authentication_error(self, email_service):
        """Test email sending with authentication error"""
        with patch("app.services.email_service.aiosmtplib.SMTP") as mock_smtp_class:
            # Setup mock to raise authentication error
            mock_instance = AsyncMock()
            mock_instance.login.side_effect = Exception("Auth failed")
            mock_smtp_class.return_value.__aenter__.return_value = mock_instance
            mock_smtp_class.return_value.__aexit__.return_value = None

            result = await email_service.send_email(
                to_address="test@example.com",
                subject="Test",
                html_body="Test"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_send_email_with_plain_text(self, email_service):
        """Test sending email with both HTML and plain text"""
        with patch("app.services.email_service.aiosmtplib.SMTP") as mock_smtp_class:
            mock_instance = AsyncMock()
            mock_smtp_class.return_value.__aenter__.return_value = mock_instance
            mock_smtp_class.return_value.__aexit__.return_value = None

            result = await email_service.send_email(
                to_address="test@example.com",
                subject="Test",
                html_body="<h1>Test</h1>",
                plain_body="Test Plain"
            )

            assert result is True

    def test_validate_email_valid(self, email_service):
        """Test email validation with valid email"""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test.email+tag@domain.com",
            "user123@sub.domain.com"
        ]

        for email in valid_emails:
            assert email_service.validate_email(email) is True

    def test_validate_email_invalid(self, email_service):
        """Test email validation with invalid email"""
        invalid_emails = [
            "invalid-email",
            "user@",
            "@example.com",
            "user @example.com",
            "user@example",
            ""
        ]

        for email in invalid_emails:
            assert email_service.validate_email(email) is False

    @pytest.mark.asyncio
    async def test_send_email_without_plain_text(self, email_service):
        """Test sending email with only HTML body"""
        with patch("app.services.email_service.aiosmtplib.SMTP") as mock_smtp_class:
            mock_instance = AsyncMock()
            mock_smtp_class.return_value.__aenter__.return_value = mock_instance
            mock_smtp_class.return_value.__aexit__.return_value = None

            result = await email_service.send_email(
                to_address="test@example.com",
                subject="Test",
                html_body="<h1>Test</h1>"
            )

            assert result is True
            # Verify send_message was called
            mock_instance.send_message.assert_called_once()
