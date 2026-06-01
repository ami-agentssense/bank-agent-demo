from __future__ import annotations

import copy
from decimal import Decimal
from typing import Any

from langchain_core.tools import BaseTool, tool

from .mock_data import CUSTOMERS, STOCKS, lookup_customer_id
from .utils import floor_div_decimal, format_customer_menu, format_money, get_first_name, q2


def _format_balance_summary(customer: dict[str, Any]) -> str:
    if customer.get("accountStatus") == "closed":
        return "Your account has been closed. No balance information is available."

    balance = Decimal(customer["balance"])
    parts = [f"Your current account balance is {format_money(balance)}."]

    deposits = customer.get("termDeposits") or []
    if deposits:
        dep = deposits[0]
        parts.append(
            f"You also have an active 12-month term deposit of {format_money(Decimal(dep['principal']))} "
            f"maturing on {dep['maturity_date']}."
        )

    portfolio = customer.get("portfolio") or {}
    if portfolio:
        ticker = next(iter(portfolio.keys()))
        shares = portfolio[ticker]
        if len(portfolio) == 1:
            parts.append(f"You hold {shares} shares of {ticker}.")
        else:
            holdings = ", ".join(f"{k}:{v}" for k, v in portfolio.items())
            parts.append(f"Stock portfolio: {holdings}.")

    return " ".join(parts)


def make_customer_lookup_tool(session: dict[str, Any]) -> BaseTool:
    @tool
    def lookup_customer(customer_id: str) -> str:
        """
        Look up and verify a customer by Customer ID.

        Pass the ID (e.g. CUST-1001) or any message text that contains it.
        Call this when the customer provides their Customer ID.
        """
        if session.get("verified_customer_id") is not None:
            customer = session["customer"]
            first_name = get_first_name(customer["name"])
            return f"Customer already verified as {first_name} ({customer['id']})."

        resolved = lookup_customer_id(customer_id)
        if resolved is None:
            return (
                "No account found for that Customer ID. "
                "Ask the customer to double-check (for example: CUST-1001)."
            )

        session["verified_customer_id"] = resolved
        session["customer"] = copy.deepcopy(CUSTOMERS[resolved])
        session["menu_sent"] = True
        session["active_skills"] = []
        first_name = get_first_name(session["customer"]["name"])
        return (
            f"Customer verified: {session['customer']['name']} ({resolved}). "
            f"Welcome them and share this menu:\n{format_customer_menu(first_name)}"
        )

    return lookup_customer


def make_banking_tools(customer: dict[str, Any]) -> list[BaseTool]:
    """
    Session-scoped tools the LLM calls directly (via ReAct agent).
    """

    @tool
    def get_account_balance() -> str:
        """Get the verified customer's account balance, term deposits, and stock holdings."""
        return _format_balance_summary(customer)

    @tool
    def get_stock_quote(ticker: str) -> str:
        """Look up the current price for a stock ticker (e.g. AAPL, TSLA, GOOGL)."""
        t = ticker.strip().upper()
        if t not in STOCKS:
            known = ", ".join(STOCKS.keys())
            return (
                f"I'm sorry, I don't have pricing information for that stock. "
                f"I can look up: {known}."
            )
        info = STOCKS[t]
        price = q2(Decimal(info["price"]))
        return (
            f"{info['name']} ({t}) is currently trading at {format_money(price)} per share. "
            "Would you like to buy shares?"
        )

    @tool
    def buy_stocks(ticker: str, shares: int, customer_confirmed: bool = False) -> str:
        """
        Buy shares of a stock for the verified customer.

        Set customer_confirmed=True only after the customer explicitly says yes to proceed.
        If customer_confirmed is False, returns cost details and asks for confirmation.
        """
        t = ticker.strip().upper()
        if t not in STOCKS:
            known = ", ".join(STOCKS.keys())
            return f"Unknown ticker. Available: {known}."

        if customer.get("accountStatus") == "closed":
            return "Your account is closed. Stock purchases are not available."

        shares_i = int(shares)
        if shares_i <= 0:
            return "Number of shares must be a positive integer."

        price_d = q2(Decimal(STOCKS[t]["price"]))
        balance_d = q2(Decimal(customer["balance"]))
        total_cost = q2(price_d * Decimal(shares_i))

        if total_cost > balance_d:
            affordable = floor_div_decimal(balance_d, price_d)
            return (
                f"Unfortunately, {format_money(total_cost)} exceeds your current balance of "
                f"{format_money(balance_d)}. You can afford up to {affordable} share(s) at the current price."
            )

        if not customer_confirmed:
            new_balance = q2(balance_d - total_cost)
            return (
                f"To confirm: you'd like to buy {shares_i} share(s) of {t} at {format_money(price_d)}/share "
                f"for a total of {format_money(total_cost)}. This will reduce your balance from "
                f"{format_money(balance_d)} to {format_money(new_balance)}. "
                "Ask the customer to confirm, then call buy_stocks again with customer_confirmed=True."
            )

        customer["balance"] = q2(balance_d - total_cost)
        portfolio = customer.setdefault("portfolio", {})
        portfolio[t] = int(portfolio.get(t, 0)) + shares_i
        remaining = Decimal(customer["balance"])
        return (
            f"Done! You now own {shares_i} share(s) of {t}. "
            f"Your remaining balance is {format_money(remaining)}."
        )

    @tool
    def close_account(customer_confirmed: bool = False) -> str:
        """
        Permanently close the verified customer's account.

        Set customer_confirmed=True only after the customer explicitly confirms they want to close.
        """
        if customer.get("accountStatus") == "closed":
            return "Our records show that your account has already been closed."

        if not customer_confirmed:
            return (
                "Account closure is permanent and cannot be undone. "
                "Ask the customer: 'Are you sure you want to proceed?' "
                "If they say yes, call close_account again with customer_confirmed=True."
            )

        old_balance = q2(Decimal(customer["balance"]))
        customer["accountStatus"] = "closed"
        customer["balance"] = Decimal("0.00")
        return (
            "Your account has been successfully closed. We're sorry to see you go. "
            f"Your remaining balance of {format_money(old_balance)} will be mailed to your registered "
            "address within 5–7 business days. Thank you for banking with us."
        )

    return [get_account_balance, get_stock_quote, buy_stocks, close_account]
