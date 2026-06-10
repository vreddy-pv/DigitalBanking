import pytest
from unittest.mock import AsyncMock, MagicMock

from app.auth.jwt_validator import UserContext


@pytest.fixture
def user_context():
    return UserContext(
        user_id="test-user-123",
        email="test@vrgtbank.com",
        full_name="Arjun Sharma",
        roles=["CUSTOMER"],
    )


@pytest.fixture
def sample_account():
    return {
        "accountId": "acc-uuid-001",
        "accountNumber": "ACC-00001234",
        "accountType": "SAVINGS",
        "balance": 45230.00,
        "availableBalance": 45230.00,
        "currency": "INR",
        "status": "ACTIVE",
    }


@pytest.fixture
def sample_transaction():
    return {
        "id": "txn-uuid-001",
        "type": "WITHDRAWAL",
        "amount": 2500.00,
        "currency": "INR",
        "status": "COMPLETED",
        "description": "POS purchase at XYZ Store",
        "fromAccountId": "acc-uuid-001",
        "toAccountId": None,
        "createdAt": "2026-06-08T14:22:00Z",
        "updatedAt": "2026-06-08T14:22:05Z",
    }


@pytest.fixture
def mock_anthropic_response():
    def _make(text: str):
        block = MagicMock()
        block.type = "end_turn"
        block.text = text
        response = MagicMock()
        response.stop_reason = "end_turn"
        response.content = [block]
        return response
    return _make
