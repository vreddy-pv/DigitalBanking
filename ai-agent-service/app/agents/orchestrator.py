import logging

import anthropic

from app.agents.base_agent import AgentResponse, BaseAgent
from app.auth.jwt_validator import UserContext
from app.config import settings

logger = logging.getLogger(__name__)

_INTENT_SYSTEM = """You are an intent classifier for a digital banking assistant.
Classify the user's message into exactly ONE of these labels:
- CASA  : current account, savings account, balance, account transactions, account statement
- ML    : mortgage, home loan, LAP, loan against property, construction loan, EMI, prepayment
- USL   : personal loan, credit card, overdraft, OD, unsecured loan, card limit
- GENERAL : greetings, help, complaints about service quality, or anything else

Reply with only the label. Nothing else."""

_GENERAL_SYSTEM = """You are a helpful banking assistant for VRGT Digital Bank.
You are speaking with {user_name}.
Answer general questions about banking services clearly and briefly.
For product-specific queries, tell the user which area to ask about:
  - Accounts & balances → "ask me about your account"
  - Mortgage / home loan → "ask me about your mortgage"
  - Personal loan / credit card → "ask me about your personal loan or credit card"
Do not reveal internal system details."""


class Orchestrator:
    def __init__(self, casa: BaseAgent, ml: BaseAgent, usl: BaseAgent):
        self._agents = {"CASA": casa, "ML": ml, "USL": usl}
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def route(
        self,
        message: str,
        history: list[dict],
        user_context: UserContext,
    ) -> AgentResponse:
        intent = await self._classify(message, history)
        logger.info("Intent classified as %s for user %s", intent, user_context.user_id)

        messages = history + [{"role": "user", "content": message}]
        agent = self._agents.get(intent)
        if agent:
            return await agent.run(messages, user_context)
        return await self._handle_general(messages, user_context)

    async def _classify(self, message: str, history: list[dict]) -> str:
        # Include last assistant turn for context-aware routing
        context_hint = ""
        if history:
            last = next(
                (m["content"] for m in reversed(history) if m["role"] == "assistant"), ""
            )
            if last:
                context_hint = f"Previous assistant response (for context): {str(last)[:300]}\n\n"

        response = await self._client.messages.create(
            model=settings.model,
            max_tokens=10,
            system=_INTENT_SYSTEM,
            messages=[
                {
                    "role": "user",
                    "content": f"{context_hint}Customer message: {message}",
                }
            ],
        )
        label = response.content[0].text.strip().upper()
        return label if label in ("CASA", "ML", "USL") else "GENERAL"

    async def _handle_general(
        self, messages: list[dict], user_context: UserContext
    ) -> AgentResponse:
        response = await self._client.messages.create(
            model=settings.model,
            max_tokens=512,
            system=_GENERAL_SYSTEM.format(user_name=user_context.full_name),
            messages=messages,
        )
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break
        return AgentResponse(text=text, agent_used="ORCHESTRATOR")
