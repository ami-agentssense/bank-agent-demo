import pytest

from bank_customer.config import SKILLS_DIR
from bank_customer.skills import SkillNotFoundError, list_skills, load_skill, resolve_skill_path


def test_list_skills():
    names = list_skills()
    assert "alice_balance" in names
    assert "david_loan" in names


def test_load_skill_by_name():
    text = load_skill("alice_balance")
    assert "Alice Cohen" in text
    assert "CUST-1001" in text


def test_resolve_skill_path_by_name():
    path = resolve_skill_path("sara_buy_stock")
    assert path.name == "sara_buy_stock.md"
    assert path.is_file()


def test_resolve_skill_path_absolute():
    path = resolve_skill_path(str(SKILLS_DIR / "david_loan.md"))
    assert path.name == "david_loan.md"


def test_missing_skill():
    with pytest.raises(SkillNotFoundError):
        load_skill("does_not_exist")
