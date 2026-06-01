from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from .config import get_anthropic_api_key, get_claude_model, get_skill_index_path, get_skills_dir
from .skill_index import (
    SkillIndex,
    entry_from_profile,
    entry_is_stale,
    load_index,
    profile_from_entry,
    save_index,
)


class SkillProfile(BaseModel):
    name: str
    persona: str = Field(default="", description="Short persona from Customer Details")
    goal: str = Field(default="", description="Short goal from Goal section")
    behavior: str = Field(default="", description="Short behavior from Behavior section")
    summary: str = Field(description="One line: what this customer does in the scenario")
    tone: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)


class SkillCatalog(BaseModel):
    profiles: list[SkillProfile] = Field(default_factory=list)

    def names(self) -> list[str]:
        return [p.name for p in self.profiles]

    def get(self, name: str) -> SkillProfile | None:
        for profile in self.profiles:
            if profile.name == name:
                return profile
        return None

    def summary_text(self) -> str:
        lines = []
        for p in self.profiles:
            tone = ", ".join(p.tone) if p.tone else "neutral"
            services = ", ".join(p.services) if p.services else "—"
            persona = p.persona or "—"
            goal = p.goal or "—"
            lines.append(
                f"- {p.name}: {p.summary} | persona={persona} | goal={goal} | "
                f"tone={tone} | services={services}"
            )
        return "\n".join(lines)


class ClassificationBatch(BaseModel):
    skills: list[SkillProfile]


@dataclass
class CatalogBuildStats:
    total: int
    updated: int
    cached: int


def list_skill_files(skills_dir: Path | None = None) -> list[Path]:
    root = skills_dir or get_skills_dir()
    if not root.is_dir():
        return []
    return sorted(root.glob("*.md"))


def load_skill_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _classify_batch(items: list[tuple[str, str]]) -> list[SkillProfile]:
    payload = [
        {"name": name, "content": text[:4000]}
        for name, text in items
    ]
    system = (
        "You classify bank customer simulation skill files. "
        "Read each skill's Customer Details, Goal, and Behavior sections. "
        "Do not rely on the filename. Return one profile per skill.\n"
        "For each skill provide:\n"
        "- persona: one short line from Customer Details\n"
        "- goal: one short line from Goal\n"
        "- behavior: one short line from Behavior\n"
        "- summary: one line combining the scenario\n"
        "Use lowercase tags.\n"
        "tone examples: angry, frustrated, polite, confused, neutral, rushed\n"
        "services examples: balance, loan, stock, currency, term_deposit, close_account\n"
        "traits examples: forgot_id, hangs_up, disputes_balance, multi_step, flirty"
    )
    human = f"Classify these skills as JSON matching the schema:\n{json.dumps(payload, indent=2)}"

    llm = ChatAnthropic(
        api_key=get_anthropic_api_key(),
        model=get_claude_model(),
        max_tokens=4096,
    )
    structured = llm.with_structured_output(ClassificationBatch)
    result: ClassificationBatch = structured.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=human),
        ]
    )
    return result.skills


def classify_skill(name: str, text: str) -> SkillProfile:
    profiles = _classify_batch([(name, text)])
    if profiles:
        return profiles[0]
    return SkillProfile(
        name=name,
        summary="Unknown skill",
        tone=["neutral"],
    )


def build_catalog(
    *,
    skills_dir: Path | None = None,
    index_path: Path | None = None,
    force: bool = False,
    on_status: Callable[[str], None] | None = None,
) -> tuple[SkillCatalog, CatalogBuildStats]:
    root = skills_dir or get_skills_dir()
    index_file = index_path or get_skill_index_path()
    paths = list_skill_files(root)

    index = SkillIndex() if force else (load_index(index_file) or SkillIndex())
    if force:
        index.skills.clear()

    to_classify: list[tuple[str, str, Path]] = []
    profiles: list[SkillProfile] = []
    updated = 0
    cached = 0

    current_names: set[str] = set()

    for path in paths:
        name = path.stem
        current_names.add(name)
        entry = index.skills.get(name)

        if not force and entry is not None and not entry_is_stale(entry, path):
            profiles.append(profile_from_entry(entry))
            cached += 1
            continue

        text = load_skill_text(path)
        to_classify.append((name, text, path))

    if to_classify:
        batch_input = [(name, text) for name, text, _ in to_classify]
        if len(batch_input) == 1:
            classified = [classify_skill(batch_input[0][0], batch_input[0][1])]
        else:
            classified = _classify_batch(batch_input)

        by_name = {p.name: p for p in classified}
        for name, text, path in to_classify:
            profile = by_name.get(name) or classify_skill(name, text)
            profile.name = name
            index.skills[name] = entry_from_profile(path, profile)
            profiles.append(profile)
            updated += 1
            if on_status is not None:
                on_status(f"Updated skill: {name}")

    for stale_name in set(index.skills) - current_names:
        del index.skills[stale_name]

    save_index(index_file, index)

    profiles.sort(key=lambda p: p.name)
    total = len(profiles)
    stats = CatalogBuildStats(total=total, updated=updated, cached=cached)

    if on_status is not None:
        on_status(
            f"Loaded {total} skill(s) ({updated} updated, {cached} from index)."
        )

    return SkillCatalog(profiles=profiles), stats


def match_skills(criteria: str, catalog: SkillCatalog) -> list[str]:
    needle = criteria.strip().lower()
    if needle in {"random", "any", "all"}:
        return catalog.names()

    tokens = [t for t in needle.replace(",", " ").split() if t]
    matched: list[str] = []
    for profile in catalog.profiles:
        haystack = " ".join(
            [
                profile.summary.lower(),
                profile.persona.lower(),
                profile.goal.lower(),
                profile.behavior.lower(),
                " ".join(profile.tone).lower(),
                " ".join(profile.services).lower(),
                " ".join(profile.traits).lower(),
            ]
        )
        if any(token in haystack for token in tokens):
            matched.append(profile.name)
            continue
        if "angry" in tokens and any(t in profile.tone for t in ("angry", "frustrated")):
            matched.append(profile.name)
    return sorted(set(matched))
