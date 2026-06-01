from pathlib import Path

from orchestrator.skill_catalog import (
    SkillCatalog,
    SkillProfile,
    build_catalog,
    list_skill_files,
    load_skill_text,
    match_skills,
)


def test_list_skill_files_finds_md(tmp_path: Path):
    (tmp_path / "alice.md").write_text("# Alice\n", encoding="utf-8")
    (tmp_path / "readme.txt").write_text("skip", encoding="utf-8")
    files = list_skill_files(tmp_path)
    assert len(files) == 1
    assert files[0].stem == "alice"


def test_match_skills_angry_and_random():
    catalog = SkillCatalog(
        profiles=[
            SkillProfile(
                name="a",
                summary="x",
                persona="angry user",
                tone=["angry"],
                services=["balance"],
            ),
            SkillProfile(name="b", summary="y", tone=["polite"], services=["loan"]),
        ]
    )
    assert match_skills("random", catalog) == ["a", "b"]
    assert "a" in match_skills("angry", catalog)
    assert match_skills("loan", catalog) == ["b"]


def test_build_catalog_uses_disk_index_without_llm(monkeypatch, tmp_path: Path):
    skill = tmp_path / "demo.md"
    skill.write_text(
        "## Customer Details\nDemo\n## Goal\nTest\n## Behavior\nPolite\n",
        encoding="utf-8",
    )
    index_path = tmp_path / ".skill_index.json"

    def fake_classify(items):
        return [
            SkillProfile(
                name=items[0][0],
                summary="Demo skill",
                persona="demo persona",
                goal="demo goal",
                behavior="demo behavior",
                tone=["polite"],
            )
        ]

    monkeypatch.setattr("orchestrator.skill_catalog._classify_batch", fake_classify)

    cat1, stats1 = build_catalog(skills_dir=tmp_path, index_path=index_path, force=True)
    assert len(cat1.profiles) == 1
    assert stats1.updated == 1
    assert index_path.is_file()

    cat2, stats2 = build_catalog(skills_dir=tmp_path, index_path=index_path)
    assert len(cat2.profiles) == 1
    assert stats2.updated == 0
    assert stats2.cached == 1


def test_build_catalog_reclassifies_stale_file(monkeypatch, tmp_path: Path):
    import time

    skill = tmp_path / "demo.md"
    skill.write_text("v1", encoding="utf-8")
    index_path = tmp_path / ".skill_index.json"
    calls = {"n": 0}

    def fake_classify(items):
        calls["n"] += 1
        return [
            SkillProfile(
                name=items[0][0],
                summary=f"summary {calls['n']}",
                tone=["polite"],
            )
        ]

    monkeypatch.setattr("orchestrator.skill_catalog._classify_batch", fake_classify)
    build_catalog(skills_dir=tmp_path, index_path=index_path, force=True)
    time.sleep(0.02)
    skill.write_text("v2", encoding="utf-8")

    messages: list[str] = []
    cat, stats = build_catalog(
        skills_dir=tmp_path,
        index_path=index_path,
        on_status=messages.append,
    )
    assert stats.updated == 1
    assert any("Updated skill: demo" in m for m in messages)
    assert cat.profiles[0].summary == "summary 2"


def test_load_skill_text(tmp_path: Path):
    p = tmp_path / "x.md"
    p.write_text("  hello  \n", encoding="utf-8")
    assert load_skill_text(p) == "hello"
