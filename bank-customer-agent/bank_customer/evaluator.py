from __future__ import annotations

from .messages import GOAL_COMPLETE_SENTINEL, ApiMessage


def goal_complete_in_message(text: str) -> bool:
    return GOAL_COMPLETE_SENTINEL in text
