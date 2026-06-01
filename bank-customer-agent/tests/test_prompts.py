from bank_customer.agent import split_goal_complete
from bank_customer.evaluator import goal_complete_in_message
from bank_customer.messages import GOAL_COMPLETE_SENTINEL
from bank_customer.prompts import build_customer_system_prompt, format_conversation_for_llm


def test_build_customer_system_prompt_includes_skill():
    prompt = build_customer_system_prompt("# Goal\nCheck balance")
    assert "Check balance" in prompt
    assert GOAL_COMPLETE_SENTINEL in prompt


def test_format_conversation_for_llm():
    text = format_conversation_for_llm(
        [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "CUST-1001"},
        ]
    )
    assert "Jenny: Hello" in text
    assert "You: CUST-1001" in text


def test_split_goal_complete():
    cleaned, done = split_goal_complete(f"Thanks! {GOAL_COMPLETE_SENTINEL}")
    assert done is True
    assert cleaned == "Thanks!"


def test_goal_complete_sentinel_only():
    cleaned, done = split_goal_complete(GOAL_COMPLETE_SENTINEL)
    assert done is True
    assert cleaned == ""


def test_goal_complete_in_message():
    assert goal_complete_in_message(f"done {GOAL_COMPLETE_SENTINEL}") is True
    assert goal_complete_in_message("hello") is False
