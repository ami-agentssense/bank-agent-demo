from bank_customer.client import BankRepClient
from bank_customer.messages import ApiMessage
from bank_customer.runner import run_scenario


GREETING = ApiMessage(role="assistant", content="Please provide Customer ID?")


def test_run_scenario_goal_complete_without_post(monkeypatch):
    calls = {"post": 0}

    class FakeClient:
        def health(self) -> bool:
            return True

        def get_messages(self) -> list[ApiMessage]:
            return [GREETING]

        def post_messages(self, messages: list[ApiMessage]) -> list[ApiMessage]:
            calls["post"] += 1
            return [
                *messages,
                ApiMessage(role="assistant", content="Hello Alice"),
            ]

    def fake_agent(*, skill_text, messages):
        return "[GOAL_COMPLETE]"

    monkeypatch.setattr("bank_customer.runner.run_customer_agent", fake_agent)

    result = run_scenario(
        client=FakeClient(),  # type: ignore[arg-type]
        skill_text="skill",
        max_turns=5,
    )

    assert result.success is True
    assert result.turns == 1
    assert calls["post"] == 0


def test_run_scenario_posts_then_completes(monkeypatch):
    class FakeClient:
        def health(self) -> bool:
            return True

        def get_messages(self) -> list[ApiMessage]:
            return [GREETING]

        def post_messages(self, messages: list[ApiMessage]) -> list[ApiMessage]:
            return [
                *messages,
                ApiMessage(role="assistant", content="Balance is $12,500"),
            ]

    replies = ["CUST-1001", "[GOAL_COMPLETE]"]
    monkeypatch.setattr(
        "bank_customer.runner.run_customer_agent",
        lambda **kwargs: replies.pop(0),
    )

    result = run_scenario(
        client=FakeClient(),  # type: ignore[arg-type]
        skill_text="skill",
        max_turns=5,
    )

    assert result.success is True
    assert result.turns == 2
    assert result.messages[-1].content == "Balance is $12,500"


def test_run_scenario_max_turns(monkeypatch):
    class FakeClient:
        def health(self) -> bool:
            return True

        def get_messages(self) -> list[ApiMessage]:
            return [GREETING]

        def post_messages(self, messages: list[ApiMessage]) -> list[ApiMessage]:
            return [
                *messages,
                ApiMessage(role="assistant", content="ok"),
            ]

    monkeypatch.setattr(
        "bank_customer.runner.run_customer_agent",
        lambda **kwargs: "hello",
    )

    result = run_scenario(
        client=FakeClient(),  # type: ignore[arg-type]
        skill_text="skill",
        max_turns=2,
    )

    assert result.success is False
    assert "max turns" in result.reason


def test_run_scenario_rep_unreachable():
    class FakeClient:
        def health(self) -> bool:
            return False

    result = run_scenario(
        client=FakeClient(),  # type: ignore[arg-type]
        skill_text="skill",
        max_turns=5,
    )

    assert result.success is False
    assert "not reachable" in result.reason
