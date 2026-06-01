from __future__ import annotations

import sys

from langchain_core.messages import AIMessage, HumanMessage

from .agent import chat_reply, parse_run_request
from .config import anthropic_key_error_message, get_anthropic_api_key, load_env
from .executor import execute_plan, format_batch_report
from .plan import build_plan, format_plan
from .skill_catalog import build_catalog


def _is_confirm(text: str) -> bool:
    return text.strip().lower() in {"yes", "y", "run", "go", "proceed"}


def _is_cancel(text: str) -> bool:
    return text.strip().lower() in {"no", "n", "cancel"}


def _on_status(line: str) -> None:
    print(line, flush=True)


def _load_catalog(*, force: bool = False):
    return build_catalog(force=force, on_status=_on_status)


def run_cli() -> int:
    load_env()
    if get_anthropic_api_key() is None:
        print(anthropic_key_error_message(), file=sys.stderr)
        return 1

    print("Apex Bank Orchestrator — loading skills…", flush=True)
    catalog, _stats = _load_catalog()
    print("Type 'quit' to exit.\n", flush=True)

    history: list = []
    pending_plan = None

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        if user_input.lower() in {"refresh skills", "refresh"}:
            print("Refreshing skills…", flush=True)
            catalog, _stats = _load_catalog(force=True)
            print(flush=True)
            continue

        if pending_plan is not None and _is_confirm(user_input):
            print("Running…\n", flush=True)

            def on_progress(line: str) -> None:
                print(line, flush=True)

            def on_session_line(line: str) -> None:
                print(line, flush=True)

            results, unexpected = execute_plan(
                pending_plan,
                on_progress=on_progress,
                on_session_line=on_session_line,
            )
            print()
            print(format_batch_report(results, unexpected), flush=True)
            print(flush=True)
            pending_plan = None
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content="Run completed."))
            continue

        if pending_plan is not None and _is_cancel(user_input):
            print("Cancelled.\n", flush=True)
            pending_plan = None
            continue

        if pending_plan is not None:
            print("Reply yes to run or no to cancel.\n", flush=True)
            continue

        spec = parse_run_request(user_input, catalog, history=history)

        if spec.needs_clarification:
            print(spec.needs_clarification, flush=True)
            print(flush=True)
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=spec.needs_clarification))
            continue

        if spec.total_sessions < 1 and not spec.explicit_skills:
            reply = chat_reply(user_input, catalog, history)
            print(reply, flush=True)
            print(flush=True)
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=reply))
            continue

        plan = build_plan(spec, catalog)
        if any("No skills match" in w for w in plan.warnings):
            question = (
                "Some criteria matched no skills. "
                + "; ".join(plan.warnings)
                + " Please adjust your request."
            )
            print(question, flush=True)
            print(flush=True)
            history.append(HumanMessage(content=user_input))
            history.append(AIMessage(content=question))
            continue

        pending_plan = plan
        summary = format_plan(plan)
        print(summary, flush=True)
        print(flush=True)
        history.append(HumanMessage(content=user_input))
        history.append(AIMessage(content=summary))

    return 0
