from __future__ import annotations

from pydantic import BaseModel, Field


class ApiMessage(BaseModel):
    role: str
    content: str


class MessagesRequest(BaseModel):
    messages: list[ApiMessage] = Field(min_length=1)


class MessagesResponse(BaseModel):
    messages: list[ApiMessage]


class HealthResponse(BaseModel):
    status: str


GOAL_COMPLETE_SENTINEL = "[GOAL_COMPLETE]"


def to_payload(messages: list[ApiMessage]) -> list[dict[str, str]]:
    return [item.model_dump() for item in messages]


def from_payload(items: list[dict[str, str]]) -> list[ApiMessage]:
    return [ApiMessage(role=item["role"], content=item["content"]) for item in items]
