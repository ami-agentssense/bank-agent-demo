from __future__ import annotations

import copy
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .agent import run_bank_agent
from .mock_data import CUSTOMERS, EXAMPLE_CUSTOMER_ID, lookup_customer_id
from .utils import get_first_name


def _session_defaults() -> dict[str, Any]:
    return {
        "verified_customer_id": None,
        "customer_id_prompted": False,
        "customer": None,
        "menu_sent": False,
        "messages": [],
        "active_skills": [],
    }


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


def _format_customer_menu(name: str) -> str:
    return (
        f"Hello {name}! I'm {BANKER_NAME}, your personal banker. "
        "I'm here to help you today. Here's what I can assist you with:\n"
        "* Check your account balance\n"
        "* Apply for a loan\n"
        "* Open a 12-month term deposit\n"
        "* Buy stocks\n"
        "* Check updated currency rates\n"
        "* Close your account\n"
        "What would you like to do?"
    )


def _auth_gate_node(state: BankGraphState) -> dict[str, Any]:
    user_message = state["user_message"]
    session = state["session_state"]

    if session.get("verified_customer_id") is None:
        if not session.get("customer_id_prompted", False):
            session["customer_id_prompted"] = True
            return {
                "assistant_message": initial_greeting(),
                "session_state": session,
            }

        customer_id = lookup_customer_id(user_message)
        if customer_id is not None:
            session["verified_customer_id"] = customer_id
            session["customer"] = copy.deepcopy(CUSTOMERS[customer_id])
            session["messages"] = []
            session["active_skills"] = []
            session["menu_sent"] = True

            first_name = get_first_name(session["customer"]["name"])
            return {
                "assistant_message": _format_customer_menu(first_name),
                "session_state": session,
            }

        return {
            "assistant_message": (
                "I'm sorry, I wasn't able to find an account with that ID. "
                f"Please double-check and try again (for example: {EXAMPLE_CUSTOMER_ID})."
            ),
            "session_state": session,
        }

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
        session = state["session_state"]
        if session.get("verified_customer_id") is None:
            return END
        if state.get("assistant_message"):
            return END
        return "bank_agent"

    graph.add_edge(START, "auth_gate")
    graph.add_conditional_edges("auth_gate", _route_after_auth)
    graph.add_edge("bank_agent", END)

    return graph.compile()
