from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from .config import REPO_ROOT

INDEX_VERSION = 1


class SkillIndexEntry(BaseModel):
    name: str
    source_path: str
    modified_at: str
    mtime: float
    persona: str = ""
    goal: str = ""
    behavior: str = ""
    summary: str = ""
    tone: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    traits: list[str] = Field(default_factory=list)


class SkillIndex(BaseModel):
    version: int = INDEX_VERSION
    skills: dict[str, SkillIndexEntry] = Field(default_factory=dict)


def mtime_to_iso(mtime: float) -> str:
    return datetime.fromtimestamp(mtime, tz=UTC).isoformat()


def relative_source_path(skill_path: Path) -> str:
    resolved = skill_path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_index(path: Path) -> SkillIndex | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        index = SkillIndex.model_validate(data)
        if index.version != INDEX_VERSION:
            return None
        return index
    except (json.JSONDecodeError, ValueError, OSError):
        return None


def save_index(path: Path, index: SkillIndex) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = index.model_dump()
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def entry_is_stale(entry: SkillIndexEntry, skill_path: Path) -> bool:
    if not skill_path.is_file():
        return True
    try:
        file_mtime = skill_path.stat().st_mtime
    except OSError:
        return True
    return file_mtime > entry.mtime


def entry_from_profile(skill_path: Path, profile) -> SkillIndexEntry:
    mtime = skill_path.stat().st_mtime
    return SkillIndexEntry(
        name=profile.name,
        source_path=relative_source_path(skill_path),
        modified_at=mtime_to_iso(mtime),
        mtime=mtime,
        persona=profile.persona,
        goal=profile.goal,
        behavior=profile.behavior,
        summary=profile.summary,
        tone=list(profile.tone),
        services=list(profile.services),
        traits=list(profile.traits),
    )


def profile_from_entry(entry: SkillIndexEntry):
    from .skill_catalog import SkillProfile

    return SkillProfile(
        name=entry.name,
        persona=entry.persona,
        goal=entry.goal,
        behavior=entry.behavior,
        summary=entry.summary,
        tone=list(entry.tone),
        services=list(entry.services),
        traits=list(entry.traits),
    )
