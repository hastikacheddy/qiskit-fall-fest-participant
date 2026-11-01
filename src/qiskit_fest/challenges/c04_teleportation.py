"""Provided code for Challenge 4 - Teleport the Qubit.

``assemble`` wires YOUR three functions into a complete protocol; ``branch_report`` checks the result exactly (no sampling).
Roles in the 3-qubit circuit: qubit 0 = the **message** (Alice's unknown state), qubit 1 = **Alice's half** of the Bell pair,
qubit 2 = **Bob**. Two classical bits carry the news from Alice to Bob:

* ``mz`` - the outcome of measuring the message qubit (after the Hadamard); it tells Bob whether to apply Z;
* ``mx`` - the outcome of measuring Alice's half; it tells Bob whether to apply X.
"""
from __future__ import annotations

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import DensityMatrix, Statevector

from .. import viz
from ..sim import Branch, exact_branches, fidelity_with_pure

MESSAGE, ALICE, BOB = 0, 1, 2

#: Public example states for the notebook (the hidden tests use many others).
R = 1 / np.sqrt(2)
EXAMPLE_STATES = {
    "|1>": Statevector([0, 1]),
    "|+>": Statevector([R, R]),
    "|+i>": Statevector([R, 1j * R]),
    "generic": Statevector([np.cos(0.4), np.exp(0.9j) * np.sin(0.4)]),
}


def prep_circuit(state: Statevector) -> QuantumCircuit:
    """One-qubit circuit that prepares ``state`` from |0> (gates only, no reset)."""
    qc = QuantumCircuit(1)
    qc.prepare_state(state.data, 0)
    return qc


def assemble(prep: QuantumCircuit, bell_pair, alice_measure, bob_fix) -> QuantumCircuit:
    """Teleportation circuit: prepare the message, share a Bell pair, Alice measures, Bob corrects.

    ``bell_pair(qc, a, b)``, ``alice_measure(qc, msg, alice, z_bit, x_bit)`` and ``bob_fix(qc, bob, z_bit, x_bit)`` are YOUR
    functions (dependency injection keeps the tests independent of anything you might edit here).
    """
    qr = QuantumRegister(3, "q")
    mz = ClassicalRegister(1, "mz")
    mx = ClassicalRegister(1, "mx")
    qc = QuantumCircuit(qr, mz, mx)
    qc.compose(prep, qubits=[MESSAGE], inplace=True)
    qc.barrier()
    bell_pair(qc, ALICE, BOB)
    qc.barrier()
    alice_measure(qc, MESSAGE, ALICE, mz[0], mx[0])
    qc.barrier()
    bob_fix(qc, BOB, mz[0], mx[0])
    return qc


def branch_report(circuit: QuantumCircuit, psi: Statevector) -> list[tuple[str, float, float]]:
    """For every measurement outcome: ``(mx mz bits, probability, fidelity of Bob's qubit with psi)`` - exact."""
    rows = []
    for br in exact_branches(circuit):
        bob = br.reduced_state([BOB])
        rows.append((br.clbit_string(), br.probability, fidelity_with_pure(bob, psi)))
    return rows


def plot_branch_fidelities(circuit: QuantumCircuit, psi: Statevector, title: str = "", *, show: bool = True):
    """Bar chart: for each of the four classical outcomes, the fidelity of Bob's final qubit with the message."""
    rows = branch_report(circuit, psi)
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    labels = [f"mx mz = {r[0]}\n(p = {r[1]:.2f})" for r in rows]
    ax.bar(labels, [r[2] for r in rows], color=viz.PALETTE[2], edgecolor="white")
    ax.set_ylim(0, 1.08)
    ax.axhline(1.0, color="k", ls=":", lw=1)
    ax.set_ylabel("fidelity of Bob's qubit with the message")
    ax.set_title(title or "Teleportation: fidelity in every measurement branch (1 = perfect)", fontweight="bold", fontsize=10)
    for i, r in enumerate(rows):
        ax.text(i, r[2] + 0.015, f"{r[2]:.3f}", ha="center", fontsize=9)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
