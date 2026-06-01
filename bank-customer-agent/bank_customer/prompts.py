from __future__ import annotations

from .messages import GOAL_COMPLETE_SENTINEL


def build_customer_system_prompt(skill_text: str) -> str:
    return (
        "You are a bank customer chatting with Jenny, your personal banker at Apex Bank.\n\n"
        "Follow the skill below for your identity, goal, and behavior.\n\n"
        "OUTPUT RULES:\n"
        "1. Write ONLY your next message as the customer — no labels or explanations.\n"
        "2. Be natural, polite, and concise.\n"
        "3. Answer Jenny's questions with specific values when she asks.\n"
        "4. When Jenny asks to confirm an action, reply with a clear yes.\n"
        "5. Do not invent balances, prices, or rates — trust what Jenny tells you.\n"
        f"6. When your goal is fully achieved, send exactly: {GOAL_COMPLETE_SENTINEL}\n\n"
        "SKILL:\n"
        f"{skill_text}\n"
    )


def format_conversation_for_llm(messages: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for item in messages:
        role = item.get("role", "")
        content = item.get("content", "").strip()
        if not content:
            continue
        if role == "assistant":
            lines.append(f"Jenny: {content}")
        elif role == "user":
            lines.append(f"You: {content}")

    if not lines:
        return "Jenny has greeted you. Write your next message as the customer:"

    transcript = "\n".join(lines)
    return (
        f"{transcript}\n\n"
        "Write your next message as the customer:"
    )
