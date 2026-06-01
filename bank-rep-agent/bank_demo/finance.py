from __future__ import annotations

from datetime import date
from decimal import Decimal

from .utils import add_months, floor_div_decimal, q2


def calculate_loan_offer(principal: str, years: int) -> dict:
    principal_d = Decimal(principal)
    rate = Decimal("0.04")
    years_i = int(years)

    total_repayment = q2(principal_d * ((Decimal("1") + rate) ** years_i))
    total_interest = q2(total_repayment - principal_d)
    monthly_payment = q2(total_repayment / (years_i * 12))

    return {
        "principal": str(q2(principal_d)),
        "years": years_i,
        "annual_rate": "0.04",
        "total_repayment": str(total_repayment),
        "total_interest": str(total_interest),
        "monthly_payment": str(monthly_payment),
    }


def calculate_term_deposit(principal: str, balance: str, today: str | None = None) -> dict:
    principal_d = Decimal(principal)
    balance_d = Decimal(balance)
    rate = Decimal("0.03")

    if principal_d <= 0:
        return {"ok": False, "error": "deposit_amount_must_be_positive"}
    if principal_d > balance_d:
        return {"ok": False, "error": "insufficient_balance", "balance": str(q2(balance_d))}

    if today:
        year, month, day = [int(x) for x in today.split("-")]
        today_d: date = date(year, month, day)
    else:
        today_d = date.today()

    return_amount = q2(principal_d * (Decimal("1") + rate))
    interest_earned = q2(return_amount - principal_d)
    maturity_d = add_months(today_d, 12)

    return {
        "ok": True,
        "principal": str(q2(principal_d)),
        "annual_rate": "0.03",
        "return_amount": str(return_amount),
        "interest_earned": str(interest_earned),
        "maturity_date": maturity_d.isoformat(),
    }


def calculate_stock_purchase(shares: int, balance: str, price: str) -> dict:
    shares_i = int(shares)
    balance_d = Decimal(balance)
    price_d = Decimal(price)

    if shares_i <= 0:
        return {"ok": False, "error": "shares_must_be_positive"}

    total_cost = q2(price_d * Decimal(shares_i))
    if total_cost > balance_d:
        affordable = floor_div_decimal(balance_d, price_d)
        return {
            "ok": False,
            "error": "insufficient_balance",
            "total_cost": str(total_cost),
            "balance": str(q2(balance_d)),
            "affordable_shares": affordable,
            "price": str(q2(price_d)),
        }

    return {
        "ok": True,
        "shares": shares_i,
        "price": str(q2(price_d)),
        "total_cost": str(total_cost),
        "new_balance": str(q2(balance_d - total_cost)),
    }
