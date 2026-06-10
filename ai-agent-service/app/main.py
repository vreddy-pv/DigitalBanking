import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents import casa_agent, ml_agent, usl_agent
from app.agents.orchestrator import Orchestrator
from app.auth.jwt_validator import UserContext, validate_token
from app.memory.redis_memory import ConversationMemory, create_memory

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# Singletons created at startup
_memory: ConversationMemory | None = None
_orchestrator: Orchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _memory, _orchestrator
    _memory = await create_memory()
    _orchestrator = Orchestrator(
        casa=casa_agent.build(),
        ml=ml_agent.build(),
        usl=usl_agent.build(),
    )
    logger.info("ai-agent-service ready")
    yield


app = FastAPI(
    title="AI Agent Service",
    description="Orchestrator + CASA / ML / USL specialist agents for Digital Banking",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────

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


# ── Routes ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "UP", "service": "ai-agent-service"}


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: UserContext = Depends(validate_token),
):
    history = await _memory.get_history(user.user_id)
    agent_response = await _orchestrator.route(request.message, history, user)
    await _memory.add_turn(user.user_id, request.message, agent_response.text)

    return ChatResponse(
        response=agent_response.text,
        agent_used=agent_response.agent_used,
        session_id=user.user_id,
        ticket_id=agent_response.ticket_id,
    )


@app.get("/api/v1/chat/history", response_model=HistoryResponse)
async def get_history(user: UserContext = Depends(validate_token)):
    turns = await _memory.get_history(user.user_id)
    return HistoryResponse(session_id=user.user_id, turns=turns)


@app.delete("/api/v1/chat/history", status_code=204)
async def clear_history(user: UserContext = Depends(validate_token)):
    await _memory.clear(user.user_id)
