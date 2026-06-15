import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

import anthropic

from app.auth.jwt_validator import UserContext
from app.config import settings
from app.observability import observability

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
        last_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )

        # ── Observability: open agent span + start timer ──────────────────────
        start_ts = time.monotonic()
        agent_span = observability.start_agent_span(self.agent_name, str(last_user_msg))

        try:
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

                logger.debug(
                    "Agent %s iter=%d stop=%s in_tok=%d out_tok=%d",
                    self.agent_name,
                    iteration,
                    response.stop_reason,
                    response.usage.input_tokens,
                    response.usage.output_tokens,
                )

                # ── Record LLM generation in LangFuse + Prometheus ────────────
                response_text = self._extract_text(response)
                observability.record_llm_generation(
                    parent=agent_span,
                    agent_name=self.agent_name,
                    model=settings.model,
                    messages=working,
                    response_text=response_text,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    iteration=iteration,
                )

                if response.stop_reason == "end_turn":
                    elapsed = time.monotonic() - start_ts
                    observability.finish_agent_span(agent_span, response_text)
                    if observability.metrics.enabled:
                        observability.metrics.agent_invocations.labels(
                            self.agent_name, "success"
                        ).inc()
                        observability.metrics.agent_latency.labels(self.agent_name).observe(
                            elapsed
                        )
                    return AgentResponse(
                        text=response_text,
                        agent_used=self.agent_name,
                        ticket_id=last_ticket_id,
                    )

                if response.stop_reason == "tool_use":
                    tool_results, ticket_id = await self._execute_tools(
                        response, user_context, agent_span
                    )
                    if ticket_id:
                        last_ticket_id = ticket_id
                    working.append({"role": "assistant", "content": response.content})
                    working.append({"role": "user", "content": tool_results})
                else:
                    logger.warning("Unexpected stop_reason: %s", response.stop_reason)
                    break

        except Exception:
            if observability.metrics.enabled:
                observability.metrics.agent_invocations.labels(
                    self.agent_name, "error"
                ).inc()
            observability.finish_agent_span(agent_span, "exception during agent run")
            raise

        # Max iterations exhausted
        if observability.metrics.enabled:
            observability.metrics.agent_invocations.labels(self.agent_name, "error").inc()
        observability.finish_agent_span(agent_span, "max iterations reached")
        return AgentResponse(
            text="I'm sorry, I was unable to complete your request. Please try again or contact support.",
            agent_used=self.agent_name,
        )

    async def _execute_tools(
        self,
        response: anthropic.types.Message,
        user_context: UserContext,
        agent_span: Any = None,
    ) -> tuple[list[dict], str | None]:
        results: list[dict] = []
        ticket_id: str | None = None

        for block in response.content:
            if block.type != "tool_use":
                continue

            logger.info("Tool call: %s args=%s", block.name, block.input)
            handler = self.tool_handlers.get(block.name)

            if handler:
                try:
                    result = await handler(user_context=user_context, **block.input)
                    if isinstance(result, dict) and "ticket_id" in result:
                        ticket_id = result["ticket_id"]
                    content = json.dumps(result)
                    success = "error" not in result if isinstance(result, dict) else True
                except Exception as exc:
                    logger.exception("Tool %s raised an exception", block.name)
                    result = {"error": f"Tool failed: {str(exc)}"}
                    content = json.dumps(result)
                    success = False
            else:
                result = {"error": f"Unknown tool: {block.name}"}
                content = json.dumps(result)
                success = False

            # ── Record tool call in LangFuse + Prometheus ─────────────────────
            observability.record_tool_call(
                parent=agent_span,
                agent_name=self.agent_name,
                tool_name=block.name,
                tool_input=dict(block.input),
                tool_output=result if isinstance(result, dict) else {"result": str(result)},
                success=success,
            )

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
