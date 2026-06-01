from __future__ import annotations

from .config import anthropic_key_error_message, get_anthropic_api_key, load_env
from .graph import build_app, _session_defaults
from .messages import to_api_messages


def run_cli() -> None:
    load_env()

    if not get_anthropic_api_key():
        print(anthropic_key_error_message())
        return

    app = build_app()
    session_state = _session_defaults()

    print("Apex Bank — chat with Jenny (type /quit to exit).\n")
    greeting = to_api_messages(session_state["messages"])[0]["content"]
    print(greeting)
    print()

    while True:
        try:
            user_message = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_message:
            continue
        if user_message.lower() in {"/quit", "quit", "exit"}:
            break

        try:
            result = app.invoke(
                {
                    "user_message": user_message,
                    "session_state": session_state,
                    "assistant_message": "",
                }
            )
        except Exception as e:
            print(f"Error: {e}")
            continue

        session_state = result["session_state"]
        assistant_message = result.get("assistant_message") or ""
        if assistant_message:
            print(assistant_message)


if __name__ == "__main__":
    run_cli()

