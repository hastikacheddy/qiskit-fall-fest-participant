"""qiskit_fest - helper package of the QubitHub Qiskit Fall Fest 2026 challenge bank.

Participant-facing helpers (safe to distribute):

* :mod:`qiskit_fest.sim`       exact simulation incl. mid-circuit measurement and classical control
* :mod:`qiskit_fest.viz`       plotting helpers
* :mod:`qiskit_fest.checks`    ``run_public_checks`` / ``if_ready`` used inside the notebooks
* :mod:`qiskit_fest.export`    ``export_submission`` (turn notebook functions into a ``.py`` file)
* :mod:`qiskit_fest.registry`  metadata of the ten challenges
* :mod:`qiskit_fest.challenges` the provided (non-TODO) code of every challenge

Instructor tooling that must also work without the instructor folder: :mod:`qiskit_fest.loading` and
:mod:`qiskit_fest.testing` (pytest plugin).
"""
from __future__ import annotations

__version__ = "1.0.0"

#: Exact library versions the project was executed and verified with (see requirements.txt).
VERIFIED_WITH = {
    "qiskit": "2.6.0",
    "qiskit-aer": "0.18.0",
    "numpy": "2.4.6",
    "scipy": "1.17.1",
    "matplotlib": "3.11.2",
    "pytest": "9.1.1",
}


def environment_report() -> dict[str, str]:
    """Installed versions of the libraries listed in :data:`VERIFIED_WITH` (``'missing'`` if not installed)."""
    from importlib import metadata

    report = {}
    for name in VERIFIED_WITH:
        try:
            report[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            report[name] = "missing"
    return report
