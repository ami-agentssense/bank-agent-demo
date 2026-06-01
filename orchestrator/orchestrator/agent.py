from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from .config import get_anthropic_api_key, get_claude_model
from .plan import RunPlanSpec
from .prompts import build_system_prompt
from .skill_catalog import SkillCatalog


def parse_run_request(
    user_message: str,
    catalog: SkillCatalog,
    history: list[BaseMessage] | None = None,
) -> RunPlanSpec:
    llm = ChatAnthropic(
        api_key=get_anthropic_api_key(),
        model=get_claude_model(),
        max_tokens=1024,
    )
    structured = llm.with_structured_output(RunPlanSpec)
    messages: list[BaseMessage] = [
        SystemMessage(content=build_system_prompt(catalog)),
        *(history or []),
        HumanMessage(content=user_message),
    ]
    return structured.invoke(messages)


def chat_reply(
    user_message: str,
    catalog: SkillCatalog,
    history: list[BaseMessage],
) -> str:
    llm = ChatAnthropic(
        api_key=get_anthropic_api_key(),
        model=get_claude_model(),
        max_tokens=512,
    )
    messages: list[BaseMessage] = [
        SystemMessage(content=build_system_prompt(catalog)),
        *history,
        HumanMessage(content=user_message),
    ]
    response = llm.invoke(messages)
    content = response.content
    if isinstance(content, str):
        return content.strip()
    return "How can I help with your automation run?"
