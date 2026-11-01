"""Provided code for Challenge 2 - The Entanglement Detective.

The *case file* below contains five suspect two-qubit states. Nothing here decides which suspects are entangled - that is
what your functions do.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .. import viz


def suspects() -> dict[str, Statevector]:
    """Five suspect states, given as exact state vectors (no circuits are revealed)."""
    r = 1 / np.sqrt(2)
    two_coins = Statevector([0.5, 0.5, 0.5, 0.5])                       # (|0>+|1>)(|0>+|1>)/2
    mystery_pair = Statevector([r, 0, 0, r])                             # (|00>+|11>)/sqrt(2)
    both_zero = Statevector([1, 0, 0, 0])                                # |00>
    tilted = Statevector([np.cos(np.pi / 8), 0, 0, np.sin(np.pi / 8)])   # cos(pi/8)|00> + sin(pi/8)|11>
    phase_trap = Statevector([0.5, 0.5, 0.5, -0.5])                      # uniform Z statistics - but not a product state
    return {
        "A: two coins": two_coins,
        "B: mystery pair": mystery_pair,
        "C: both zero": both_zero,
        "D: tilted pair": tilted,
        "E: phase trap": phase_trap,
    }


def plot_case_file(states: dict[str, Statevector], correlation, entangled, *, show: bool = True):
    """Bar chart of the Z/X/Y correlations of every suspect (computed by YOUR ``correlation``) and your verdicts."""
    import matplotlib.pyplot as plt

    names = list(states)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    width = 0.26
    for k, basis in enumerate("ZXY"):
        vals = [float(correlation(states[n], basis)) for n in names]
        ax.bar(np.arange(len(names)) + (k - 1) * width, vals, width, label=f"{basis}{basis} correlation", color=viz.PALETTE[k])
    ax.axhline(0, color="k", lw=0.7)
    labels = [f"{n}\n{'ENTANGLED' if entangled(states[n]) else 'product'}" for n in names]
    ax.set_xticks(np.arange(len(names)), labels, fontsize=8)
    ax.set_ylim(-1.15, 1.35)
    ax.set_ylabel("correlation  E = P(equal) - P(different)")
    ax.set_title("Case file: correlations in three bases, and your verdict", fontweight="bold")
    ax.legend(ncol=3, loc="upper center", fontsize=8)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
