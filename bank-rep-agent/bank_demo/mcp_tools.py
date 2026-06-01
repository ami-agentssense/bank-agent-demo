from __future__ import annotations

import asyncio
import logging
from typing import cast

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import get_mcp_frankfurter_enabled, get_mcp_frankfurter_url

logger = logging.getLogger(__name__)

_MCP_TOOL_CACHE: list[BaseTool] | None = None
_MCP_CACHE_KEY: tuple[bool, str] | None = None


def _candidate_urls(url: str) -> list[str]:
    clean = url.strip().rstrip("/")
    candidates = [clean]
    if not clean.endswith("/mcp"):
        candidates.append(f"{clean}/mcp")
    return candidates


async def _load_frankfurter_tools_async(url: str) -> list[BaseTool]:
    last_error: Exception | None = None

    for candidate in _candidate_urls(url):
        try:
            client = MultiServerMCPClient(
                {
                    "frankfurter": {
                        "transport": "http",
                        "url": candidate,
                    }
                }
            )
            tools = await client.get_tools()
            return cast(list[BaseTool], tools)
        except Exception as exc:  # pragma: no cover - exercised in fallback tests
            last_error = exc

    if last_error is not None:
        raise last_error
    return []


def get_frankfurter_mcp_tools() -> list[BaseTool]:
    """
    Return Frankfurter MCP tools as LangChain-compatible tools.

    - Uses env flags in `config.py`
    - Caches discovery across turns to avoid reconnecting every message
    - Falls back to [] if MCP is disabled/unavailable
    """
    global _MCP_TOOL_CACHE, _MCP_CACHE_KEY

    enabled = get_mcp_frankfurter_enabled()
    url = get_mcp_frankfurter_url()
    cache_key = (enabled, url)
    if _MCP_TOOL_CACHE is not None and _MCP_CACHE_KEY == cache_key:
        return list(_MCP_TOOL_CACHE)

    if not enabled:
        _MCP_TOOL_CACHE = []
        _MCP_CACHE_KEY = cache_key
        return []

    try:
        tools = asyncio.run(_load_frankfurter_tools_async(url))
    except Exception as exc:
        logger.warning("Frankfurter MCP unavailable at %s: %s", url, exc)
        tools = []

    _MCP_TOOL_CACHE = list(tools)
    _MCP_CACHE_KEY = cache_key
    return list(_MCP_TOOL_CACHE)


async def get_frankfurter_mcp_tools_async() -> list[BaseTool]:
    """
    Async-safe version of Frankfurter MCP tool loading.

    Use this from async flows to avoid nested `asyncio.run(...)` calls.
    """
    global _MCP_TOOL_CACHE, _MCP_CACHE_KEY

    enabled = get_mcp_frankfurter_enabled()
    url = get_mcp_frankfurter_url()
    cache_key = (enabled, url)
    if _MCP_TOOL_CACHE is not None and _MCP_CACHE_KEY == cache_key:
        return list(_MCP_TOOL_CACHE)

    if not enabled:
        _MCP_TOOL_CACHE = []
        _MCP_CACHE_KEY = cache_key
        return []

    try:
        tools = await _load_frankfurter_tools_async(url)
    except Exception as exc:
        logger.warning("Frankfurter MCP unavailable at %s: %s", url, exc)
        tools = []

    _MCP_TOOL_CACHE = list(tools)
    _MCP_CACHE_KEY = cache_key
    return list(_MCP_TOOL_CACHE)

