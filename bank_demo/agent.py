from __future__ import annotations

import asyncio
from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from .config import (
    get_anthropic_api_key,
    get_claude_model,
    get_mcp_frankfurter_enabled,
    get_mcp_frankfurter_url,
)
from .mcp_tools import get_frankfurter_mcp_tools_async
from .mock_data import STOCKS
from .prompts import build_agent_system_prompt
from .tools import make_banking_tools


def _last_assistant_text(messages: list[BaseMessage]) -> str:
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage):
            continue
        content = msg.content
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            parts = [
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            text = "".join(parts).strip()
            if text:
                return text
    return "I'm sorry, I couldn't process that request."


def run_bank_agent(
    *,
    session: dict[str, Any],
    user_message: str,
) -> str:
    return asyncio.run(_run_bank_agent_async(session=session, user_message=user_message))


async def _run_bank_agent_async(
    *,
    session: dict[str, Any],
    user_message: str,
) -> str:
    customer = session["customer"]
    local_tools = make_banking_tools(customer)
    mcp_tools = await get_frankfurter_mcp_tools_async()
    tools = [*local_tools, *mcp_tools]
    if not session.get("_mcp_tools_logged"):
        if get_mcp_frankfurter_enabled():
            if mcp_tools:
                session["_mcp_status"] = (
                    f"connected:{get_mcp_frankfurter_url()}:tools={len(mcp_tools)}"
                )
            else:
                session["_mcp_status"] = (
                    f"enabled_no_tools:{get_mcp_frankfurter_url()}"
                )
        else:
            session["_mcp_status"] = "disabled"
        session["_mcp_tools_logged"] = True
    system_prompt = build_agent_system_prompt(
        customer=customer,
        stocks=STOCKS,
        user_message=user_message,
        session=session,
    )

    llm = ChatAnthropic(
        api_key=get_anthropic_api_key(),
        model=get_claude_model(),
        max_tokens=2048,
    )
    agent = create_react_agent(llm, tools, prompt=system_prompt)

    messages: list[BaseMessage] = list(session.get("messages") or [])
    messages.append(HumanMessage(content=user_message))

    result = await agent.ainvoke({"messages": messages})
    new_messages: list[BaseMessage] = result["messages"]
    session["messages"] = new_messages

    return _last_assistant_text(new_messages)
