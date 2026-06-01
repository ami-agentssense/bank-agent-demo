import time
from pathlib import Path

from orchestrator.skill_catalog import SkillProfile, build_catalog
from orchestrator.skill_index import (
    SkillIndexEntry,
    entry_is_stale,
    load_index,
    mtime_to_iso,
    profile_from_entry,
    save_index,
)
from orchestrator.skill_index import SkillIndex


def test_entry_is_stale_when_file_newer(tmp_path: Path):
    skill = tmp_path / "demo.md"
    skill.write_text("content", encoding="utf-8")
    mtime = skill.stat().st_mtime
    entry = SkillIndexEntry(
        name="demo",
        source_path="demo.md",
        modified_at=mtime_to_iso(mtime),
        mtime=mtime,
        summary="x",
    )
    time.sleep(0.02)
    skill.write_text("updated", encoding="utf-8")
    assert entry_is_stale(entry, skill) is True


def test_entry_not_stale_when_unchanged(tmp_path: Path):
    skill = tmp_path / "demo.md"
    skill.write_text("content", encoding="utf-8")
    mtime = skill.stat().st_mtime
    entry = SkillIndexEntry(
        name="demo",
        source_path="demo.md",
        modified_at=mtime_to_iso(mtime),
        mtime=mtime,
        summary="x",
    )
    assert entry_is_stale(entry, skill) is False


def test_profile_from_entry_roundtrip():
    entry = SkillIndexEntry(
        name="alice",
        source_path="skills/alice.md",
        modified_at="2026-01-01T00:00:00+00:00",
        mtime=1735689600.0,
        persona="polite",
        goal="balance",
        behavior="concise",
        summary="check balance",
        tone=["polite"],
        services=["balance"],
    )
    profile = profile_from_entry(entry)
    assert profile.name == "alice"
    assert profile.persona == "polite"
