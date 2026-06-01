from __future__ import annotations

import os
import re
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass

from .config import (
    get_customer_agent_dir,
    get_customer_conversation_log,
    get_max_turns,
    get_orchestrator_stream_transcript,
    get_orchestrator_stream_turns_only,
    get_rep_pre_customer_delay,
)
from .rep_server import RepServer, start_rep_server


@dataclass
class SessionResult:
    index: int
    skill: str
    success: bool
    reason: str
    turns: int | None
    duration_sec: float
    output_tail: str


def _tail(text: str, lines: int = 20) -> str:
    parts = text.strip().splitlines()
    return "\n".join(parts[-lines:])


def _parse_turns(output: str) -> int | None:
    match = re.search(r"Done in (\d+) turn", output)
    if match:
        return int(match.group(1))
    match = re.search(r"Failed after (\d+) turn", output)
    if match:
        return int(match.group(1))
    return None


def _parse_reason(output: str, exit_code: int) -> str:
    if "goal complete" in output.lower():
        return "goal complete"
    if "max turns" in output.lower():
        return "max turns"
    if "not reachable" in output.lower():
        return "bank rep API not reachable"
    if exit_code == 0:
        return "ok"
    return "failed"


def _should_stream_line(line: str, *, turns_only: bool) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if not turns_only:
        return True
    return (
        stripped.startswith("--- turn ")
        or stripped.startswith("CUSTOMER:")
        or stripped.startswith("BANK:")
        or stripped.startswith("Done in ")
        or stripped.startswith("Failed after ")
    )


def _run_customer_process(
    *,
    customer_dir: str,
    env: dict[str, str],
    skill: str,
    max_turns: int,
    on_line: Callable[[str], None] | None,
    stream: bool,
    turns_only: bool,
) -> tuple[str, int]:
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            "main.py",
            "--skill",
            skill,
            "--max-turns",
            str(max_turns),
        ],
        cwd=customer_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    chunks: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        chunks.append(line)
        if stream and on_line is not None and _should_stream_line(line.rstrip("\n"), turns_only=turns_only):
            on_line(line.rstrip("\n"))
    returncode = proc.wait()
    return "".join(chunks), returncode


def run_session(
    *,
    index: int,
    skill: str,
    on_line: Callable[[str], None] | None = None,
) -> SessionResult:
    started = time.monotonic()
    rep: RepServer | None = None
    stream = get_orchestrator_stream_transcript()
    turns_only = get_orchestrator_stream_turns_only()
    try:
        rep = start_rep_server()
        time.sleep(get_rep_pre_customer_delay())

        customer_dir = get_customer_agent_dir()
        env = os.environ.copy()
        env["CUSTOMER_CONVERSATION_LOG"] = "true" if get_customer_conversation_log() else "false"

        combined, returncode = _run_customer_process(
            customer_dir=str(customer_dir),
            env=env,
            skill=skill,
            max_turns=get_max_turns(),
            on_line=on_line,
            stream=stream,
            turns_only=turns_only,
        )
        turns = _parse_turns(combined)
        reason = _parse_reason(combined, returncode)
        success = returncode == 0
        return SessionResult(
            index=index,
            skill=skill,
            success=success,
            reason=reason,
            turns=turns,
            duration_sec=time.monotonic() - started,
            output_tail=_tail(combined),
        )
    except Exception as exc:
        return SessionResult(
            index=index,
            skill=skill,
            success=False,
            reason=str(exc),
            turns=None,
            duration_sec=time.monotonic() - started,
            output_tail="",
        )
    finally:
        if rep is not None:
            rep.stop()
