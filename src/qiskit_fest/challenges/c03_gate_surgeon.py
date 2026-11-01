"""Provided code for Challenge 3 - Gate Surgeon.

Contains the *patient charts* (the exact bugs, shown as code), diagnosis tools and plots. The repaired circuits are what
YOU write in the notebook.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from .. import viz

R = 1 / np.sqrt(2)
GHZ_TARGET = Statevector([R, 0, 0, 0, 0, 0, 0, R])
SWAP_TARGET = Operator(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]))


def tilted_target(theta: float) -> Statevector:
    """cos(theta/2)|00> + sin(theta/2)|11>."""
    return Statevector([np.cos(theta / 2), 0, 0, np.sin(theta / 2)])


# ----------------------------------------------------------------------------------------------- the buggy originals
def buggy_ghz() -> QuantumCircuit:
    qc = QuantumCircuit(3)
    qc.h(2)
    qc.cx(1, 0)
    qc.cx(0, 2)
    qc.x(1)
    return qc


def buggy_swap() -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.cx(0, 1)
    qc.cx(1, 0)
    return qc


def buggy_tilted_pair(theta: float) -> QuantumCircuit:
    qc = QuantumCircuit(2)
    qc.ry(theta / 2, 0)
    qc.cx(1, 0)
    return qc


def buggy_readout() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3)
    qc.x(1)
    qc.measure([0, 1, 2], [2, 1, 0])
    return qc


# ----------------------------------------------------------------------------------------------- diagnosis tools
def describe_state(circuit: QuantumCircuit, name: str = "state") -> None:
    """Print the non-zero amplitudes of the state a measurement-free circuit prepares (bit-strings: qubit 0 on the right)."""
    sv = Statevector(circuit)
    n = circuit.num_qubits
    print(f"{name}:")
    shown = False
    for i, amp in enumerate(sv.data):
        if abs(amp) > 1e-9:
            shown = True
            print(f"  |{format(i, f'0{n}b')}>  amplitude {amp.real:+.3f}{amp.imag:+.3f}j   probability {abs(amp) ** 2:.3f}")
    if not shown:
        print("  (zero state?)")


def state_fidelity(circuit: QuantumCircuit, target: Statevector) -> float:
    """|<target|prepared>|^2 - 1.0 means 'same state (up to global phase)'."""
    return float(abs(np.vdot(target.data, Statevector(circuit).data)) ** 2)


def plot_fidelity_scan(builder, thetas=None, *, show: bool = True):
    """Fidelity of ``builder(theta)`` with cos(theta/2)|00> + sin(theta/2)|11> over a range of angles (1.0 = correct)."""
    thetas = np.linspace(-np.pi, 2 * np.pi, 61) if thetas is None else np.asarray(thetas)
    fid = [state_fidelity(builder(float(t)), tilted_target(float(t))) for t in thetas]
    return viz.plot_lines({"fidelity with the target": (thetas, fid)}, "Does the repair work for every angle?", "theta (radians)",
                          "fidelity (1 = correct)", show=show, markers=False)
