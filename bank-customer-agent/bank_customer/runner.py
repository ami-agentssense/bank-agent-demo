from __future__ import annotations

from dataclasses import dataclass

from .agent import run_customer_agent, split_goal_complete
from .client import BankRepClient, BankRepClientError
from .config import get_customer_conversation_log
from .evaluator import goal_complete_in_message
from .messages import ApiMessage


@dataclass
class RunResult:
    success: bool
    messages: list[ApiMessage]
    turns: int
    reason: str


def _log_turn(turn: int, user_message: str, assistant_message: str) -> None:
    if not get_customer_conversation_log():
        return
    print(f"--- turn {turn} ---", flush=True)
    print(f"CUSTOMER: {user_message}", flush=True)
    if assistant_message:
        print(f"BANK: {assistant_message}", flush=True)
    print(flush=True)


def _last_assistant_message(messages: list[ApiMessage]) -> str:
    for item in reversed(messages):
        if item.role == "assistant":
            return item.content
    return ""


def run_scenario(
    *,
    client: BankRepClient,
    skill_text: str,
    max_turns: int,
) -> RunResult:
    if not client.health():
        return RunResult(
            success=False,
            messages=[],
            turns=0,
            reason="bank rep API is not reachable",
        )

    messages = client.get_messages()
    turns = 0

    while turns < max_turns:
        turns += 1
        draft = run_customer_agent(skill_text=skill_text, messages=messages)
        user_message, goal_met = split_goal_complete(draft)

        if goal_met and not user_message:
            return RunResult(
                success=True,
                messages=messages,
                turns=turns,
                reason="goal complete",
            )

        if not user_message:
            return RunResult(
                success=False,
                messages=messages,
                turns=turns,
                reason="customer agent returned an empty message",
            )

        try:
            updated = client.post_messages(
                [*messages, ApiMessage(role="user", content=user_message)]
            )
        except BankRepClientError as exc:
            return RunResult(
                success=False,
                messages=messages,
                turns=turns,
                reason=str(exc),
            )

        assistant_message = _last_assistant_message(updated)
        _log_turn(turns, user_message, assistant_message)
        messages = updated

        if goal_met:
            return RunResult(
                success=True,
                messages=messages,
                turns=turns,
                reason="goal complete",
            )

        if goal_complete_in_message(user_message):
            return RunResult(
                success=True,
                messages=messages,
                turns=turns,
                reason="goal complete",
            )

    return RunResult(
        success=False,
        messages=messages,
        turns=turns,
        reason=f"max turns ({max_turns}) reached",
    )
