from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root (parent of the bank_demo package).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

_PLACEHOLDER_VALUES = frozenset(
    {
        "",
        "your_anthropic_api_key_here",
        "YOUR_ANTHROPIC_API_KEY",
        "sk-ant-...",
    }
)
_OPENAI_PLACEHOLDER_VALUES = frozenset({"your_openai_api_key_here", "YOUR_OPENAI_API_KEY"})


def _normalize_key(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().strip('"').strip("'")
    if value in _PLACEHOLDER_VALUES:
        return None
    return value


def load_env() -> None:
    """Load variables from `.env` in the project root (if present)."""
    if ENV_FILE.is_file():
        # `.env` is the source of truth for local development.
        load_dotenv(ENV_FILE, override=True)


def get_anthropic_api_key() -> str | None:
    return _normalize_key(os.getenv("ANTHROPIC_API_KEY"))


def get_openai_api_key() -> str | None:
    key = os.getenv("OPENAI_API_KEY")
    key = _normalize_key(key)
    if key is None:
        return None
    if key in _OPENAI_PLACEHOLDER_VALUES:
        return None
    return key


def anthropic_key_error_message() -> str:
    if not ENV_FILE.is_file():
        return (
            f"Missing `.env` file at {ENV_FILE}. "
            "Copy `.env.example` to `.env` and set ANTHROPIC_API_KEY."
        )

    from dotenv import dotenv_values

    file_key = (dotenv_values(ENV_FILE).get("ANTHROPIC_API_KEY") or "").strip()
    if file_key in _PLACEHOLDER_VALUES or not file_key:
        return (
            f"Set a real Anthropic API key in `{ENV_FILE.name}` "
            "(replace `your_anthropic_api_key_here`) and save the file."
        )

    return (
        f"Could not load ANTHROPIC_API_KEY from `{ENV_FILE}`. "
        "Check the file format: ANTHROPIC_API_KEY=sk-ant-..."
    )


def get_claude_model() -> str:
    return os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001").strip()


def get_openai_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()


def get_llm_provider() -> str:
    provider = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    if provider in {"anthropic", "openai"}:
        return provider
    return "anthropic"


def get_selective_skill_loading() -> bool:
    """When true, only relevant skill markdown files are appended to the system prompt."""
    val = os.getenv("SELECTIVE_SKILL_LOADING", "false").strip().lower()
    return val in {"1", "true", "yes", "on"}


def get_mcp_frankfurter_enabled() -> bool:
    """Enable/disable loading tools from the Frankfurter MCP server."""
    val = os.getenv("MCP_FRANKFURTER_ENABLED", "true").strip().lower()
    return val in {"1", "true", "yes", "on"}


def get_mcp_frankfurter_url() -> str:
    """
    Frankfurter MCP endpoint URL.
    The default points to the public server and can be overridden in `.env`.
    """
    return os.getenv("MCP_FRANKFURTER_URL", "https://mcp.frankfurter.dev/").strip()


def get_api_conversation_log() -> bool:
    """When true, POST /api/v1/messages prints each turn to the server terminal."""
    val = os.getenv("API_CONVERSATION_LOG", "true").strip().lower()
    return val in {"1", "true", "yes", "on"}


def openai_key_error_message() -> str:
    if not ENV_FILE.is_file():
        return (
            f"Missing `.env` file at {ENV_FILE}. "
            "Copy `.env.example` to `.env` and set OPENAI_API_KEY."
        )

    from dotenv import dotenv_values

    file_key = (dotenv_values(ENV_FILE).get("OPENAI_API_KEY") or "").strip()
    if file_key in _PLACEHOLDER_VALUES or not file_key:
        return (
            f"Set a real OpenAI API key in `{ENV_FILE.name}` "
            "(replace `your_openai_api_key_here`) and save the file."
        )

    return (
        f"Could not load OPENAI_API_KEY from `{ENV_FILE}`. "
        "Check the file format: OPENAI_API_KEY=sk-..."
    )
