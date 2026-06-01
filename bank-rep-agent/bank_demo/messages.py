from __future__ import annotations

import copy
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from .mock_data import CUSTOMERS, lookup_customer_id


def _text_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "".join(parts).strip()
    return ""


def to_api_messages(messages: list[BaseMessage]) -> list[dict[str, str]]:
    api_messages: list[dict[str, str]] = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            text = _text_content(msg.content)
            if text:
                api_messages.append({"role": "user", "content": text})
        elif isinstance(msg, AIMessage):
            text = _text_content(msg.content)
            if text:
                api_messages.append({"role": "assistant", "content": text})
    return api_messages


def from_api_messages(api_messages: list[dict[str, str]]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in api_messages:
        role = item.get("role", "")
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def sync_session_auth_from_messages(
    session: dict[str, Any],
    api_messages: list[dict[str, str]],
) -> None:
    session["verified_customer_id"] = None
    session["customer"] = None
    session["menu_sent"] = False
    session["active_skills"] = []

    for item in api_messages:
        if item.get("role") != "user":
            continue
        customer_id = lookup_customer_id(item.get("content", ""))
        if customer_id is None:
            continue
        session["verified_customer_id"] = customer_id
        session["customer"] = copy.deepcopy(CUSTOMERS[customer_id])
        session["menu_sent"] = True
