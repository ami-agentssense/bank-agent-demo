import subprocess
from io import StringIO
from unittest.mock import MagicMock, patch

from orchestrator.session_runner import (
    _parse_reason,
    _parse_turns,
    _should_stream_line,
    run_session,
)


def test_parse_turns():
    assert _parse_turns("Done in 3 turn(s).") == 3
    assert _parse_turns("Failed after 12 turns") == 12
    assert _parse_turns("no info") is None


def test_parse_reason():
    assert _parse_reason("Goal complete!", 0) == "goal complete"
    assert _parse_reason("max turns reached", 1) == "max turns"
    assert _parse_reason("", 1) == "failed"


def test_should_stream_line_turns_only():
    assert _should_stream_line("--- turn 1 ---", turns_only=True)
    assert _should_stream_line("CUSTOMER: hi", turns_only=True)
    assert not _should_stream_line("Skill: alice", turns_only=True)
    assert _should_stream_line("Skill: alice", turns_only=False)


def test_run_session_success():
    mock_rep = MagicMock()
    output = "--- turn 1 ---\nCUSTOMER: hi\nBANK: hello\nDone in 2 turn(s): goal complete\n"

    mock_proc = MagicMock()
    mock_proc.stdout = StringIO(output)
    mock_proc.wait.return_value = 0

    lines: list[str] = []

    with (
        patch("orchestrator.session_runner.start_rep_server", return_value=mock_rep),
        patch("orchestrator.session_runner.time.sleep"),
        patch("orchestrator.session_runner.subprocess.Popen", return_value=mock_proc),
        patch("orchestrator.session_runner.get_customer_agent_dir"),
        patch("orchestrator.session_runner.get_max_turns", return_value=30),
        patch("orchestrator.session_runner.get_customer_conversation_log", return_value=True),
        patch("orchestrator.session_runner.get_rep_pre_customer_delay", return_value=0),
        patch("orchestrator.session_runner.get_orchestrator_stream_transcript", return_value=True),
        patch("orchestrator.session_runner.get_orchestrator_stream_turns_only", return_value=True),
    ):
        result = run_session(
            index=1,
            skill="alice_balance",
            on_line=lines.append,
        )

    assert result.success is True
    assert result.turns == 2
    assert any("CUSTOMER:" in line for line in lines)
    assert not any("Skill:" in line for line in lines)
    mock_rep.stop.assert_called_once()
