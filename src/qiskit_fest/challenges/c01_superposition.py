"""Provided code for Challenge 1 - Superposition Under the Microscope.

Nothing here solves a TODO: it only offers finite-shot sampling (to contrast with exact probabilities), Bloch vectors and
plots that take *your* results as input.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Pauli, Statevector

from .. import viz

#: Public worked example for ``born_probabilities``: amplitudes (3/5, 4i/5) give probabilities (0.36, 0.64).
EXAMPLE_AMPLITUDES = (0.6, 0.8j)
EXAMPLE_PROBABILITIES = (0.36, 0.64)


def sampled_frequencies(circuit: QuantumCircuit, shots: int = 1000, seed: int = 7) -> dict[str, float]:
    """Measure every qubit of a measurement-free circuit ``shots`` times and return the observed frequencies.

    Uses Qiskit's ``StatevectorSampler`` with a fixed ``seed`` (reproducible). Unlike exact probabilities, these numbers
    fluctuate around the truth by about ``sqrt(p (1 - p) / shots)``.
    """
    n = circuit.num_qubits
    qc = circuit.copy()
    qc.measure_all()
    result = StatevectorSampler(default_shots=shots, seed=seed).run([qc]).result()
    counts = result[0].data.meas.get_counts()
    return {format(i, f"0{n}b"): counts.get(format(i, f"0{n}b"), 0) / shots for i in range(2**n)}


def shot_noise(p: float, shots: int) -> float:
    """Standard deviation of an observed frequency for true probability ``p`` and ``shots`` repetitions."""
    return float(np.sqrt(p * (1 - p) / shots))


def bloch_vector(circuit: QuantumCircuit) -> tuple[float, float, float]:
    """Bloch vector (<X>, <Y>, <Z>) of the state prepared by a one-qubit circuit."""
    if circuit.num_qubits != 1:
        raise ValueError("bloch_vector expects a one-qubit circuit")
    state = Statevector(circuit)
    return tuple(float(np.real(state.expectation_value(Pauli(p)))) for p in "XYZ")


def plot_exact_vs_sampled(circuit: QuantumCircuit, exact, shots=(10, 50, 200, 1000), *, show: bool = True):
    """Compare ``exact`` (computed by YOUR ``exact_probabilities``) with finite-shot frequencies for several shot counts."""
    n = circuit.num_qubits
    keys = [format(i, f"0{n}b") for i in range(2**n)]
    dists = {"exact (yours)": dict(zip(keys, map(float, exact)))}
    for s in shots:
        dists[f"{s} shots"] = sampled_frequencies(circuit, shots=s)
    return viz.plot_distributions(dists, "Exact probabilities versus finite-shot frequencies", show=show, figsize=(8, 3.8))


def plot_same_probabilities_different_states(circuits: dict[str, QuantumCircuit], *, show: bool = True):
    """For each named one-qubit circuit: its Z-basis outcome probabilities (left) and Bloch components (right).

    Different circuits can share the left picture and still differ on the right - phases are invisible to a Z measurement.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(circuits), 2, figsize=(8, 2.1 * len(circuits)), squeeze=False)
    for row, (name, qc) in enumerate(circuits.items()):
        state = Statevector(qc)
        probs = state.probabilities()
        axes[row, 0].bar(["0", "1"], probs, color=viz.PALETTE[0])
        axes[row, 0].set_ylim(0, 1.05)
        axes[row, 0].set_ylabel(name)
        axes[row, 1].bar(["<X>", "<Y>", "<Z>"], bloch_vector(qc), color=viz.PALETTE[1])
        axes[row, 1].set_ylim(-1.05, 1.05)
        axes[row, 1].axhline(0, color="k", lw=0.6)
    axes[0, 0].set_title("measure in Z: P(0), P(1)", fontweight="bold")
    axes[0, 1].set_title("what the state really is: Bloch vector", fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)
