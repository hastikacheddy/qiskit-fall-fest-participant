"""Provided code for Challenge 5 - Find the Hidden State (Grover search).

Conventions (also in the problem statement): bit-strings use Qiskit order - the **rightmost** character is qubit 0, so the
integer ``int(marked, 2)`` is the index of the marked basis state. Nothing here builds an oracle, a diffuser or a Grover
circuit: those are your TODOs. The helpers only *measure* what you built.
"""
from __future__ import annotations

import math

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .. import viz

#: Public example: a non-palindromic bit-string, so a reversed bit order is visible immediately.
EXAMPLE_MARKED = "110"


def success_probability(circuit: QuantumCircuit, marked: str) -> float:
    """Probability of measuring the marked bit-string at the end of a measurement-free circuit (exact simulation)."""
    return float(abs(Statevector(circuit).data[int(marked, 2)]) ** 2)


def theoretical_success(n: int, num_marked: int, iterations: int) -> float:
    """Ideal success probability sin^2((2k+1) theta) with theta = arcsin(sqrt(M / N)) after k Grover iterations."""
    theta = math.asin(math.sqrt(num_marked / 2**n))
    return math.sin((2 * iterations + 1) * theta) ** 2


def _display_amplitudes(state: Statevector) -> np.ndarray:
    """Real amplitudes for plotting. A circuit is only defined up to a global phase (a diffuser built as I - 2|s><s| has the
    opposite sign of 2|s><s| - I), so the phase is fixed such that the *mean* amplitude is positive. The diffuser keeps the
    mean, which makes the picture independent of how the circuit was built."""
    data = np.asarray(state.data)
    total = data.sum()
    anchor = total if abs(total) > 1e-9 else data[int(np.argmax(np.abs(data)))]
    return np.real(data * np.exp(-1j * np.angle(anchor)))


def plot_amplitude_steps(marked: str, oracle, diffuser, *, show: bool = True):
    """Amplitudes of all basis states: uniform start, after YOUR oracle, after YOUR diffuser (one Grover iteration)."""
    import matplotlib.pyplot as plt

    n = len(marked)
    h_all = QuantumCircuit(n)
    h_all.h(range(n))
    start = Statevector(h_all)
    after_oracle = start.evolve(oracle(marked))
    after_diffuser = after_oracle.evolve(diffuser(n))
    keys = [format(i, f"0{n}b") for i in range(2**n)]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, (title, sv) in zip(axes, [("1. uniform superposition", start), ("2. after the oracle (sign flip)", after_oracle),
                                       ("3. after the diffuser (amplified)", after_diffuser)]):
        colors = [viz.PALETTE[1] if k == marked else viz.PALETTE[0] for k in keys]
        ax.bar(keys, _display_amplitudes(sv), color=colors)
        ax.axhline(0, color="k", lw=0.7)
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.tick_params(axis="x", labelrotation=90, labelsize=8)
    axes[0].set_ylabel("amplitude")
    fig.suptitle(f"One Grover iteration (marked = {marked}, highlighted)", fontweight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.text(0.5, 0.005, "global phase fixed so that the mean amplitude is positive", ha="center", fontsize=8, color="0.35")
    return viz._finish(fig, show)


def plot_success_curve(grover_circuit, marked: str, kmax: int | None = None, num_marked: int = 1, *, show: bool = True):
    """Success probability of YOUR ``grover_circuit(marked, k)`` for k = 0..kmax, with the ideal theory curve."""
    n = len(marked)
    kmax = kmax if kmax is not None else int(math.ceil(1.6 * math.pi / (4 * math.asin(math.sqrt(num_marked / 2**n)))))
    ks = list(range(kmax + 1))
    measured = [success_probability(grover_circuit(marked, k), marked) for k in ks]
    theory = [theoretical_success(n, num_marked, k) for k in ks]
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(ks, theory, "-", color="k", lw=1.2, label="theory  sin²((2k+1)θ)")
    ax.plot(ks, measured, "o", color=viz.PALETTE[1], ms=7, label="your circuit")
    best = int(np.argmax(theory))
    ax.axvline(best, color=viz.PALETTE[2], ls="--", lw=1)
    ax.text(best - 0.08, 0.04, f"first maximum at k = {best}", color=viz.PALETTE[2], fontsize=9, ha="right")
    ax.set_xlabel("number of Grover iterations k")
    ax.set_ylabel(f"P(measure {marked})")
    ax.set_ylim(0, 1.05)
    ax.set_xticks(ks)
    ax.set_title("Success probability versus iterations - more is not better", fontweight="bold")
    ax.legend(loc="upper right")
    fig.tight_layout()
    return viz._finish(fig, show)
