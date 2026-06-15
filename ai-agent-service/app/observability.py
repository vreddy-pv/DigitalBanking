"""
Unified observability for ai-agent-service.

Three layers (all optional / graceful fallback):
  1. LangFuse  — AI-specific tracing: LLM calls, tool calls, token usage
  2. Datadog   — Infrastructure APM: FastAPI, httpx, Redis auto-patched
  3. Prometheus — Custom metrics exported at GET /metrics

Enable via environment variables:
  LANGFUSE_ENABLED=true   LANGFUSE_PUBLIC_KEY=... LANGFUSE_SECRET_KEY=...
  DD_TRACE_ENABLED=true   (DD_AGENT_HOST / DD_AGENT_PORT default to datadog-agent:8126)
  Prometheus is always on (no external dependency).
"""

import contextvars
import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Context var: carry the active LangFuse trace through async call chains ──
_trace_ctx: contextvars.ContextVar[Optional[Any]] = contextvars.ContextVar(
    "langfuse_trace", default=None
)


# ── Prometheus metrics ────────────────────────────────────────────────────────

class _Metrics:
    def __init__(self) -> None:
        self.enabled = False
        try:
            from prometheus_client import Counter, Histogram

            self.agent_invocations: Counter = Counter(
                "banking_agent_invocations_total",
                "Total agent invocations",
                ["agent_name", "status"],
            )
            self.agent_latency: Histogram = Histogram(
                "banking_agent_latency_seconds",
                "Agent end-to-end latency in seconds",
                ["agent_name"],
                buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
            )
            self.llm_tokens: Counter = Counter(
                "banking_llm_tokens_total",
                "LLM tokens consumed",
                ["agent_name", "token_type"],  # token_type: input | output
            )
            self.tool_calls: Counter = Counter(
                "banking_tool_calls_total",
                "Tool invocations",
                ["agent_name", "tool_name", "status"],  # status: success | error
            )
            self.intent_classifications: Counter = Counter(
                "banking_intent_classifications_total",
                "Intent labels produced by the orchestrator classifier",
                ["intent"],
            )
            self.enabled = True
            logger.info("✓ Prometheus metrics ready")
        except ImportError:
            logger.warning("prometheus_client not installed — metrics endpoint will return 503")


# ── Main manager ─────────────────────────────────────────────────────────────

class ObservabilityManager:
    def __init__(self) -> None:
        self._langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
        self._dd_enabled = os.getenv("DD_TRACE_ENABLED", "false").lower() == "true"
        self._env = os.getenv("ENV", "dev")
        self._version = os.getenv("APP_VERSION", "2.0.0")
        self._lf: Optional[Any] = None  # Langfuse client
        self.metrics = _Metrics()

    # ── Init ─────────────────────────────────────────────────────────────────

    def init(self) -> None:
        if self._langfuse_enabled:
            self._init_langfuse()
        if self._dd_enabled:
            self._init_datadog()
        logger.info(
            "Observability — langfuse=%s datadog=%s prometheus=%s env=%s",
            self._langfuse_enabled,
            self._dd_enabled,
            self.metrics.enabled,
            self._env,
        )

    def _init_langfuse(self) -> None:
        try:
            from langfuse import Langfuse

            self._lf = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "http://langfuse-server:3001"),
                threads=5,
                flush_at=50,
                flush_interval=30,
            )
            logger.info("✓ LangFuse initialised (host=%s)", os.getenv("LANGFUSE_HOST"))
        except Exception as exc:
            logger.error("✗ LangFuse init failed (%s) — proceeding without it", exc)
            self._langfuse_enabled = False

    def _init_datadog(self) -> None:
        try:
            from ddtrace import config as dd_cfg, patch_all

            patch_all(fastapi=True, httpx=True, redis=True, logging=True)
            dd_cfg.service = os.getenv("DD_SERVICE", "ai-agent-service")
            dd_cfg.env = self._env
            dd_cfg.version = self._version
            logger.info("✓ Datadog APM initialised (env=%s service=%s)", self._env, dd_cfg.service)
        except Exception as exc:
            logger.error("✗ Datadog init failed (%s) — proceeding without it", exc)
            self._dd_enabled = False

    # ── Request-level (per-chat) trace ────────────────────────────────────────

    def start_request_trace(
        self, user_id: str, message: str, session_id: str
    ) -> Optional[Any]:
        """
        Open a LangFuse trace for one chat request and store it in the async
        context so downstream agents can attach child spans to it.
        Returns the trace object (or None when LangFuse is disabled).
        """
        if not self._lf:
            return None
        try:
            trace = self._lf.trace(
                name="chat_request",
                user_id=user_id,
                session_id=session_id,
                input={"message": message},
                tags=[self._env, "digital-banking"],
            )
            _trace_ctx.set(trace)
            return trace
        except Exception as exc:
            logger.debug("LangFuse trace start failed: %s", exc)
            return None

    def finish_request_trace(
        self, trace: Optional[Any], output: str, agent_used: str
    ) -> None:
        if trace is None:
            return
        try:
            trace.update(output={"response": output, "agent_used": agent_used})
        except Exception as exc:
            logger.debug("LangFuse trace finish failed: %s", exc)

    def get_current_trace(self) -> Optional[Any]:
        """Retrieve the trace created for the current async request."""
        return _trace_ctx.get()

    def flush(self) -> None:
        """Flush buffered LangFuse events to the server."""
        if self._lf:
            try:
                self._lf.flush()
            except Exception:
                pass

    # ── Agent-level spans ─────────────────────────────────────────────────────

    def start_agent_span(self, agent_name: str, input_msg: str) -> Optional[Any]:
        trace = self.get_current_trace()
        if trace is None:
            return None
        try:
            return trace.span(
                name=f"{agent_name.lower()}_agent",
                input={"agent": agent_name, "last_message": input_msg[:300]},
            )
        except Exception:
            return None

    def finish_agent_span(self, span: Optional[Any], output: str) -> None:
        if span is None:
            return
        try:
            span.end(output={"summary": output[:400]})
        except Exception:
            pass

    # ── LLM generation recording ──────────────────────────────────────────────

    def record_llm_generation(
        self,
        parent: Optional[Any],
        agent_name: str,
        model: str,
        messages: list,
        response_text: str,
        input_tokens: int,
        output_tokens: int,
        iteration: int,
    ) -> None:
        if parent is not None:
            try:
                gen = parent.generation(
                    name=f"llm_call_iter_{iteration}",
                    model=model,
                    input=messages[-4:],   # last 4 turns to keep payload small
                    output=response_text,
                    usage={
                        "input": input_tokens,
                        "output": output_tokens,
                        "unit": "TOKENS",
                    },
                )
                gen.end()
            except Exception:
                pass

        if self.metrics.enabled:
            self.metrics.llm_tokens.labels(agent_name, "input").inc(input_tokens)
            self.metrics.llm_tokens.labels(agent_name, "output").inc(output_tokens)

    # ── Tool call recording ───────────────────────────────────────────────────

    def record_tool_call(
        self,
        parent: Optional[Any],
        agent_name: str,
        tool_name: str,
        tool_input: dict,
        tool_output: dict,
        success: bool,
    ) -> None:
        if parent is not None:
            try:
                span = parent.span(
                    name=f"tool_{tool_name}",
                    input=tool_input,
                    output=tool_output,
                )
                span.end()
            except Exception:
                pass

        if self.metrics.enabled:
            status = "success" if success else "error"
            self.metrics.tool_calls.labels(agent_name, tool_name, status).inc()

    # ── Intent classification recording ──────────────────────────────────────

    def record_intent(self, intent: str) -> None:
        if self.metrics.enabled:
            self.metrics.intent_classifications.labels(intent).inc()


# ── Singleton ─────────────────────────────────────────────────────────────────
observability = ObservabilityManager()
