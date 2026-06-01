from __future__ import annotations

import argparse
import sys

from .client import BankRepClient
from .config import (
    SKILLS_DIR,
    anthropic_key_error_message,
    get_anthropic_api_key,
    get_bank_rep_base_url,
    get_max_turns,
    load_env,
)
from .runner import run_scenario
from .skills import SkillNotFoundError, list_skills, load_skill


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Autonomous bank customer agent (talks to bank-rep-agent via REST)",
    )
    parser.add_argument(
        "--skill",
        help="Skill name (e.g. alice_balance) or path to a skill markdown file",
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="List available skills and exit",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Override MAX_TURNS from .env",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override BANK_REP_BASE_URL from .env",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    load_env()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_skills:
        names = list_skills()
        if not names:
            print(f"No skills found in {SKILLS_DIR}")
            return 1
        for name in names:
            print(name)
        return 0

    if not args.skill:
        parser.error("--skill is required (or use --list-skills)")

    if get_anthropic_api_key() is None:
        print(anthropic_key_error_message(), file=sys.stderr)
        return 1

    try:
        skill_text = load_skill(args.skill)
    except SkillNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    base_url = args.base_url or get_bank_rep_base_url()
    max_turns = args.max_turns or get_max_turns()
    client = BankRepClient(base_url)

    print(f"Skill: {args.skill}", flush=True)
    print(f"Bank rep: {base_url}", flush=True)
    print(flush=True)

    result = run_scenario(
        client=client,
        skill_text=skill_text,
        max_turns=max_turns,
    )

    if result.success:
        print(f"Done in {result.turns} turn(s): {result.reason}")
        return 0

    print(f"Failed after {result.turns} turn(s): {result.reason}", file=sys.stderr)
    return 1
