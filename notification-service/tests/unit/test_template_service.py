import pytest
from app.services.template_service import TemplateService


@pytest.fixture
def template_service():
    return TemplateService()


SAMPLE_CUSTOMER = "Jane Doe"
SAMPLE_AMOUNT = 5000.00
SAMPLE_ACCOUNT = "ACC-001234"
SAMPLE_TX_ID = "TXN-20260509-001"
SAMPLE_TIMESTAMP = "2026-05-09T10:00:00Z"
SAMPLE_RECIPIENT = "John Smith"
SAMPLE_TO_ACCOUNT = "ACC-009876"


class TestTemplateService:
    """Tests for TemplateService rendering methods."""

    @pytest.mark.asyncio
    async def test_render_deposit_notification(self, template_service):
        """Rendered output contains customer_name, amount, and transaction_id."""
        html_body, plain_body = await template_service.render_deposit_notification(
            customer_name=SAMPLE_CUSTOMER,
            amount=SAMPLE_AMOUNT,
            account_number=SAMPLE_ACCOUNT,
            transaction_id=SAMPLE_TX_ID,
            timestamp=SAMPLE_TIMESTAMP,
        )

        assert SAMPLE_CUSTOMER in html_body
        assert SAMPLE_TX_ID in html_body
        assert SAMPLE_ACCOUNT in html_body

        assert SAMPLE_CUSTOMER in plain_body
        assert SAMPLE_TX_ID in plain_body
        assert "5,000.00" in plain_body

    @pytest.mark.asyncio
    async def test_render_withdrawal_notification(self, template_service):
        """Rendered output contains customer_name and transaction_id."""
        html_body, plain_body = await template_service.render_withdrawal_notification(
            customer_name=SAMPLE_CUSTOMER,
            amount=SAMPLE_AMOUNT,
            account_number=SAMPLE_ACCOUNT,
            transaction_id=SAMPLE_TX_ID,
            timestamp=SAMPLE_TIMESTAMP,
        )

        assert SAMPLE_CUSTOMER in html_body
        assert SAMPLE_TX_ID in html_body

        assert SAMPLE_CUSTOMER in plain_body
        assert SAMPLE_TX_ID in plain_body
        # Withdrawal plain text mentions "withdrawal"
        assert "withdrawal" in plain_body.lower()

    @pytest.mark.asyncio
    async def test_render_transfer_notification(self, template_service):
        """Rendered output contains customer_name, recipient_name, and transaction_id."""
        html_body, plain_body = await template_service.render_transfer_notification(
            customer_name=SAMPLE_CUSTOMER,
            amount=SAMPLE_AMOUNT,
            from_account=SAMPLE_ACCOUNT,
            to_account=SAMPLE_TO_ACCOUNT,
            recipient_name=SAMPLE_RECIPIENT,
            transaction_id=SAMPLE_TX_ID,
            timestamp=SAMPLE_TIMESTAMP,
        )

        assert SAMPLE_CUSTOMER in html_body
        assert SAMPLE_TX_ID in html_body
        assert SAMPLE_RECIPIENT in html_body

        assert SAMPLE_CUSTOMER in plain_body
        assert SAMPLE_TX_ID in plain_body
        assert SAMPLE_RECIPIENT in plain_body
        assert "transfer" in plain_body.lower()

    @pytest.mark.asyncio
    async def test_all_templates_return_tuple(self, template_service):
        """Each render method returns a (html_body, plain_body) tuple of two strings."""
        deposit_result = await template_service.render_deposit_notification(
            customer_name="A", amount=100.0, account_number="X",
            transaction_id="T1", timestamp="2026-01-01",
        )
        withdrawal_result = await template_service.render_withdrawal_notification(
            customer_name="A", amount=100.0, account_number="X",
            transaction_id="T2", timestamp="2026-01-01",
        )
        transfer_result = await template_service.render_transfer_notification(
            customer_name="A", amount=100.0, from_account="X",
            to_account="Y", recipient_name="B",
            transaction_id="T3", timestamp="2026-01-01",
        )

        for result in [deposit_result, withdrawal_result, transfer_result]:
            assert isinstance(result, tuple)
            assert len(result) == 2
            html_body, plain_body = result
            assert isinstance(html_body, str)
            assert isinstance(plain_body, str)
            assert len(html_body) > 0
            assert len(plain_body) > 0

    @pytest.mark.asyncio
    async def test_html_templates_are_valid_html(self, template_service):
        """HTML bodies start with a valid HTML marker."""
        deposit_html, _ = await template_service.render_deposit_notification(
            customer_name="A", amount=100.0, account_number="X",
            transaction_id="T1", timestamp="2026-01-01",
        )
        withdrawal_html, _ = await template_service.render_withdrawal_notification(
            customer_name="A", amount=100.0, account_number="X",
            transaction_id="T2", timestamp="2026-01-01",
        )
        transfer_html, _ = await template_service.render_transfer_notification(
            customer_name="A", amount=100.0, from_account="X",
            to_account="Y", recipient_name="B",
            transaction_id="T3", timestamp="2026-01-01",
        )

        valid_starters = ("<!DOCTYPE", "<html", "<div")
        for html in [deposit_html, withdrawal_html, transfer_html]:
            stripped = html.strip()
            assert any(
                stripped.startswith(s) for s in valid_starters
            ), f"HTML body does not start with a valid HTML tag: {stripped[:60]!r}"
