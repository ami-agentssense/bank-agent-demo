from bank_demo.skill_selection import select_skill_files


def test_select_loan_skill():
    session: dict = {}
    files = select_skill_files("I want to apply for a loan", session)
    assert "loan_rules.md" in files
    assert "domain_refusal.md" in files
    assert "stock_rules.md" not in files


def test_select_deposit_skill():
    session: dict = {}
    files = select_skill_files("open a term deposit", session)
    assert "term_deposit_rules.md" in files
    assert "loan_rules.md" not in files


def test_continuation_keeps_loan_skill():
    session: dict = {}
    select_skill_files("I need a loan", session)
    files = select_skill_files("5000", session)
    assert "loan_rules.md" in files


def test_stock_overrides_previous_loan_topic():
    session: dict = {}
    select_skill_files("I need a loan", session)
    files = select_skill_files("what is the price of AAPL", session)
    assert "stock_rules.md" in files
    assert "loan_rules.md" not in files
