import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

import anthropic

from app.auth.jwt_validator import UserContext
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    text: str
    agent_used: str
    ticket_id: str | None = None


class BaseAgent:
    MAX_ITERATIONS = 6

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: list[dict],
        tool_handlers: dict[str, Callable[..., Coroutine[Any, Any, dict]]],
    ):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_handlers = tool_handlers
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, messages: list[dict], user_context: UserContext) -> AgentResponse:
        working = list(messages)
        last_ticket_id: str | None = None

        for iteration in range(self.MAX_ITERATIONS):
            response = await self._client.messages.create(
                model=settings.model,
                max_tokens=settings.max_tokens,
                system=self.system_prompt.format(
                    user_name=user_context.full_name,
                    user_id=user_context.user_id,
                    user_email=user_context.email,
                ),
                tools=self.tools,
                messages=working,
            )

            logger.debug("Agent %s iteration %d stop_reason=%s", self.agent_name, iteration, response.stop_reason)

            if response.stop_reason == "end_turn":
                return AgentResponse(
                    text=self._extract_text(response),
                    agent_used=self.agent_name,
                    ticket_id=last_ticket_id,
                )

            if response.stop_reason == "tool_use":
                tool_results, ticket_id = await self._execute_tools(response, user_context)
                if ticket_id:
                    last_ticket_id = ticket_id
                working.append({"role": "assistant", "content": response.content})
                working.append({"role": "user", "content": tool_results})
            else:
                logger.warning("Unexpected stop_reason: %s", response.stop_reason)
                break

        return AgentResponse(
            text="I'm sorry, I was unable to complete your request. Please try again or contact support.",
            agent_used=self.agent_name,
        )

    async def _execute_tools(
        self,
        response: anthropic.types.Message,
        user_context: UserContext,
    ) -> tuple[list[dict], str | None]:
        results: list[dict] = []
        ticket_id: str | None = None

        for block in response.content:
            if block.type != "tool_use":
                continue

            logger.info("Calling tool: %s args=%s", block.name, block.input)
            handler = self.tool_handlers.get(block.name)

            if handler:
                try:
                    result = await handler(user_context=user_context, **block.input)
                    if isinstance(result, dict) and "ticket_id" in result:
                        ticket_id = result["ticket_id"]
                    content = json.dumps(result)
                except Exception as exc:
                    logger.exception("Tool %s raised an exception", block.name)
                    content = json.dumps({"error": f"Tool failed: {str(exc)}"})
            else:
                content = json.dumps({"error": f"Unknown tool: {block.name}"})

            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": content}
            )

        return results, ticket_id

    @staticmethod
    def _extract_text(response: anthropic.types.Message) -> str:
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""
