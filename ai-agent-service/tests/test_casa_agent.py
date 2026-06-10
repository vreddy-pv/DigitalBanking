import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.base_agent import BaseAgent
from app.agents import casa_agent
from app.tools.complaint_tools import raise_complaint, get_complaint_status


@pytest.fixture
def casa():
    return casa_agent.build()


# ── BaseAgent agentic loop ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_agent_returns_text_on_end_turn(casa, user_context, mock_anthropic_response):
    response = mock_anthropic_response("Your savings account balance is ₹45,230.")
    casa._client.messages.create = AsyncMock(return_value=response)

    result = await casa.run([{"role": "user", "content": "What is my balance?"}], user_context)

    assert result.text == "Your savings account balance is ₹45,230."
    assert result.agent_used == "CASA"


@pytest.mark.asyncio
async def test_agent_executes_tool_then_returns_text(casa, user_context):
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool-123"
    tool_use_block.name = "get_customer_accounts"
    tool_use_block.input = {}

    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [tool_use_block]

    text_block = MagicMock()
    text_block.type = "end_turn"
    text_block.text = "You have 1 savings account with a balance of ₹45,230."

    final_response = MagicMock()
    final_response.stop_reason = "end_turn"
    final_response.content = [text_block]

    mock_tool_handler = AsyncMock(return_value={"accounts": [{"accountNumber": "ACC-001", "balance": 45230}]})

    with patch.dict(casa.tool_handlers, {"get_customer_accounts": mock_tool_handler}):
        casa._client.messages.create = AsyncMock(side_effect=[tool_response, final_response])
        result = await casa.run([{"role": "user", "content": "Show me my accounts"}], user_context)

    mock_tool_handler.assert_awaited_once()
    assert "45,230" in result.text


@pytest.mark.asyncio
async def test_agent_handles_tool_exception_gracefully(casa, user_context):
    tool_use_block = MagicMock()
    tool_use_block.type = "tool_use"
    tool_use_block.id = "tool-456"
    tool_use_block.name = "get_customer_accounts"
    tool_use_block.input = {}

    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [tool_use_block]

    text_block = MagicMock()
    text_block.text = "I'm sorry, I couldn't retrieve your accounts right now."

    final_response = MagicMock()
    final_response.stop_reason = "end_turn"
    final_response.content = [text_block]

    failing_handler = AsyncMock(side_effect=Exception("connection timeout"))

    with patch.dict(casa.tool_handlers, {"get_customer_accounts": failing_handler}):
        casa._client.messages.create = AsyncMock(side_effect=[tool_response, final_response])
        result = await casa.run([{"role": "user", "content": "Show accounts"}], user_context)

    # Agent should still return a response (not raise)
    assert result.text is not None


# ── Complaint tools ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_raise_complaint_returns_ticket_id(user_context):
    result = await raise_complaint(
        user_context=user_context,
        transaction_id="txn-uuid-001",
        account_id="acc-uuid-001",
        complaint_type="UNAUTHORIZED",
        description="I did not make this ₹2,500 transaction at XYZ Store.",
        product_line="CASA",
    )
    assert "ticket_id" in result
    assert result["ticket_id"].startswith("CMP-")
    assert result["status"] == "ACCEPTED"


@pytest.mark.asyncio
async def test_get_complaint_status_returns_accepted(user_context):
    # First raise a complaint
    created = await raise_complaint(
        user_context=user_context,
        transaction_id="txn-uuid-002",
        account_id="acc-uuid-001",
        complaint_type="DISPUTE",
        description="Wrong amount charged.",
        product_line="CASA",
    )
    ticket_id = created["ticket_id"]

    # Then check status
    status = await get_complaint_status(user_context=user_context, ticket_id=ticket_id)
    assert status["ticket_id"] == ticket_id
    assert status["status"] == "ACCEPTED"


@pytest.mark.asyncio
async def test_get_complaint_status_unknown_ticket(user_context):
    result = await get_complaint_status(user_context=user_context, ticket_id="CMP-NONEXISTENT")
    assert "error" in result


@pytest.mark.asyncio
async def test_complaint_unauthorised_access(user_context):
    other_user = MagicMock()
    other_user.user_id = "different-user-999"

    # Raise complaint as user_context
    created = await raise_complaint(
        user_context=user_context,
        transaction_id="txn-uuid-003",
        account_id="acc-uuid-001",
        complaint_type="FRAUD",
        description="Suspicious transaction.",
        product_line="CASA",
    )

    # Try to access as a different user
    result = await get_complaint_status(user_context=other_user, ticket_id=created["ticket_id"])
    assert "error" in result
    assert "authorised" in result["error"].lower()
