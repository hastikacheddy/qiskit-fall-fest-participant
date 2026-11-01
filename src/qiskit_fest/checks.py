"""Helpers used inside the participant notebooks.

``run_public_checks(n)``   runs the public smoke tests of challenge ``n`` against the functions defined in the notebook
                           and prints a friendly summary (these are *not* the instructors' hidden tests).
``if_ready()``             context manager: skips a block with a hint while a TODO is still unfinished.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import paths, testing
from .loading import ImplProxy
from .registry import get

__all__ = ["run_public_checks", "if_ready", "CheckReport"]


@contextlib.contextmanager
def if_ready(hint: str = "Finish the TODO above to see this result."):
    """Run the block, but turn an unfinished TODO (``NotImplementedError``) into a friendly message."""
    try:
        yield
    except NotImplementedError as exc:
        print(f"[not ready yet] {exc}\n  -> {hint}")


@dataclass
class CheckReport:
    challenge: int
    records: list[dict] = field(default_factory=list)
    exit_code: int = 0

    @property
    def passed(self) -> int:
        return sum(r["outcome"] == "passed" for r in self.records)

    @property
    def failed(self) -> int:
        return sum(r["outcome"] == "failed" and not r.get("todo") for r in self.records)

    @property
    def todo(self) -> int:
        return sum(bool(r.get("todo")) for r in self.records)

    @property
    def skipped(self) -> int:
        return sum(r["outcome"] == "skipped" for r in self.records)

    @property
    def total(self) -> int:
        return len(self.records)

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and self.passed == self.total - self.skipped

    def summary(self) -> str:
        ch = get(self.challenge)
        lines = [f"Challenge {ch.number} - {ch.title}: public checks"]
        if not self.records:
            lines.append("  (no checks matched - nothing was run)")
        groups: dict[str, list[dict]] = {}
        for r in self.records:  # parametrised cases of one check share a description: report them together
            groups.setdefault(r["description"], []).append(r)
        for desc, rs in groups.items():
            suffix = f"  (x{len(rs)} cases)" if len(rs) > 1 else ""
            failed = [r for r in rs if r["outcome"] == "failed" and not r.get("todo")]
            todo = [r for r in rs if r.get("todo")]
            if failed:
                lines.append(f"  [FAIL] {desc}{suffix}\n         {failed[0]['message']}")
            elif todo:
                lines.append(f"  [TODO] {desc}{suffix}\n         {todo[0]['message']}")
            elif all(r["outcome"] == "skipped" for r in rs):
                lines.append(f"  [skip] {desc} ({rs[0]['message']})")
            else:
                lines.append(f"  [PASS] {desc}{suffix}")
        done = f"{self.passed}/{self.total - self.skipped} public checks passed"
        if self.all_passed:
            done += " - nice! The instructors will also run additional hidden tests, so test your own edge cases too."
        lines.append("  " + done)
        return "\n".join(lines)

    def __repr__(self) -> str:
        return self.summary()


def run_public_checks(challenge: int, namespace: dict | None = None, *, keyword: str | None = None,
                      verbose: bool = False) -> CheckReport:
    """Run the public checks of ``challenge`` against the functions in ``namespace`` (default: the caller's globals).

    Usage in a notebook cell:  ``run_public_checks(1, globals())``. Pass ``keyword="born"`` to run only the checks
    whose name contains that text (handy right after finishing one part).
    """
    import pytest

    ch = get(challenge)
    if namespace is None:
        namespace = sys._getframe(1).f_globals  # the notebook's globals
    root = paths.require_repo_root()
    test_file = paths.public_test_path(ch)
    if not test_file.is_file():
        raise FileNotFoundError(f"public tests not found: {test_file}")
    proxy = ImplProxy(namespace, ch, "your notebook")

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "results.json"
        args = [str(test_file), "-q", "--tb=short", "--no-header", "-p", "no:cacheprovider",
                "-c", str(root / "pyproject.toml"), "--rootdir", str(root), f"--results-json={out}"]
        if keyword:
            args += ["-k", keyword]
        testing.OVERRIDE_IMPL = proxy
        buffer = io.StringIO()
        try:
            if verbose:
                code = pytest.main(args)
            else:
                with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                    code = pytest.main(args)
        finally:
            testing.OVERRIDE_IMPL = None
        records = json.loads(out.read_text(encoding="utf8")) if out.exists() else []
    report = CheckReport(challenge=ch.number, records=records, exit_code=int(code))
    print(report.summary())
    return report
