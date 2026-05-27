from __future__ import annotations

from decimal import Decimal


CUSTOMERS: dict[str, dict] = {
    "CUST-1001": {
        "id": "CUST-1001",
        "name": "Alice Cohen",
        "balance": Decimal("12500.00"),
        "accountStatus": "active",  # "active" | "closed"
        "termDeposits": [],  # populated when customer opens a deposit
        "portfolio": {},  # { "AAPL": 3, "TSLA": 1, ... }
    },
    "CUST-1002": {
        "id": "CUST-1002",
        "name": "David Levi",
        "balance": Decimal("3200.00"),
        "accountStatus": "active",
        "termDeposits": [],
        "portfolio": {},
    },
    "CUST-1003": {
        "id": "CUST-1003",
        "name": "Sara Ben-David",
        "balance": Decimal("47800.00"),
        "accountStatus": "active",
        "termDeposits": [],
        "portfolio": {"AAPL": 2},
    },
}

EXAMPLE_CUSTOMER_ID = "CUST-1001"


def lookup_customer_id(raw: str) -> str | None:
    """Resolve a customer ID case-insensitively to the canonical key in CUSTOMERS."""
    needle = raw.strip().upper()
    if not needle:
        return None
    for key in CUSTOMERS:
        if key.upper() == needle:
            return key
    return None


STOCKS: dict[str, dict] = {
    "AAPL": {"name": "Apple Inc.", "price": Decimal("213.49")},
    "TSLA": {"name": "Tesla Inc.", "price": Decimal("248.50")},
    "GOOGL": {"name": "Alphabet Inc.", "price": Decimal("178.30")},
    "AMZN": {"name": "Amazon.com Inc.", "price": Decimal("195.80")},
    "MSFT": {"name": "Microsoft Corp.", "price": Decimal("422.10")},
    "NVDA": {"name": "NVIDIA Corp.", "price": Decimal("131.38")},
    "META": {"name": "Meta Platforms", "price": Decimal("602.90")},
}

