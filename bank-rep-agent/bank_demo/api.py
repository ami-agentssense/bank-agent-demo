from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_api_conversation_log, load_env
from .graph import _session_defaults, build_app
from .messages import (
    from_api_messages,
    sync_session_auth_from_messages,
    to_api_messages,
)

load_env()

app = FastAPI(title="Apex Bank API", version="0.1.0")

_graph_app = build_app()
_session_state: dict[str, Any] = _session_defaults()

_PROMPT_BLUE = "\033[34m"
_PROMPT_RESET = "\033[0m"


def _log_prompt(text: str, *, user: bool = False) -> None:
    prefix = "PROMPTS: USER: " if user else "PROMPTS: "
    print(f"{_PROMPT_BLUE}{prefix}{text}{_PROMPT_RESET}", flush=True)


class ApiMessage(BaseModel):
    role: str
    content: str


class MessagesRequest(BaseModel):
    messages: list[ApiMessage] = Field(min_length=1)


class MessagesResponse(BaseModel):
    messages: list[ApiMessage]


class HealthResponse(BaseModel):
    status: str


def reset_session_state() -> None:
    global _session_state
    _session_state = _session_defaults()
    _log_greeting()


def get_session_messages() -> list[dict[str, str]]:
    return to_api_messages(_session_state["messages"])


def _log_greeting() -> None:
    if not get_api_conversation_log():
        return
    api_messages = get_session_messages()
    if not api_messages:
        return
    print("Apex Bank — Jenny (API)\n", flush=True)
    _log_prompt(api_messages[0]["content"])
    print(flush=True)


def _log_turn(user_message: str, assistant_message: str) -> None:
    if not get_api_conversation_log():
        return
    _log_prompt(user_message, user=True)
    if assistant_message:
        _log_prompt(assistant_message)
    print(flush=True)


def post_session_messages(client_messages: list[dict[str, str]]) -> list[dict[str, str]]:
    global _session_state

    if not client_messages:
        raise ValueError("messages must not be empty")
    if client_messages[-1].get("role") != "user":
        raise ValueError("last message must have role 'user'")

    sync_session_auth_from_messages(_session_state, client_messages)
    history = client_messages[:-1]
    _session_state["messages"] = from_api_messages(history)
    user_message = client_messages[-1]["content"]

    result = _graph_app.invoke(
        {
            "user_message": user_message,
            "session_state": _session_state,
            "assistant_message": "",
        }
    )
    _log_turn(user_message, (result.get("assistant_message") or "").strip())

    return to_api_messages(_session_state["messages"])


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/api/v1/messages", response_model=MessagesResponse)
def get_messages() -> MessagesResponse:
    return MessagesResponse(
        messages=[ApiMessage(**item) for item in get_session_messages()]
    )


@app.post("/api/v1/messages", response_model=MessagesResponse)
def post_messages(body: MessagesRequest) -> MessagesResponse:
    payload = [item.model_dump() for item in body.messages]
    for item in payload:
        if item["role"] not in {"user", "assistant"}:
            raise HTTPException(status_code=400, detail="role must be 'user' or 'assistant'")

    try:
        updated = post_session_messages(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return MessagesResponse(messages=[ApiMessage(**item) for item in updated])


@app.on_event("startup")
def _on_startup() -> None:
    _log_greeting()
