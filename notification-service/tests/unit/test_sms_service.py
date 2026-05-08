import pytest
from app.services.sms_service import SMSService


@pytest.fixture
def sms_service():
    """Fixture for SMSService"""
    return SMSService()


class TestSMSService:
    """Test suite for SMSService"""

    @pytest.mark.asyncio
    async def test_send_sms_valid_phone(self, sms_service):
        """Test sending SMS with valid phone number"""
        result = await sms_service.send_sms(
            to_number="+1234567890",
            message_body="Test message"
        )

        # Mock implementation should return True
        assert result is True

    @pytest.mark.asyncio
    async def test_send_sms_invalid_phone(self, sms_service):
        """Test sending SMS with invalid phone number"""
        result = await sms_service.send_sms(
            to_number="invalid-number",
            message_body="Test message"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_send_sms_various_phone_formats(self, sms_service):
        """Test sending SMS with various phone formats"""
        valid_phones = [
            "+1234567890",
            "1234567890",
            "+1 (123) 456-7890",
            "123-456-7890",
            "+91 9876543210"
        ]

        for phone in valid_phones:
            result = await sms_service.send_sms(
                to_number=phone,
                message_body="Test message"
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_send_sms_long_message(self, sms_service):
        """Test sending SMS with long message (exceeds 160 chars)"""
        long_message = "a" * 200  # 200 characters

        result = await sms_service.send_sms(
            to_number="+1234567890",
            message_body=long_message
        )

        # Should still succeed (warning logged)
        assert result is True

    def test_validate_phone_number_valid(self, sms_service):
        """Test phone number validation with valid numbers"""
        valid_numbers = [
            "1234567890",
            "+1234567890",
            "(123) 456-7890",
            "123-456-7890",
            "+1 (123) 456-7890",
            "9876543210",
            "+919876543210"
        ]

        for phone in valid_numbers:
            assert sms_service.validate_phone_number(phone) is True

    def test_validate_phone_number_invalid(self, sms_service):
        """Test phone number validation with invalid numbers"""
        invalid_numbers = [
            "123",  # Too short
            "a1234567890",  # Contains letters
            "abc",  # All letters
            "",  # Empty
            "++1234567890",  # Double +
            "1234567"  # Too short (7 digits)
        ]

        for phone in invalid_numbers:
            assert sms_service.validate_phone_number(phone) is False

    def test_format_phone_number(self, sms_service):
        """Test phone number formatting to E.164"""
        test_cases = [
            ("1234567890", "+1234567890"),
            ("+1234567890", "+1234567890"),
            ("(123) 456-7890", "+1234567890"),
            ("123-456-7890", "+1234567890"),
            ("+1 (123) 456-7890", "+1234567890"),
        ]

        for input_phone, expected_output in test_cases:
            result = sms_service.format_phone_number(input_phone)
            assert result == expected_output

    @pytest.mark.asyncio
    async def test_send_sms_empty_message(self, sms_service):
        """Test sending SMS with empty message"""
        result = await sms_service.send_sms(
            to_number="+1234567890",
            message_body=""
        )

        # Should still succeed (no validation on message content)
        assert result is True

    def test_validate_phone_number_edge_cases(self, sms_service):
        """Test phone number validation edge cases"""
        # Exactly 10 digits (minimum)
        assert sms_service.validate_phone_number("1234567890") is True

        # Exactly 15 digits (maximum)
        assert sms_service.validate_phone_number("123456789012345") is True

        # 9 digits (below minimum)
        assert sms_service.validate_phone_number("123456789") is False

        # 16 digits (above maximum)
        assert sms_service.validate_phone_number("1234567890123456") is False

    @pytest.mark.asyncio
    async def test_send_sms_international_numbers(self, sms_service):
        """Test sending SMS to international phone numbers"""
        international_numbers = [
            "+441234567890",  # UK
            "+33123456789",   # France
            "+919876543210",  # India
            "+861234567890"   # China
        ]

        for phone in international_numbers:
            result = await sms_service.send_sms(
                to_number=phone,
                message_body="Test message"
            )
            assert result is True
