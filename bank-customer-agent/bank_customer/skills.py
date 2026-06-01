from __future__ import annotations

from pathlib import Path

from .config import SKILLS_DIR


class SkillNotFoundError(Exception):
    pass


def list_skills(skills_dir: Path | None = None) -> list[str]:
    root = skills_dir or SKILLS_DIR
    if not root.is_dir():
        return []
    return sorted(path.stem for path in root.glob("*.md"))


def resolve_skill_path(name_or_path: str, skills_dir: Path | None = None) -> Path:
    root = skills_dir or SKILLS_DIR
    candidate = Path(name_or_path)
    if candidate.is_file():
        return candidate.resolve()

    if candidate.suffix != ".md":
        candidate = root / f"{name_or_path}.md"
    else:
        candidate = root / candidate.name

    if candidate.is_file():
        return candidate.resolve()

    raise SkillNotFoundError(f"Skill not found: {name_or_path}")


def load_skill(name_or_path: str, skills_dir: Path | None = None) -> str:
    path = resolve_skill_path(name_or_path, skills_dir)
    return path.read_text(encoding="utf-8").strip()
