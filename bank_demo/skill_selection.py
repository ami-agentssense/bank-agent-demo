from __future__ import annotations

from typing import Any

# Keywords (lowercase) that suggest which skill file to attach.
SKILL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "domain_refusal.md": (),  # always included when selective loading is on
    "loan_rules.md": (
        "loan",
        "borrow",
        "borrowing",
        "lend",
        "lending",
        "credit",
        "mortgage",
        "interest rate",
        "repay",
        "repayment",
    ),
    "term_deposit_rules.md": (
        "term deposit",
        "fixed deposit",
        "deposit",
        "savings",
        "save money",
        "saving",
        "cd ",
        "certificate of deposit",
    ),
    "stock_rules.md": (
        "stock",
        "stocks",
        "share",
        "shares",
        "invest",
        "investing",
        "portfolio",
        "ticker",
        "aapl",
        "tsla",
        "googl",
        "amzn",
        "msft",
        "nvda",
        "meta",
        "buy shares",
        "sell shares",
    ),
}

# If the user sends a short follow-up (amount, term, yes/no), keep prior active skills.
_CONTINUATION_PHRASES = frozenset(
    {
        "yes",
        "no",
        "y",
        "n",
        "ok",
        "okay",
        "confirm",
        "confirmed",
        "cancel",
        "proceed",
        "sure",
        "go ahead",
    }
)


def _is_continuation_message(message: str) -> bool:
    text = message.strip().lower()
    if not text:
        return False
    if text in _CONTINUATION_PHRASES:
        return True
    # Mostly digits (loan amount, deposit amount, share count, term years).
    compact = text.replace(",", "").replace("$", "").replace(".", "")
    if compact.isdigit():
        return True
    # "5 years", "10k", "1 year"
    if len(text.split()) <= 4 and any(ch.isdigit() for ch in text):
        return True
    return False


def _match_skills_from_message(message: str) -> set[str]:
    text = message.lower()
    matched: set[str] = {"domain_refusal.md"}

    for filename, keywords in SKILL_KEYWORDS.items():
        if filename == "domain_refusal.md":
            continue
        if any(kw in text for kw in keywords):
            matched.add(filename)

    return matched


def select_skill_files(
    user_message: str,
    session: dict[str, Any] | None,
) -> list[str]:
    """
    Choose which skill markdown files to inject this turn.

    - New topic keywords replace topical skills (keeps domain_refusal).
    - Short follow-ups keep skills from the previous turn.
    """
    if session is None:
        session = {}
    matched = _match_skills_from_message(user_message)
    topical = matched - {"domain_refusal.md"}
    previous = set(session.get("active_skills") or [])

    if topical:
        active = matched
    elif _is_continuation_message(user_message) and previous:
        active = previous | {"domain_refusal.md"}
    else:
        active = {"domain_refusal.md"}

    filenames = sorted(active)
    session["active_skills"] = filenames
    return filenames
