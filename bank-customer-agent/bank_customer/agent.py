from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from .config import get_anthropic_api_key, get_claude_model
from .messages import ApiMessage, GOAL_COMPLETE_SENTINEL
from .prompts import build_customer_system_prompt, format_conversation_for_llm


def run_customer_agent(
    *,
    skill_text: str,
    messages: list[ApiMessage],
) -> str:
    system_prompt = build_customer_system_prompt(skill_text)
    history = [{"role": m.role, "content": m.content} for m in messages]
    human_prompt = format_conversation_for_llm(history)

    llm = ChatAnthropic(
        api_key=get_anthropic_api_key(),
        model=get_claude_model(),
        max_tokens=512,
    )
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]
    )
    content = response.content
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


def split_goal_complete(text: str) -> tuple[str, bool]:
    if GOAL_COMPLETE_SENTINEL not in text:
        return text, False
    cleaned = text.replace(GOAL_COMPLETE_SENTINEL, "").strip()
    return cleaned, True
