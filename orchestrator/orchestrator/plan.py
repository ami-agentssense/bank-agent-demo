from __future__ import annotations

import random
from typing import Literal

from pydantic import BaseModel, Field

from .skill_catalog import SkillCatalog, match_skills


class DistributionBucket(BaseModel):
    criteria: str
    percent: float = Field(ge=0, le=100)


class RunPlanSpec(BaseModel):
    total_sessions: int = Field(default=0, ge=0)
    distribution: list[DistributionBucket] | None = None
    explicit_skills: list[str] | None = None
    needs_clarification: str | None = None


class PlannedSession(BaseModel):
    index: int
    skill: str
    criteria: str
    summary: str


class RunPlan(BaseModel):
    sessions: list[PlannedSession]
    warnings: list[str] = Field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.sessions)


def _allocate_counts(total: int, buckets: list[DistributionBucket]) -> list[int]:
    if not buckets:
        return []
    raw = [total * b.percent / 100.0 for b in buckets]
    counts = [int(x) for x in raw]
    remainder = total - sum(counts)
    fractions = [(i, raw[i] - counts[i]) for i in range(len(buckets))]
    fractions.sort(key=lambda x: x[1], reverse=True)
    for i in range(remainder):
        counts[fractions[i % len(fractions)][0]] += 1
    return counts


def build_plan(
    spec: RunPlanSpec,
    catalog: SkillCatalog,
    *,
    rng: random.Random | None = None,
) -> RunPlan:
    rng = rng or random.Random()
    warnings: list[str] = []

    if spec.explicit_skills:
        sessions: list[PlannedSession] = []
        for i, skill in enumerate(spec.explicit_skills, start=1):
            profile = catalog.get(skill)
            if profile is None:
                warnings.append(f"Unknown skill: {skill}")
                summary = "—"
            else:
                summary = profile.summary
            sessions.append(
                PlannedSession(
                    index=i,
                    skill=skill,
                    criteria="explicit",
                    summary=summary,
                )
            )
        return RunPlan(sessions=sessions, warnings=warnings)

    total = spec.total_sessions
    buckets = spec.distribution
    if not buckets:
        buckets = [DistributionBucket(criteria="random", percent=100.0)]

    percent_sum = sum(b.percent for b in buckets)
    if abs(percent_sum - 100.0) > 0.01:
        warnings.append(f"Distribution percents sum to {percent_sum}, not 100")

    counts = _allocate_counts(total, buckets)
    sessions = []
    idx = 0

    for bucket, count in zip(buckets, counts):
        pool = match_skills(bucket.criteria, catalog)
        if not pool:
            warnings.append(f"No skills match criteria: {bucket.criteria!r}")
            pool = catalog.names()
        for _ in range(count):
            idx += 1
            skill = rng.choice(pool)
            profile = catalog.get(skill)
            sessions.append(
                PlannedSession(
                    index=idx,
                    skill=skill,
                    criteria=bucket.criteria,
                    summary=profile.summary if profile else "—",
                )
            )

    return RunPlan(sessions=sessions, warnings=warnings)


def format_plan(plan: RunPlan) -> str:
    lines = [f"Plan: {plan.total} session(s)"]
    for s in plan.sessions:
        lines.append(f"  {s.index}. {s.skill} ({s.criteria}) — {s.summary}")
    for w in plan.warnings:
        lines.append(f"  ! {w}")
    lines.append("Proceed? (yes/no)")
    return "\n".join(lines)
