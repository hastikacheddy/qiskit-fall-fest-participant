"""Export the functions you wrote in a notebook into a stand-alone ``.py`` file (an optional way to hand in a solution).

The notebook itself can be submitted too; this is a convenience for graders that prefer a plain Python file. The exported
file is made self-contained: imports and simple constants your functions rely on are copied along, and the result is
imported once to prove that it loads.
"""
from __future__ import annotations

import ast
import builtins
import inspect
import symtable
import textwrap
from pathlib import Path

from .loading import load_py
from .registry import get


class ExportError(RuntimeError):
    pass


def _free_globals(source: str) -> set[str]:
    """Names a block of function definitions reads from module scope (excluding builtins and its own definitions)."""
    table = symtable.symtable(source, "<export>", "exec")
    defined = {s.get_name() for s in table.get_symbols() if s.is_assigned() or s.is_imported()}
    used: set[str] = set()

    def walk(t):
        for sym in t.get_symbols():
            if sym.is_global() and sym.is_referenced():
                used.add(sym.get_name())
        for child in t.get_children():
            walk(child)

    walk(table)
    return {n for n in used if n not in defined and not hasattr(builtins, n)}


def _import_line(name: str, obj) -> str | None:
    """A line that recreates ``name`` for ``obj`` if it is a module, an imported callable/class or a simple constant."""
    import types

    if isinstance(obj, types.ModuleType):
        return f"import {obj.__name__}" if obj.__name__ == name else f"import {obj.__name__} as {name}"
    mod = getattr(obj, "__module__", None)
    if mod and mod not in ("__main__", "fest_notebook", "builtins") and hasattr(obj, "__name__"):
        qual = obj.__name__
        return f"from {mod} import {qual}" + (f" as {name}" if qual != name else "")
    if isinstance(obj, (int, float, complex, str, bool, bytes, tuple, list, dict, set, frozenset, type(None))):
        return f"{name} = {obj!r}"
    return None


def export_submission(namespace: dict, challenge: int, path: str | Path | None = None) -> Path:
    """Write the challenge functions (and your helper functions) found in ``namespace`` to ``submission_cNN.py``.

    Raises :class:`ExportError` if a required function is missing or its source cannot be retrieved.
    """
    ch = get(challenge)
    path = Path(path) if path else Path.cwd() / f"submission_c{ch.number:02d}.py"
    wanted = [n for n in ch.all_functions if callable(namespace.get(n))]
    missing = [n for n in ch.functions if n not in wanted]
    if missing:
        raise ExportError(f"these required functions are not defined yet: {', '.join(missing)}")
    mod_name = namespace.get("__name__", "__main__")
    helpers = [
        n for n, v in namespace.items()
        if inspect.isfunction(v) and v.__module__ == mod_name and n not in wanted and not n.startswith("_")
    ]
    parts: list[str] = []
    for name in wanted + helpers:
        try:
            parts.append(textwrap.dedent(inspect.getsource(namespace[name])).rstrip() + "\n")
        except (OSError, TypeError) as exc:
            raise ExportError(
                f"could not read the source of `{name}` ({exc}). Re-run the cell that defines it, or hand in the "
                "notebook itself (File > Download .ipynb)."
            ) from None
    body = "\n\n".join(parts)
    header_lines, unresolved = [], []
    for name in sorted(_free_globals(body)):
        if name in namespace:
            line = _import_line(name, namespace[name])
            (header_lines if line else unresolved).append(line or name)
        else:
            unresolved.append(name)
    if unresolved:
        raise ExportError(
            "your functions use names that cannot be exported automatically: "
            + ", ".join(sorted(unresolved))
            + ". Define them inside the functions, or hand in the notebook itself."
        )
    text = (
        f'"""Challenge {ch.number} ({ch.title}) - exported from a notebook with qiskit_fest.export."""\n'
        "from __future__ import annotations\n\n" + "\n".join(sorted(set(header_lines))) + "\n\n\n" + body
    )
    ast.parse(text)  # syntax check
    path.write_text(text, encoding="utf8")
    load_py(path)  # prove that the file imports on its own
    return path
