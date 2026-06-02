from __future__ import annotations

import copy
from typing import Any, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from .agent import run_bank_agent
from .mock_data import CUSTOMERS, lookup_customer_id
from .utils import format_customer_menu, get_first_name


def _session_defaults() -> dict[str, Any]:
    return {
        "session_id": "",
        "verified_customer_id": None,
        "customer_id_prompted": True,
        "customer": None,
        "menu_sent": False,
        "messages": [AIMessage(content=initial_greeting())],
        "active_skills": [],
    }


def _append_turn(session: dict[str, Any], user_message: str, assistant_text: str) -> None:
    messages = list(session.get("messages") or [])
    messages.append(HumanMessage(content=user_message))
    messages.append(AIMessage(content=assistant_text))
    session["messages"] = messages


class BankGraphState(TypedDict):
    user_message: str
    session_state: dict[str, Any]
    assistant_message: str


BANKER_NAME = "Jenny"


def initial_greeting() -> str:
    return (
        f"Hello! I'm {BANKER_NAME}, your personal banker at Apex Bank. "
        "Before we proceed, could you please provide me with your Customer ID?"
    )


def _auth_gate_node(state: BankGraphState) -> dict[str, Any]:
    user_message = state["user_message"]
    session = state["session_state"]

    if session.get("verified_customer_id") is None:
        customer_id = lookup_customer_id(user_message)
        if customer_id is not None:
            session["verified_customer_id"] = customer_id
            session["customer"] = copy.deepcopy(CUSTOMERS[customer_id])
            session["active_skills"] = []
            session["menu_sent"] = True

            first_name = get_first_name(session["customer"]["name"])
            reply = format_customer_menu(first_name, banker_name=BANKER_NAME)
            _append_turn(session, user_message, reply)
            return {
                "assistant_message": reply,
                "session_state": session,
            }

        return {"assistant_message": "", "session_state": session}

    return {"assistant_message": "", "session_state": session}


def _bank_agent_node(state: BankGraphState) -> dict[str, Any]:
    session = state["session_state"]
    reply = run_bank_agent(session=session, user_message=state["user_message"])
    return {"assistant_message": reply, "session_state": session}


def build_app():
    graph = StateGraph(BankGraphState)

    graph.add_node("auth_gate", _auth_gate_node)
    graph.add_node("bank_agent", _bank_agent_node)

    def _route_after_auth(state: BankGraphState) -> Literal["bank_agent", END]:
        if state.get("assistant_message"):
            return END
        return "bank_agent"

    graph.add_edge(START, "auth_gate")
    graph.add_conditional_edges("auth_gate", _route_after_auth)
    graph.add_edge("bank_agent", END)

    return graph.compile()
