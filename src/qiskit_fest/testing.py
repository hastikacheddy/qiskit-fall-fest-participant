"""pytest plugin of the challenge bank (loaded through ``addopts = -p qiskit_fest.testing`` in pyproject.toml).

Provides

* ``--impl``          which implementation to test: ``reference``, ``starter``, a ``.py`` file or a ``.ipynb`` notebook;
* ``--results-json``  write one record per test (outcome, tier, requirement ids, short message) to a JSON file; every record is
                     also appended to ``<file>.partial.jsonl`` as soon as the test finishes, so a crash or a timeout keeps the
                     results of the tests that did finish;
* a notebook submission whose cells raised while it was loaded is reported in ``<file>.notes.json`` (cell index -> message);
* ``--test-timeout``  end the pytest process if one test runs longer than N seconds (a submission with an endless loop): the hanging
                     test is recorded as ``timeout`` and the exit status is ``TIMEOUT_EXIT_CODE``;
* ``--exclude-nodeids`` skip exactly the listed test ids (used by the grader to continue after a timeout);
* the ``impl`` fixture (an :class:`~qiskit_fest.loading.ImplProxy`) for modules marked ``challenge(n)``;
* the markers ``challenge(n)``, ``tier(name)``, ``covers(*ids)`` and ``needs_aer``.

Tests never print the *expected* values of hidden checks in their own messages; the JSON results contain only the
test description, the tier and a short failure message so that sanitised feedback can be produced from them.
"""
from __future__ import annotations

import faulthandler
import importlib
import json
import os
import sys
import threading
from importlib.util import find_spec
from pathlib import Path

import pytest

from . import loading

#: Set by ``qiskit_fest.checks.run_public_checks`` so that a notebook's own functions are tested.
OVERRIDE_IMPL: loading.ImplProxy | None = None


def _aer_available() -> bool:
    """Is qiskit-aer installed *now*? Asked when the tests are collected, never cached when this plugin is imported.

    The setup cell of the challenge 6 notebook imports ``qiskit_fest.checks`` (and with it this plugin) first and installs Aer afterwards. A value
    remembered from import time would keep every challenge 6 check skipped on a machine that has no Aer yet - found on a real Colab runtime,
    where all 15 public checks of the first run were skipped although Aer had just been installed.
    """
    importlib.invalidate_caches()  # a package that was installed after the interpreter started is found only after this
    return find_spec("qiskit_aer") is not None


def pytest_addoption(parser):
    group = parser.getgroup("qiskit-fest", "Qiskit Fall Fest challenge bank")
    group.addoption("--impl", action="store", default=None,
                    help="implementation under test: 'reference', 'starter', a .py file or a .ipynb notebook")
    group.addoption("--results-json", action="store", default=None,
                    help="write per-test results (outcome, tier, covered requirements) to this JSON file")
    group.addoption("--test-timeout", action="store", type=float, default=0.0,
                    help="abort the whole pytest process when a single test runs longer than this many seconds (0 = off); "
                         "finished tests stay available in <results-json>.partial.jsonl")
    group.addoption("--exclude-nodeids", action="store", default=None,
                    help="JSON file with a list of exact test node ids that must not run")


def pytest_configure(config):
    for line in (
        "challenge(n): the test module belongs to challenge number n (1-10)",
        "tier(name): smoke | core | edge | quality | bonus | meta - how the result is used in grading (meta is never graded)",
        "covers(*ids): requirement ids from qiskit_fest.registry that the test verifies",
        "needs_aer: test needs the optional qiskit-aer package (skipped when it is not installed)",
        "slow: end-to-end test that runs notebooks, containers or many subprocesses (minutes); skip it in everyday work with -m 'not slow'",
    ):
        config.addinivalue_line("markers", line)
    config._fest_records = []
    config._fest_notes = {}
    path = config.getoption("--results-json", default=None)
    if path:  # start fresh side files (stale ones from an earlier run must never be mistaken for this run)
        Path(_partial_path(path)).write_text("", encoding="utf8")
        Path(_notes_path(path)).unlink(missing_ok=True)


def _partial_path(results_json: str) -> str:
    return f"{results_json}.partial.jsonl"


def _notes_path(results_json: str) -> str:
    """Side file with facts about the implementation under test that are not test results (cells of a notebook that failed to load)."""
    return f"{results_json}.notes.json"


def pytest_collection_modifyitems(config, items):
    exclude_file = config.getoption("--exclude-nodeids", default=None)
    if exclude_file:
        excluded = set(json.loads(Path(exclude_file).read_text(encoding="utf8")))
        dropped = [item for item in items if item.nodeid in excluded]
        if dropped:
            config.hook.pytest_deselected(items=dropped)
            items[:] = [item for item in items if item.nodeid not in excluded]
    if _aer_available():
        return
    skip = pytest.mark.skip(reason="qiskit-aer is not installed (optional dependency of Challenge 6)")
    for item in items:
        if "needs_aer" in item.keywords:
            item.add_marker(skip)


#: Exit status of a process that was stopped by the ``--test-timeout`` watchdog.
TIMEOUT_EXIT_CODE = 97
#: If native code holds the GIL, the Python timer cannot run; the C-level fallback kills the process this many seconds later.
WATCHDOG_GRACE = 10.0


def _on_timeout(results_json: str | None, nodeid: str, timeout: float) -> None:
    """Runs in the watchdog thread: record which test hung, then end the process immediately (nothing can unblock it)."""
    try:
        if results_json:
            record = {"nodeid": nodeid, "name": nodeid.split("::")[-1], "outcome": "timeout", "tier": "core", "covers": [], "todo": False,
                      "error_type": "Timeout", "message": f"no result after {timeout:g} s", "description": "", "duration": float(timeout)}
            with open(_partial_path(results_json), "a", encoding="utf8") as stream:
                stream.write(json.dumps(record) + "\n")
    finally:
        os._exit(TIMEOUT_EXIT_CODE)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Watchdog for ``--test-timeout`` (a submission with an endless loop must not block the grading of everything else).

    A timer thread writes a ``timeout`` record for the hanging test into the partial stream and ends the process with
    :data:`TIMEOUT_EXIT_CODE`. Native code that never releases the GIL would also block that thread, so a ``faulthandler``
    watchdog (pure C, no GIL needed) ends the process ``WATCHDOG_GRACE`` seconds later with exit status 1 and no record.
    """
    timeout = item.config.getoption("--test-timeout", default=0.0)
    timer = None
    if timeout and timeout > 0:
        timer = threading.Timer(timeout, _on_timeout, args=(item.config.getoption("--results-json", default=None), item.nodeid, timeout))
        timer.daemon = True
        timer.start()
        faulthandler.dump_traceback_later(timeout + WATCHDOG_GRACE, exit=True, file=sys.__stderr__)
    try:
        yield
    finally:
        if timer is not None:
            timer.cancel()
            faulthandler.cancel_dump_traceback_later()


@pytest.fixture(scope="session")
def default_impl_name() -> str:
    """Implementation used when ``--impl`` is not given. conftest.py files override this fixture."""
    return "starter"


@pytest.fixture(scope="module")
def impl(request, default_impl_name):
    """The implementation under test for the challenge declared with ``pytestmark = pytest.mark.challenge(n)``."""
    marker = request.node.get_closest_marker("challenge")
    if marker is None:
        raise RuntimeError("test module needs `pytestmark = pytest.mark.challenge(<number>)`")
    number = int(marker.args[0])
    if OVERRIDE_IMPL is not None:
        return OVERRIDE_IMPL
    spec = request.config.getoption("--impl") or default_impl_name
    proxy = loading.load_implementation(spec, number)
    errors = getattr(proxy, "load_errors", None)
    path = request.config.getoption("--results-json", default=None)
    if errors and path:  # cells of a submitted notebook that raised while it was loaded: written at once, so a later crash keeps them
        notes = request.config._fest_notes.setdefault("load_errors", {})
        notes.update({str(index): str(message)[:200] for index, message in errors})
        Path(_notes_path(path)).write_text(json.dumps(request.config._fest_notes), encoding="utf8")
    return proxy


def _marker_args(item, name):
    out = []
    for mark in item.iter_markers(name=name):
        out.extend(mark.args)
    return out


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    counts = (rep.when == "call") or (rep.when in ("setup", "teardown") and (rep.failed or rep.skipped))
    if not counts:
        return
    tiers = _marker_args(item, "tier")
    message = ""
    if rep.failed and call.excinfo is not None:
        exc = call.excinfo.value
        message = f"{type(exc).__name__}: {exc}".strip().splitlines()[0][:300] if str(exc) else type(exc).__name__
    elif rep.skipped and isinstance(rep.longrepr, tuple):
        message = str(rep.longrepr[2]).replace("Skipped: ", "")[:200]
    doc = (getattr(item.function, "__doc__", None) or "").strip().splitlines()
    record = {
        "nodeid": item.nodeid,
        "name": item.name,
        "description": doc[0].strip() if doc else item.name,
        "outcome": "skipped" if rep.skipped else ("passed" if rep.passed else "failed"),
        "tier": tiers[0] if tiers else "core",
        "covers": _marker_args(item, "covers"),
        "todo": bool(call.excinfo and isinstance(call.excinfo.value, loading.TodoNotImplemented)),
        "error_type": type(call.excinfo.value).__name__ if (rep.failed and call.excinfo is not None) else "",
        "message": message,
        "duration": round(rep.duration, 4),
    }
    item.config._fest_records.append(record)
    path = item.config.getoption("--results-json", default=None)
    if path:
        try:
            with open(_partial_path(path), "a", encoding="utf8") as stream:
                stream.write(json.dumps(record) + "\n")
        except OSError:  # results are a convenience: never let them break a test run
            pass


def pytest_sessionfinish(session, exitstatus):
    path = session.config.getoption("--results-json", default=None)
    if path:
        Path(path).write_text(json.dumps(session.config._fest_records, indent=1), encoding="utf8")
        Path(_partial_path(path)).unlink(missing_ok=True)  # the complete file supersedes the partial stream
