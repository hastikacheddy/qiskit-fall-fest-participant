"""Environment helpers used by the first cell of every notebook."""
from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys

from . import VERIFIED_WITH, environment_report


def print_environment() -> None:
    """Print the installed library versions and say whether they match the verified set (see requirements.txt)."""
    have = environment_report()
    differ = {k: (VERIFIED_WITH[k], have[k]) for k in VERIFIED_WITH if have[k] not in (VERIFIED_WITH[k], "missing")}
    missing = [k for k, v in have.items() if v == "missing" and k != "qiskit-aer"]
    print("Python", sys.version.split()[0], "|", ", ".join(f"{k} {v}" for k, v in have.items()))
    if missing:
        print("Missing packages:", ", ".join(missing), "- run `pip install -r requirements.txt`.")
    if differ:
        print("Note: versions differ from the verified set (verified -> yours):",
              {k: f"{a} -> {b}" for k, (a, b) in differ.items()},
              "\n      Everything should still work; if a check behaves oddly, `pip install -r requirements.txt` "
              "reproduces the verified environment.")
    elif not missing:
        print("Environment matches the verified set.")


TLS_HINT = ("On some Linux systems qiskit-aer cannot be loaded ('cannot allocate memory in static TLS block'). Start Python / Jupyter with the "
            "environment variable GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096, for example `export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096` "
            "in the terminal before `jupyter lab`. (It has to be set before the process starts; it cannot be set from inside a running notebook.)")


def _import_name(requirement: str) -> str:
    return requirement.split("[")[0].split("=")[0].split(">")[0].split("<")[0].strip().replace("-", "_")


def ensure_packages(*requirements: str) -> None:
    """Install optional packages that are not importable yet (``ensure_packages("qiskit-aer")``) and check that they load.

    The import name is derived from the distribution name (``qiskit-aer`` -> ``qiskit_aer``). A package that is installed but fails to
    import is reported with the reason (and, for the known static-TLS problem of qiskit-aer on some Linux systems, the fix) instead of
    leaving the participant with a cryptic traceback later.
    """
    todo = [r for r in requirements if importlib.util.find_spec(_import_name(r)) is None]
    if todo:
        print("Installing:", ", ".join(todo), "(first run only) ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *todo])
        importlib.invalidate_caches()
    for requirement in requirements:
        name = _import_name(requirement)
        try:
            importlib.import_module(name)
        except ImportError as exc:
            print(f"WARNING: {name} is installed but cannot be imported: {exc}")
            if "static TLS" in str(exc):
                print(TLS_HINT)
