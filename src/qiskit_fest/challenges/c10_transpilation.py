"""Provided code for Challenge 10 - The Hardware Architect (transpilation for a chip with limited connectivity).

The provided pieces are the device description, the reference circuit, the *baseline* transpilation your result is compared with,
validators and plots. Nothing here counts gates, checks a circuit against a device or optimises: those are your TODOs.

The device model (identical in the problem statement and in every test)
* qubits ``0 .. n-1``; the **coupling map** is a list of qubit pairs ``(a, b)`` that can run a two-qubit gate - the pairs are
  **bidirectional** ((a, b) allows both directions);
* the **basis gates** are the only gates the chip runs; ``measure`` and ``barrier`` are always allowed;
* the number of device qubits equals ``max(node) + 1`` of the coupling map, and the circuits of this challenge have exactly that many qubits.
"""
from __future__ import annotations

import math
import numbers

import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from .. import viz

#: A line of six qubits 0-1-2-3-4-5 and an IBM-like native gate set.
LINE6 = [(i, i + 1) for i in range(5)]
BASIS_GATES = ["rz", "sx", "x", "cx"]


def line_edges(n: int) -> list[tuple[int, int]]:
    """Coupling map of a line of ``n`` qubits."""
    return [(i, i + 1) for i in range(n - 1)]


def ring_edges(n: int) -> list[tuple[int, int]]:
    """Coupling map of a ring of ``n`` qubits."""
    return [(i, (i + 1) % n) for i in range(n)]


def validate_device(coupling_edges, basis_gates) -> tuple[list[tuple[int, int]], list[str], int]:
    """Check a device description and return ``(edges, basis, num_qubits)``.

    ``ValueError`` unless ``coupling_edges`` is a non-empty list of pairs of distinct non-negative integers (no repeated pair, in
    either direction) and ``basis_gates`` a non-empty collection of gate names (strings). ``num_qubits = max(node) + 1``.
    """
    try:
        edges = list(coupling_edges)
    except TypeError:
        raise ValueError("coupling_edges must be a list of qubit pairs") from None
    if not edges:
        raise ValueError("the coupling map is empty")
    clean, seen = [], set()
    for edge in edges:
        try:
            a, b = edge
        except (TypeError, ValueError):
            raise ValueError(f"every coupling must be a pair of qubits, got {edge!r}") from None
        if not all(isinstance(q, numbers.Integral) and not isinstance(q, bool) and q >= 0 for q in (a, b)):
            raise ValueError(f"qubit indices must be non-negative integers, got {edge!r}")
        if a == b:
            raise ValueError(f"a qubit cannot be coupled to itself: {edge!r}")
        key = (min(int(a), int(b)), max(int(a), int(b)))
        if key in seen:
            raise ValueError(f"the coupling {key} appears more than once")
        seen.add(key)
        clean.append((int(a), int(b)))
    try:
        basis = list(basis_gates)
    except TypeError:
        raise ValueError("basis_gates must be a collection of gate names") from None
    if not basis or not all(isinstance(g, str) and g for g in basis):
        raise ValueError("basis_gates must be a non-empty collection of gate names")
    return clean, basis, 1 + max(q for pair in clean for q in pair)


def symmetric_coupling_map(coupling_edges) -> CouplingMap:
    """Qiskit ``CouplingMap`` with both directions of every coupling (the device model is bidirectional)."""
    edges = [tuple(e) for e in coupling_edges]
    return CouplingMap(edges + [(b, a) for a, b in edges])


def baseline_transpile(circuit: QuantumCircuit, coupling_edges, basis_gates=BASIS_GATES, seed: int = 0) -> QuantumCircuit:
    """The *baseline*: Qiskit's lowest optimisation level (0: trivial layout, no optimisation) for the given device. Your
    optimised circuit is judged against this one (same coupling map, basis gates and seed)."""
    pm = generate_preset_pass_manager(optimization_level=0, coupling_map=symmetric_coupling_map(coupling_edges),
                                      basis_gates=list(basis_gates), seed_transpiler=seed)
    return pm.run(circuit)


# ------------------------------------------------------------------------------------------------------------------
# circuits
# ------------------------------------------------------------------------------------------------------------------
def star_ghz(n: int) -> QuantumCircuit:
    """GHZ preparation 'star': H on qubit 0, then CNOT(0, k) for every other qubit k. Simple to write, bad for a line."""
    qc = QuantumCircuit(n)
    qc.h(0)
    for k in range(1, n):
        qc.cx(0, k)
    return qc


def reference_circuit() -> QuantumCircuit:
    """The supplied reference circuit (6 qubits): ZZ-type interactions along a path whose qubits are *scrambled* (0-3-1-4-2-5), one
    long-range CNOT pair and a Hadamard pair that cancel. A naive layout needs many SWAPs; a good layout needs none."""
    path = [0, 3, 1, 4, 2, 5]
    qc = QuantumCircuit(6)
    qc.h(range(6))
    for a, b in zip(path, path[1:]):
        qc.cx(a, b)
        qc.rz(0.37, b)
        qc.cx(a, b)          # exp(-i theta ZZ / 2) up to local gates: two CNOTs per link
    qc.cx(0, 5)
    qc.cx(0, 5)              # a CNOT pair: the identity
    qc.h(2)
    qc.h(2)                  # a Hadamard pair: the identity
    return qc


# ------------------------------------------------------------------------------------------------------------------
# plots
# ------------------------------------------------------------------------------------------------------------------
def plot_coupling_map(coupling_edges, title: str = "Coupling map", highlight=None, *, show: bool = True):
    """Draw the device graph (nodes on a circle); ``highlight`` is an optional list of coupled pairs to emphasise."""
    import matplotlib.pyplot as plt

    edges, _, n = validate_device(coupling_edges, ["cx"])
    angles = np.pi / 2 - 2 * np.pi * np.arange(n) / n
    pos = {q: (math.cos(a), math.sin(a)) for q, a in enumerate(angles)}
    marked = {tuple(sorted(e)) for e in (highlight or [])}
    fig, ax = plt.subplots(figsize=(3.8, 3.4))
    for a, b in edges:
        hot = tuple(sorted((a, b))) in marked
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color=viz.PALETTE[1] if hot else "0.5", lw=3 if hot else 1.6, zorder=1)
    for q in range(n):
        ax.scatter(*pos[q], s=420, color=viz.PALETTE[0], edgecolor="white", zorder=2)
        ax.text(*pos[q], str(q), color="white", ha="center", va="center", fontweight="bold", zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_cost_comparison(rows: dict, title: str = "Baseline versus optimised circuit", *, show: bool = True):
    """Grouped bars for ``{label: {'depth': ..., 'two_qubit_gates': ..., 'total_gates': ...}}`` (e.g. 'baseline', 'optimised')."""
    import matplotlib.pyplot as plt

    metrics = ["two_qubit_gates", "depth", "total_gates"]
    names = list(rows)
    width = 0.8 / len(names)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    for i, name in enumerate(names):
        values = [rows[name][m] for m in metrics]
        bars = ax.bar(np.arange(len(metrics)) + (i - (len(names) - 1) / 2) * width, values, width, label=name, color=viz.PALETTE[i], edgecolor="white")
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.5, str(v), ha="center", fontsize=8)
    ax.set_xticks(np.arange(len(metrics)), ["two-qubit gates", "depth", "total gates"])
    ax.set_title(title, fontweight="bold")
    ax.legend()
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
