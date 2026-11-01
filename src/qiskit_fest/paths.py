"""Locating the repository, challenge folders and (when present) the instructor assets."""
from __future__ import annotations

from pathlib import Path

from .registry import Challenge, get


def _looks_like_repo(path: Path) -> bool:
    return (path / "pyproject.toml").is_file() and (path / "challenges").is_dir() and (path / "src" / "qiskit_fest").is_dir()


def repo_root() -> Path | None:
    """Repository root (works for an editable install and when running from inside the checkout), else ``None``."""
    here = Path(__file__).resolve()
    for candidate in (here.parents[2], *Path.cwd().resolve().parents, Path.cwd().resolve()):
        if _looks_like_repo(candidate):
            return candidate
    return None


def require_repo_root() -> Path:
    root = repo_root()
    if root is None:
        raise RuntimeError(
            "Could not find the qiskit-fall-fest-challenges folder. Open the notebook from inside that folder "
            "(see README.md, section 'Open a challenge') or install the package with `pip install -e .`."
        )
    return root


def challenge_dir(challenge: int | Challenge) -> Path:
    ch = get(challenge) if isinstance(challenge, int) else challenge
    return require_repo_root() / "challenges" / ch.folder


def starter_path(challenge: int | Challenge) -> Path:
    ch = get(challenge) if isinstance(challenge, int) else challenge
    return challenge_dir(ch) / "starter.py"


def public_test_path(challenge: int | Challenge) -> Path:
    ch = get(challenge) if isinstance(challenge, int) else challenge
    return require_repo_root() / "tests" / "public" / f"test_c{ch.number:02d}_public.py"


def instructor_dir() -> Path | None:
    """The ``instructor`` folder, or ``None`` in a participant checkout (where it must not exist)."""
    root = repo_root()
    if root is None:
        return None
    inst = root / "instructor"
    return inst if inst.is_dir() else None


def solution_module_name(challenge: int | Challenge) -> str:
    ch = get(challenge) if isinstance(challenge, int) else challenge
    return f"instructor.solutions.challenge_{ch.number:02d}_solution"
