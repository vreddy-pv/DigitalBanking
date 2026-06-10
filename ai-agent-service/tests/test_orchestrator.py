import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.agents.orchestrator import Orchestrator
from app.agents.base_agent import AgentResponse


@pytest.fixture
def mock_agents():
    casa = AsyncMock()
    casa.run = AsyncMock(return_value=AgentResponse(text="Your balance is ₹45,230.", agent_used="CASA"))
    ml = AsyncMock()
    ml.run = AsyncMock(return_value=AgentResponse(text="Your EMI is ₹44,067.", agent_used="ML"))
    usl = AsyncMock()
    usl.run = AsyncMock(return_value=AgentResponse(text="Your personal loan balance is ₹3,20,000.", agent_used="USL"))
    return casa, ml, usl


@pytest.fixture
def orchestrator(mock_agents):
    casa, ml, usl = mock_agents
    return Orchestrator(casa=casa, ml=ml, usl=usl)


@pytest.mark.asyncio
@pytest.mark.parametrize("message,expected_agent", [
    ("What is my account balance?", "CASA"),
    ("Show me my recent transactions", "CASA"),
    ("What is my home loan EMI?", "ML"),
    ("When is my personal loan payment due?", "USL"),
])
async def test_route_calls_correct_agent(
    orchestrator, mock_agents, user_context, message, expected_agent
):
    casa, ml, usl = mock_agents
    agent_map = {"CASA": casa, "ML": ml, "USL": usl}

    with patch.object(orchestrator, "_classify", return_value=expected_agent):
        result = await orchestrator.route(message, [], user_context)

    agent_map[expected_agent].run.assert_awaited_once()
    assert result.agent_used == expected_agent


@pytest.mark.asyncio
async def test_general_intent_returns_orchestrator_response(
    orchestrator, user_context
):
    with patch.object(orchestrator, "_classify", return_value="GENERAL"):
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text="Hello! How can I help you today?")]
        orchestrator._client.messages.create = AsyncMock(return_value=mock_resp)

        result = await orchestrator.route("Hello!", [], user_context)

    assert result.agent_used == "ORCHESTRATOR"
    assert "Hello" in result.text


@pytest.mark.asyncio
async def test_route_passes_history_to_agent(orchestrator, mock_agents, user_context):
    casa, _, _ = mock_agents
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello Arjun!"},
    ]
    with patch.object(orchestrator, "_classify", return_value="CASA"):
        await orchestrator.route("What is my balance?", history, user_context)

    call_args = casa.run.call_args
    messages_passed = call_args[0][0]
    assert len(messages_passed) == 3  # 2 history + 1 new user message
    assert messages_passed[-1]["content"] == "What is my balance?"


@pytest.mark.asyncio
async def test_classify_unknown_label_falls_back_to_general(orchestrator, user_context):
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="UNKNOWN")]
    orchestrator._client.messages.create = AsyncMock(return_value=mock_resp)

    label = await orchestrator._classify("some random message", [])
    assert label == "GENERAL"
