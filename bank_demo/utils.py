from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import math


TWOPLACES = Decimal("0.01")


def q2(amount: Decimal) -> Decimal:
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def format_money(amount: Decimal) -> str:
    # Ensure we always show 2 decimals and $ prefix.
    amt = q2(amount)
    return f"${amt:,.2f}"


def safe_int_from_string(text: str) -> int | None:
    try:
        v = int(text.strip())
    except Exception:
        return None
    return v


def parse_decimal(text: str) -> Decimal | None:
    try:
        # Avoid float issues; rely on Decimal parsing.
        cleaned = text.strip().replace(",", "")
        return Decimal(cleaned)
    except Exception:
        return None


def add_months(d: date, months: int) -> date:
    """
    Add calendar months to a date, clamping the day to the last valid day of
    the target month.
    """

    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    # Days in target month
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    last_day = (next_month_first - date(year, month, 1)).days
    day = min(d.day, last_day)
    return date(year, month, day)


def floor_div_decimal(a: Decimal, b: Decimal) -> int:
    if b == 0:
        return 0
    # Decimal doesn't directly floor-div to int; convert carefully.
    return int((a / b).to_integral_value(rounding="ROUND_FLOOR"))


def get_first_name(full_name: str) -> str:
    full_name = full_name.strip()
    if not full_name:
        return full_name
    return full_name.split()[0]

