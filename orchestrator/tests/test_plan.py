import random

from orchestrator.plan import DistributionBucket, RunPlanSpec, build_plan, format_plan
from orchestrator.skill_catalog import SkillCatalog, SkillProfile


def _catalog() -> SkillCatalog:
    return SkillCatalog(
        profiles=[
            SkillProfile(name="alice_balance", summary="Check balance", tone=["polite"], services=["balance"]),
            SkillProfile(name="carl_angry", summary="Angry customer", tone=["angry"], services=["balance"]),
            SkillProfile(name="david_loan", summary="Loan inquiry", tone=["neutral"], services=["loan"]),
        ]
    )


def test_build_plan_random_distribution():
    spec = RunPlanSpec(
        total_sessions=10,
        distribution=[DistributionBucket(criteria="random", percent=100.0)],
    )
    plan = build_plan(spec, _catalog(), rng=random.Random(42))
    assert plan.total == 10
    assert all(s.skill in _catalog().names() for s in plan.sessions)


def test_build_plan_weighted_allocation():
    spec = RunPlanSpec(
        total_sessions=10,
        distribution=[
            DistributionBucket(criteria="angry", percent=30.0),
            DistributionBucket(criteria="loan", percent=20.0),
            DistributionBucket(criteria="random", percent=50.0),
        ],
    )
    plan = build_plan(spec, _catalog(), rng=random.Random(0))
    assert plan.total == 10
    angry = [s for s in plan.sessions if s.criteria == "angry"]
    loan = [s for s in plan.sessions if s.criteria == "loan"]
    assert len(angry) == 3
    assert len(loan) == 2


def test_explicit_skills():
    spec = RunPlanSpec(explicit_skills=["alice_balance", "david_loan"])
    plan = build_plan(spec, _catalog())
    assert [s.skill for s in plan.sessions] == ["alice_balance", "david_loan"]


def test_format_plan_includes_proceed():
    spec = RunPlanSpec(total_sessions=2)
    plan = build_plan(spec, _catalog(), rng=random.Random(1))
    text = format_plan(plan)
    assert "Proceed? (yes/no)" in text
    assert "Plan: 2 session(s)" in text
