from __future__ import annotations

from decimal import Decimal

from bank_demo.finance import calculate_loan_offer, calculate_term_deposit, calculate_stock_purchase


def test_calculate_loan_offer_1_year():
    out = calculate_loan_offer("1000.00", 1)
    assert out["principal"] == "1000.00"
    assert out["years"] == 1
    # Total repayment = 1000 * 1.04^1 = 1040.00
    assert out["total_repayment"] == "1040.00"
    assert out["total_interest"] == "40.00"
    assert out["monthly_payment"] == "86.67"


def test_calculate_term_deposit():
    out = calculate_term_deposit("1000.00", "2000.00", today="2026-05-27")
    assert out["ok"] is True
    assert out["principal"] == "1000.00"
    assert out["annual_rate"] == "0.03"
    assert out["return_amount"] == "1030.00"
    assert out["interest_earned"] == "30.00"
    # 12-month maturity: 2027-05-27
    assert out["maturity_date"] == "2027-05-27"


def test_calculate_stock_purchase_ok():
    out = calculate_stock_purchase(3, "500.00", "100.00")
    assert out["ok"] is True
    assert out["total_cost"] == "300.00"
    assert out["new_balance"] == "200.00"


def test_calculate_stock_purchase_insufficient():
    out = calculate_stock_purchase(10, "500.00", "100.00")
    assert out["ok"] is False
    assert out["error"] == "insufficient_balance"
    assert out["total_cost"] == "1000.00"
    assert out["balance"] == "500.00"
    assert out["affordable_shares"] == 5

