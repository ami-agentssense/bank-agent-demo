from bank_demo.agent import _run_bank_agent_async


async def _run_with_mocks(monkeypatch, session_id: str):
    captured_kwargs: dict = {}

    class DummyAgent:
        async def ainvoke(self, _payload):
            from langchain_core.messages import AIMessage

            return {"messages": [AIMessage(content="ok")]}

    def fake_chat_anthropic(**kwargs):
        captured_kwargs.update(kwargs)
        return object()

    async def fake_get_tools():
        return []

    def fake_create_react_agent(_llm, _tools, prompt):
        assert prompt
        return DummyAgent()

    monkeypatch.setattr("bank_demo.agent.ChatAnthropic", fake_chat_anthropic)
    monkeypatch.setattr("bank_demo.agent.get_frankfurter_mcp_tools_async", fake_get_tools)
    monkeypatch.setattr("bank_demo.agent.create_react_agent", fake_create_react_agent)

    session = {
        "session_id": session_id,
        "customer": {"name": "Alice Cohen"},
        "messages": [],
    }
    await _run_bank_agent_async(session=session, user_message="Hello")
    return captured_kwargs


def test_chat_anthropic_sets_session_header(monkeypatch):
    import asyncio

    kwargs = asyncio.run(_run_with_mocks(monkeypatch, "sid-123"))
    assert kwargs["default_headers"] == {"X-Session-Id": "sid-123"}


def test_chat_anthropic_omits_session_header_when_missing(monkeypatch):
    import asyncio

    kwargs = asyncio.run(_run_with_mocks(monkeypatch, ""))
    assert "default_headers" not in kwargs


async def _run_openai_with_mocks(monkeypatch, session_id: str):
    captured_kwargs: dict = {}

    class DummyAgent:
        async def ainvoke(self, _payload):
            from langchain_core.messages import AIMessage

            return {"messages": [AIMessage(content="ok")]}

    def fake_chat_openai(**kwargs):
        captured_kwargs.update(kwargs)
        return object()

    async def fake_get_tools():
        return []

    def fake_create_react_agent(_llm, _tools, prompt):
        assert prompt
        return DummyAgent()

    monkeypatch.setattr("bank_demo.agent.ChatOpenAI", fake_chat_openai)
    monkeypatch.setattr("bank_demo.agent.get_frankfurter_mcp_tools_async", fake_get_tools)
    monkeypatch.setattr("bank_demo.agent.create_react_agent", fake_create_react_agent)
    monkeypatch.setattr("bank_demo.agent.get_llm_provider", lambda: "openai")

    session = {
        "session_id": session_id,
        "customer": {"name": "Alice Cohen"},
        "messages": [],
    }
    await _run_bank_agent_async(session=session, user_message="Hello")
    return captured_kwargs


def test_chat_openai_sets_session_header(monkeypatch):
    import asyncio

    kwargs = asyncio.run(_run_openai_with_mocks(monkeypatch, "sid-456"))
    assert kwargs["default_headers"] == {"X-Session-Id": "sid-456"}
