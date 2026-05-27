from __future__ import annotations

from bank_demo.graph import _format_customer_menu
import bank_demo.mcp_tools as mcp_tools


def _reset_mcp_cache() -> None:
    mcp_tools._MCP_TOOL_CACHE = None
    mcp_tools._MCP_CACHE_KEY = None


def test_services_menu_includes_currency_updates() -> None:
    menu = _format_customer_menu("Alice")
    assert "Check updated currency rates" in menu


def test_mcp_disabled_returns_no_tools(monkeypatch) -> None:
    _reset_mcp_cache()
    monkeypatch.setenv("MCP_FRANKFURTER_ENABLED", "false")
    tools = mcp_tools.get_frankfurter_mcp_tools()
    assert tools == []


def test_mcp_loader_fallback_returns_no_tools(monkeypatch) -> None:
    _reset_mcp_cache()
    monkeypatch.setenv("MCP_FRANKFURTER_ENABLED", "true")
    monkeypatch.setenv("MCP_FRANKFURTER_URL", "https://mcp.frankfurter.dev/")

    async def _boom(url: str):
        raise RuntimeError("network down")

    monkeypatch.setattr(mcp_tools, "_load_frankfurter_tools_async", _boom)
    tools = mcp_tools.get_frankfurter_mcp_tools()
    assert tools == []

