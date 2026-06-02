from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage
from uuid import UUID

import bank_demo.api as api_module
from bank_demo.api import app
from bank_demo.graph import initial_greeting


def _client() -> TestClient:
    api_module.reset_session_state()
    return TestClient(app)


def test_health():
    response = _client().get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_messages_returns_greeting():
    client = _client()
    response = client.get("/api/v1/messages")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 1
    assert data["messages"][0]["role"] == "assistant"
    assert data["messages"][0]["content"] == initial_greeting()


def test_post_customer_id_returns_menu():
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    response = client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *greeting,
                {"role": "user", "content": "CUST-1001"},
            ]
        },
    )

    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) >= 3
    assert messages[1]["content"] == "CUST-1001"
    assert "Alice" in messages[-1]["content"]


def test_post_requires_last_user_message():
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    response = client.post(
        "/api/v1/messages",
        json={"messages": greeting},
    )

    assert response.status_code == 400
    assert "last message" in response.json()["detail"].lower()


def test_post_logs_turn_to_stdout(capsys):
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *greeting,
                {"role": "user", "content": "CUST-1001"},
            ]
        },
    )

    captured = capsys.readouterr()
    assert "[session_id=" in captured.out
    assert "PROMPTS: USER: CUST-1001" in captured.out
    assert "Alice" in captured.out


def test_reset_session_state_sets_uuid():
    api_module.reset_session_state()
    session_id = api_module._session_state["session_id"]
    assert isinstance(session_id, str)
    assert session_id
    assert str(UUID(session_id)) == session_id
    assert session_id == api_module.SERVER_SESSION_ID


def test_post_logs_silent_when_disabled(monkeypatch, capsys):
    monkeypatch.setenv("API_CONVERSATION_LOG", "false")
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *greeting,
                {"role": "user", "content": "CUST-1001"},
            ]
        },
    )

    captured = capsys.readouterr()
    assert initial_greeting() not in captured.out
    assert "PROMPTS: USER:" not in captured.out


def test_startup_logs_greeting(capsys):
    api_module.reset_session_state()

    captured = capsys.readouterr()
    assert "Apex Bank — Jenny (API)" in captured.out
    assert f"session_id={api_module.SERVER_SESSION_ID}" in captured.out
    assert "PROMPTS:" in captured.out
    assert initial_greeting() in captured.out


def test_greeting_log_silent_when_disabled(monkeypatch, capsys):
    monkeypatch.setenv("API_CONVERSATION_LOG", "false")
    api_module.reset_session_state()

    captured = capsys.readouterr()
    assert initial_greeting() not in captured.out


def test_post_embedded_customer_id_returns_menu():
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    response = client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *greeting,
                {"role": "user", "content": "Hi Jenny! My customer ID is CUST-1001."},
            ]
        },
    )

    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) >= 3
    assert "Alice" in messages[-1]["content"]


def test_banking_turn_after_login(monkeypatch):
    client = _client()
    greeting = client.get("/api/v1/messages").json()["messages"]

    login = client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *greeting,
                {"role": "user", "content": "CUST-1001"},
            ]
        },
    ).json()["messages"]

    def fake_run_bank_agent(*, session, user_message):
        messages = list(session.get("messages") or [])
        messages.append(HumanMessage(content=user_message))
        reply = "Your checking balance is $12,500.00."
        messages.append(AIMessage(content=reply))
        session["messages"] = messages
        return reply

    monkeypatch.setattr("bank_demo.graph.run_bank_agent", fake_run_bank_agent)

    response = client.post(
        "/api/v1/messages",
        json={
            "messages": [
                *login,
                {"role": "user", "content": "What is my balance?"},
            ]
        },
    )

    assert response.status_code == 200
    messages = response.json()["messages"]
    assert messages[-2]["content"] == "What is my balance?"
    assert messages[-1]["role"] == "assistant"
    assert "12,500" in messages[-1]["content"]
