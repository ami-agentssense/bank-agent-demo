from bank_demo.graph import _session_defaults, build_app, initial_greeting
from bank_demo.messages import to_api_messages


def test_session_defaults_includes_greeting():
    session = _session_defaults()
    api_messages = to_api_messages(session["messages"])
    assert len(api_messages) == 1
    assert api_messages[0]["role"] == "assistant"
    assert api_messages[0]["content"] == initial_greeting()


def test_auth_flow_appends_messages():
    app = build_app()
    session = _session_defaults()

    result = app.invoke(
        {
            "user_message": "CUST-1001",
            "session_state": session,
            "assistant_message": "",
        }
    )

    api_messages = to_api_messages(result["session_state"]["messages"])
    assert len(api_messages) == 3
    assert api_messages[0]["content"] == initial_greeting()
    assert api_messages[1] == {"role": "user", "content": "CUST-1001"}
    assert "Alice" in api_messages[2]["content"]
    assert result["session_state"]["verified_customer_id"] == "CUST-1001"


def test_auth_flow_embedded_customer_id():
    app = build_app()
    session = _session_defaults()

    result = app.invoke(
        {
            "user_message": "Hi Jenny! My customer ID is CUST-1001.",
            "session_state": session,
            "assistant_message": "",
        }
    )

    api_messages = to_api_messages(result["session_state"]["messages"])
    assert len(api_messages) == 3
    assert "CUST-1001" in api_messages[1]["content"]
    assert "Alice" in api_messages[2]["content"]
    assert result["session_state"]["verified_customer_id"] == "CUST-1001"


def test_invalid_customer_id_routes_to_bank_agent(monkeypatch):
    app = build_app()
    session = _session_defaults()

    def fake_run_bank_agent(*, session, user_message):
        from langchain_core.messages import AIMessage, HumanMessage

        messages = list(session.get("messages") or [])
        messages.append(HumanMessage(content=user_message))
        reply = "Please provide a valid Customer ID."
        messages.append(AIMessage(content=reply))
        session["messages"] = messages
        return reply

    monkeypatch.setattr("bank_demo.graph.run_bank_agent", fake_run_bank_agent)

    result = app.invoke(
        {
            "user_message": "CUST-9999",
            "session_state": session,
            "assistant_message": "",
        }
    )

    api_messages = to_api_messages(result["session_state"]["messages"])
    assert len(api_messages) == 3
    assert api_messages[1]["content"] == "CUST-9999"
    assert "valid Customer ID" in api_messages[2]["content"]
    assert result["session_state"]["verified_customer_id"] is None
