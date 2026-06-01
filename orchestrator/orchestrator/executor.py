from __future__ import annotations

from collections.abc import Callable

from .config import get_long_turn_threshold
from .plan import RunPlan
from .session_runner import SessionResult, run_session


def execute_plan(
    plan: RunPlan,
    *,
    on_progress: Callable[[str], None] | None = None,
    on_session_line: Callable[[str], None] | None = None,
) -> tuple[list[SessionResult], list[str]]:
    results: list[SessionResult] = []
    unexpected: list[str] = []
    threshold = get_long_turn_threshold()

    for session in plan.sessions:
        prefix = f"[#{session.index} {session.skill}]"

        def line_callback(line: str, *, p: str = prefix) -> None:
            if on_session_line is not None:
                on_session_line(f"{p} {line}")

        if on_progress is not None:
            on_progress(
                f"Session {session.index}/{plan.total} {session.skill} … running"
            )

        result = run_session(
            index=session.index,
            skill=session.skill,
            on_line=line_callback if on_session_line is not None else None,
        )
        results.append(result)

        if result.turns is not None and result.turns > threshold:
            unexpected.append(
                f"#{result.index} {result.skill}: {result.turns} turns (>{threshold})"
            )
        if result.success and "error" in result.output_tail.lower():
            unexpected.append(f"#{result.index} {result.skill}: success but output mentions errors")

        if on_progress is not None:
            status = "ok" if result.success else "failed"
            turns = f" ({result.turns} turns)" if result.turns else ""
            on_progress(
                f"Session {result.index}/{plan.total} {result.skill} … {status}{turns}"
            )

    return results, unexpected


def format_batch_report(
    results: list[SessionResult],
    unexpected: list[str],
) -> str:
    ok = sum(1 for r in results if r.success)
    failed = len(results) - ok
    lines = [f"Sessions: {len(results)} | OK: {ok} | Failed: {failed}"]

    for r in results:
        if not r.success:
            turns = f" ({r.turns} turns)" if r.turns else ""
            lines.append(f"- #{r.index} {r.skill}: {r.reason}{turns}")

    if unexpected:
        lines.append("Unexpected:")
        for item in unexpected:
            lines.append(f"- {item}")

    return "\n".join(lines)
