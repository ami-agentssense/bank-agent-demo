from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent
ENV_FILE = PROJECT_ROOT / ".env"

_PLACEHOLDER_VALUES = frozenset(
    {
        "",
        "your_anthropic_api_key_here",
        "YOUR_ANTHROPIC_API_KEY",
        "sk-ant-...",
    }
)


def load_env() -> None:
    if ENV_FILE.is_file():
        load_dotenv(ENV_FILE, override=True)


def get_anthropic_api_key() -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY")
    if key is None:
        return None
    key = key.strip().strip('"').strip("'")
    if key in _PLACEHOLDER_VALUES:
        return None
    return key


def anthropic_key_error_message() -> str:
    if not ENV_FILE.is_file():
        return (
            f"Missing `.env` file at {ENV_FILE}. "
            "Copy `.env.example` to `.env` and set ANTHROPIC_API_KEY."
        )
    return f"Set a real Anthropic API key in `{ENV_FILE.name}` and save the file."


def get_claude_model() -> str:
    return os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001").strip()


def get_bank_rep_base_url() -> str:
    return os.getenv("BANK_REP_BASE_URL", "http://127.0.0.1:8000").strip().rstrip("/")


def _resolve_path(env_name: str, default_relative: str) -> Path:
    raw = os.getenv(env_name, default_relative).strip()
    path = Path(raw)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def get_bank_rep_dir() -> Path:
    return _resolve_path("BANK_REP_DIR", "bank-rep-agent")


def get_customer_agent_dir() -> Path:
    return _resolve_path("CUSTOMER_AGENT_DIR", "bank-customer-agent")


def get_skills_dir() -> Path:
    return _resolve_path("SKILLS_DIR", "bank-customer-agent/skills")


def get_max_turns() -> int:
    raw = os.getenv("MAX_TURNS", "30").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 30


def get_rep_startup_timeout() -> float:
    raw = os.getenv("REP_STARTUP_TIMEOUT", "30").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 30.0


def get_rep_pre_customer_delay() -> float:
    raw = os.getenv("REP_PRE_CUSTOMER_DELAY", "1").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 1.0


def get_long_turn_threshold() -> int:
    raw = os.getenv("LONG_TURN_THRESHOLD", "25").strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return 25


def get_customer_conversation_log() -> bool:
    val = os.getenv("CUSTOMER_CONVERSATION_LOG", "false").strip().lower()
    return val in {"1", "true", "yes", "on"}


def get_orchestrator_stream_transcript() -> bool:
    val = os.getenv("ORCHESTRATOR_STREAM_TRANSCRIPT", "true").strip().lower()
    return val in {"1", "true", "yes", "on"}


def get_orchestrator_stream_turns_only() -> bool:
    val = os.getenv("ORCHESTRATOR_STREAM_TURNS_ONLY", "true").strip().lower()
    return val in {"1", "true", "yes", "on"}


def get_skill_index_path() -> Path:
    raw = os.getenv("SKILL_INDEX_PATH", ".skill_index.json").strip()
    path = Path(raw)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return path
