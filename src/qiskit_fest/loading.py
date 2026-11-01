"""Loading the implementation under test: reference solution, starter file, participant ``.py`` or notebook.

``ImplProxy`` wraps whatever was loaded so that

* a missing function produces a clear failure ("your solution does not define ...") instead of an ``AttributeError``;
* a function that still raises ``NotImplementedError`` (an unfinished TODO) is reported as "TODO not implemented".

SECURITY NOTE: loading a participant file or notebook *executes its code*. Only grade submissions inside a sandbox
(container / separate machine, no credentials, with a time limit). See instructor/validation_guide.md.
"""
from __future__ import annotations

import functools
import hashlib
import importlib
import importlib.util
import json
import os
import re
import sys
import types
from pathlib import Path
from typing import Any, Mapping

from .registry import Challenge, get

SKIP_TAG = "skip-grading"


class ImplementationError(AssertionError):
    """The implementation under test is missing something it must provide."""


class TodoNotImplemented(ImplementationError):
    """A TODO function was called but still raises NotImplementedError."""


class ImplProxy:
    """Attribute access to the functions of an implementation (a module, a namespace dict or an object)."""

    def __init__(self, source: Any, challenge: Challenge, label: str = "implementation", load_errors: list | None = None):
        self._source = source
        self._challenge = challenge
        self._label = label
        self.load_errors = load_errors or []

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<ImplProxy challenge={self._challenge.number} source={self._label}>"

    def _lookup(self, name: str):
        src = self._source
        if isinstance(src, Mapping):
            return src[name]
        return getattr(src, name)

    def has(self, name: str) -> bool:
        try:
            self._lookup(name)
            return True
        except (KeyError, AttributeError):
            return False

    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError(name)
        try:
            obj = self._lookup(name)
        except (KeyError, AttributeError):
            raise ImplementationError(
                f"Your solution does not define `{name}`. Define it with exactly this name (see the function contract)."
            ) from None
        if callable(obj) and not isinstance(obj, type):
            return _wrap(name, obj)
        return obj


def _wrap(name: str, func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotImplementedError as exc:
            raise TodoNotImplemented(f"TODO not implemented: {name}() ({exc})") from None

    return wrapper


# ------------------------------------------------------------------------------------------------------------------
def _unique_module_name(path: Path) -> str:
    return "fest_submission_" + hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:10]


def load_py(path: str | Path) -> types.ModuleType:
    """Import a ``.py`` file as a fresh module."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    name = _unique_module_name(path)
    sys.modules.pop(name, None)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses & friends look the module up by name
    spec.loader.exec_module(module)
    return module


_MAGIC = re.compile(r"^\s*(%|!)")


def _cell_source(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def load_notebook(path: str | Path) -> tuple[dict, list[tuple[int, str]]]:
    """Execute the code cells of a notebook (except cells tagged ``skip-grading``) in one fresh namespace.

    Errors in individual cells do not stop the loading: they are returned as ``(cell_index, message)`` so that
    functions defined in later cells are still available. Lines starting with ``%`` or ``!`` are dropped.
    Returns ``(namespace, errors)``.
    """
    path = Path(path)
    nb = json.loads(path.read_text(encoding="utf8"))
    os.environ.setdefault("MPLBACKEND", "Agg")
    ns: dict[str, Any] = {"__name__": "fest_notebook", "__file__": str(path)}
    try:
        from IPython.display import display as _display  # type: ignore

        ns["display"] = _display
    except Exception:  # IPython is optional here
        ns["display"] = lambda *a, **k: None
    # The setup cell of every notebook is tagged skip-grading (it runs pip), but it is also where these two names come from:
    # without them every demo cell that says `with if_ready():` would fail on load and be reported as a broken cell.
    from .checks import if_ready, run_public_checks

    ns["if_ready"] = if_ready
    ns["run_public_checks"] = run_public_checks
    errors: list[tuple[int, str]] = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        tags = cell.get("metadata", {}).get("tags", []) or []
        if SKIP_TAG in tags:
            continue
        code = "\n".join(line for line in _cell_source(cell).splitlines() if not _MAGIC.match(line))
        if not code.strip():
            continue
        try:
            exec(compile(code, f"<{path.name} cell {i}>", "exec"), ns)
        except BaseException as exc:  # noqa: BLE001 - a broken cell must not stop grading
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            errors.append((i, f"{type(exc).__name__}: {exc}"))
    return ns, errors


def load_implementation(spec: str | None, challenge: int | Challenge, default: str = "starter") -> ImplProxy:
    """Load the implementation named by ``spec``.

    ``spec`` is one of: ``'reference'`` (instructor solution), ``'starter'`` (the starter file of the challenge),
    a path to a ``.py`` file or a ``.ipynb`` notebook, or ``'module:dotted.name'``. ``None`` means ``default``.
    """
    from . import paths  # local import: paths imports the registry only

    ch = get(challenge) if isinstance(challenge, int) else challenge
    spec = spec or default
    if spec == "reference":
        try:
            module = importlib.import_module(paths.solution_module_name(ch))
        except ModuleNotFoundError as exc:
            raise ImplementationError(
                "The reference solutions are instructor-only and are not part of this checkout "
                f"({exc}). Use --impl <your file> or run inside the notebook."
            ) from None
        return ImplProxy(module, ch, "reference solution")
    if spec == "starter":
        return ImplProxy(load_py(paths.starter_path(ch)), ch, "starter file")
    if spec.startswith("variant:"):  # instructor tooling: "variant:<challenge>:<name>" (see instructor/variant_tests)
        _, number, name = spec.split(":", 2)
        try:
            catalog = importlib.import_module(f"instructor.variant_tests.catalog.c{int(number):02d}")
            reference = importlib.import_module(paths.solution_module_name(ch))
        except ModuleNotFoundError as exc:
            raise ImplementationError(f"variants are instructor-only and not available here ({exc})") from None
        ns = {k: v for k, v in vars(reference).items() if not k.startswith("__")}
        ns.update(catalog.VARIANTS[name].overrides)
        return ImplProxy(ns, ch, f"variant {number}:{name}")
    if spec.startswith("module:"):
        return ImplProxy(importlib.import_module(spec.split(":", 1)[1]), ch, spec)
    path = Path(spec)
    if path.suffix == ".ipynb":
        ns, errors = load_notebook(path)
        return ImplProxy(ns, ch, path.name, load_errors=errors)
    return ImplProxy(load_py(path), ch, path.name)
