import json
import logging
from collections import defaultdict

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory fallback used when Redis is unavailable
_fallback: dict[str, list[dict]] = defaultdict(list)


class ConversationMemory:
    def __init__(self, redis_client: aioredis.Redis | None):
        self._redis = redis_client

    def _key(self, user_id: str) -> str:
        return f"chat:session:{user_id}"

    async def get_history(self, user_id: str) -> list[dict]:
        key = self._key(user_id)
        if self._redis:
            try:
                raw = await self._redis.get(key)
                return json.loads(raw) if raw else []
            except Exception:
                logger.warning("Redis read failed, using fallback")
        return list(_fallback[key])

    async def add_turn(self, user_id: str, user_message: str, assistant_reply: str) -> None:
        key = self._key(user_id)
        history = await self.get_history(user_id)

        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_reply})

        # Sliding window: keep last N turns (each turn = 2 messages)
        max_messages = settings.max_conversation_turns * 2
        if len(history) > max_messages:
            history = history[-max_messages:]

        if self._redis:
            try:
                await self._redis.set(key, json.dumps(history), ex=settings.session_ttl_seconds)
                return
            except Exception:
                logger.warning("Redis write failed, using fallback")
        _fallback[key] = history

    async def clear(self, user_id: str) -> None:
        key = self._key(user_id)
        if self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                logger.warning("Redis delete failed")
        _fallback.pop(key, None)


async def create_memory() -> ConversationMemory:
    try:
        client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        logger.info("Redis connected: %s", settings.redis_url)
        return ConversationMemory(client)
    except Exception:
        logger.warning("Redis unavailable — using in-memory session store")
        return ConversationMemory(None)
