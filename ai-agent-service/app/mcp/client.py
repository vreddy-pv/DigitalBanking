import logging
from typing import Any, Callable, Coroutine

import httpx

from app.auth.jwt_validator import UserContext

logger = logging.getLogger(__name__)


class MCPToolClient:
    """
    HTTP client for MCP adapter servers.
    Wraps each adapter's REST API into tool handlers compatible with BaseAgent.
    user_id is injected automatically — Claude never sees it in the tool schema.
    """

    def __init__(self, server_url: str, name: str) -> None:
        self._url = server_url.rstrip("/")
        self._name = name

    def make_handlers(
        self, tool_names: list[str]
    ) -> dict[str, Callable[..., Coroutine[Any, Any, dict]]]:
        """Build a handler dict keyed by tool name, each proxying to the MCP adapter."""
        return {name: self._make_handler(name) for name in tool_names}

    def _make_handler(self, tool_name: str) -> Callable[..., Coroutine[Any, Any, dict]]:
        adapter_url = f"{self._url}/api/tools/{tool_name}"
        server_name = self._name

        async def _handler(user_context: UserContext, **kwargs: Any) -> dict:
            payload = {"user_id": user_context.user_id, **kwargs}
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(adapter_url, json=payload)
                    if resp.status_code == 404:
                        return {"error": f"Tool '{tool_name}' not found on {server_name}"}
                    resp.raise_for_status()
                    return resp.json()
            except httpx.TimeoutException:
                logger.error("Timeout calling %s on %s", tool_name, server_name)
                return {"error": f"MCP adapter {server_name} timed out. Please try again."}
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP %s from %s/%s", exc.response.status_code, server_name, tool_name)
                return {"error": f"Backend error from {server_name}: {exc.response.status_code}"}

        return _handler
