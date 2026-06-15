import json
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents import casa_agent, complaint_agent, cul_agent, ml_agent
from app.agents.orchestrator import Orchestrator
from app.auth.jwt_validator import UserContext, validate_token
from app.memory.redis_memory import ConversationMemory, create_memory
from app.observability import observability
from app.workers.investigation_worker import InvestigationWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

_memory: ConversationMemory | None = None
_orchestrator: Orchestrator | None = None
_investigation_worker: InvestigationWorker | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _memory, _orchestrator, _investigation_worker

    # ── Observability must initialise first (patches httpx/redis before clients open) ──
    observability.init()

    _memory = await create_memory()
    _orchestrator = Orchestrator(
        casa=casa_agent.build(),
        ml=ml_agent.build(),
        cul=cul_agent.build(),
        complaint=complaint_agent.build(),
    )
    _investigation_worker = InvestigationWorker()
    await _investigation_worker.start()
    logger.info("ai-agent-service ready — CASA / ML / CUL / COMPLAINT agents online")
    yield
    await _investigation_worker.stop()
    observability.flush()


app = FastAPI(
    title="AI Agent Service",
    description="Orchestrator + CASA / ML / CUL / COMPLAINT specialist agents for Digital Banking",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    response: str
    agent_used: str
    session_id: str
    ticket_id: str | None = None


class HistoryResponse(BaseModel):
    session_id: str
    turns: list[dict]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "UP", "service": "ai-agent-service", "version": "2.0.0"}


@app.get("/metrics", include_in_schema=False)
async def prometheus_metrics():
    """Prometheus scrape endpoint — collected by Datadog Agent or Prometheus."""
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return Response(
            content="# prometheus_client not installed\n",
            status_code=503,
            media_type="text/plain",
        )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: UserContext = Depends(validate_token),
):
    history = await _memory.get_history(user.user_id)

    # ── Open LangFuse trace for this request ──────────────────────────────────
    trace = observability.start_request_trace(
        user_id=user.user_id,
        message=request.message,
        session_id=user.user_id,
    )

    try:
        agent_response = await _orchestrator.route(request.message, history, user)
        await _memory.add_turn(user.user_id, request.message, agent_response.text)
        observability.finish_request_trace(trace, agent_response.text, agent_response.agent_used)
        return ChatResponse(
            response=agent_response.text,
            agent_used=agent_response.agent_used,
            session_id=user.user_id,
            ticket_id=agent_response.ticket_id,
        )
    finally:
        observability.flush()


@app.post("/api/v1/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: UserContext = Depends(validate_token),
):
    """
    SSE streaming endpoint.  Runs the full agentic loop (including all tool calls),
    then streams the final text response word-by-word via Server-Sent Events.

    Event format:
      data: {"text": "<chunk>", "agent": "<agent_name>"}   — text chunk
      data: {"done": true, "agent": "...", "ticket_id": null}  — completion
    """
    async def generate():
        history = await _memory.get_history(user.user_id)
        trace = observability.start_request_trace(
            user_id=user.user_id,
            message=request.message,
            session_id=user.user_id,
        )
        try:
            agent_response = await _orchestrator.route(request.message, history, user)
            await _memory.add_turn(user.user_id, request.message, agent_response.text)
            observability.finish_request_trace(
                trace, agent_response.text, agent_response.agent_used
            )
        finally:
            observability.flush()

        words = agent_response.text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == 0 else f" {word}"
            yield f"data: {json.dumps({'text': chunk, 'agent': agent_response.agent_used})}\n\n"

        yield f"data: {json.dumps({'done': True, 'agent': agent_response.agent_used, 'ticket_id': agent_response.ticket_id})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/v1/chat/history", response_model=HistoryResponse)
async def get_history(user: UserContext = Depends(validate_token)):
    turns = await _memory.get_history(user.user_id)
    return HistoryResponse(session_id=user.user_id, turns=turns)


@app.delete("/api/v1/chat/history", status_code=204)
async def clear_history(user: UserContext = Depends(validate_token)):
    await _memory.clear(user.user_id)
