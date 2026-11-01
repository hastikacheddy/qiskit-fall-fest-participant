"""Provided code for Challenge 9 - Protect the Logical Qubit (the three-qubit bit-flip repetition code).

The provided pieces are the logical test states, the exact code words, a small experiment harness that runs *your* functions, an
input check for the feed-forward step and plots. Nothing here encodes, extracts a syndrome, decodes or corrects: those are your TODOs.

Layout used throughout (also by the tests)
* data qubits ``DATA = (0, 1, 2)`` hold the code word, ancilla qubits ``ANCILLAS = (3, 4)`` receive the syndrome;
* the logical input state ``alpha|0> + beta|1>`` is placed on the *first data qubit* (qubit 0) before encoding;
* a 2-bit classical register ``syn`` records the syndrome: ``syn[0]`` <- ancilla 0, ``syn[1]`` <- ancilla 1.
"""
from __future__ import annotations

import numbers

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import Clbit
from qiskit.quantum_info import Statevector

from .. import viz
from ..sim import exact_branches, fidelity_with_pure

DATA = (0, 1, 2)
ANCILLAS = (3, 4)

_H = 2 ** -0.5

#: Logical states ``(alpha, beta)`` used in the notebook and in the public tests (the hidden tests use many more).
LOGICAL_STATES = {
    "zero": (1.0, 0.0),
    "one": (0.0, 1.0),
    "plus": (_H, _H),
    "minus": (_H, -_H),
    "plus_i": (_H, 1j * _H),
    "generic": (np.cos(0.4), np.exp(1.1j) * np.sin(0.4)),
}


def code_state(alpha: complex, beta: complex, phase_flip: bool = False) -> Statevector:
    """The encoded logical qubit on three qubits: ``alpha|000> + beta|111>`` (bit-flip code) or ``alpha|+++> + beta|--->`` (phase-flip code)."""
    data = np.zeros(8, dtype=complex)
    if not phase_flip:
        data[0b000], data[0b111] = alpha, beta
    else:
        plus = np.full(8, 8 ** -0.5, dtype=complex)
        signs = np.array([(-1) ** bin(i).count("1") for i in range(8)], dtype=float)
        data = alpha * plus + beta * plus * signs
    return Statevector(data)


def _is_index(value) -> bool:
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def validate_layout(qc: QuantumCircuit, data, ancillas, syndrome) -> tuple[list[int], list[int], ClassicalRegister]:
    """Check the arguments of ``add_feedforward_correction`` and return ``(data, ancillas, syndrome)``.

    ``ValueError`` unless: ``qc`` is a ``QuantumCircuit``; ``data`` are three and ``ancillas`` two distinct qubit indices of ``qc``
    (no index in both); ``syndrome`` is a two-bit ``ClassicalRegister`` that belongs to ``qc``.
    """
    if not isinstance(qc, QuantumCircuit):
        raise ValueError("qc must be a QuantumCircuit")
    try:
        data, ancillas = list(data), list(ancillas)
    except TypeError:
        raise ValueError("data and ancillas must be sequences of qubit indices") from None
    if len(data) != 3 or len(ancillas) != 2:
        raise ValueError("need exactly 3 data qubits and 2 ancilla qubits")
    indices = data + ancillas
    if not all(_is_index(q) and 0 <= q < qc.num_qubits for q in indices):
        raise ValueError(f"qubit indices must be integers in [0, {qc.num_qubits - 1}]")
    if len(set(int(q) for q in indices)) != 5:
        raise ValueError("data and ancilla qubits must all be different")
    if not isinstance(syndrome, ClassicalRegister) or len(syndrome) != 2 or syndrome not in qc.cregs:
        raise ValueError("syndrome must be a 2-bit ClassicalRegister that was added to the circuit")
    return [int(q) for q in data], [int(q) for q in ancillas], syndrome


# ------------------------------------------------------------------------------------------------------------------
# experiment harness (runs YOUR functions)
# ------------------------------------------------------------------------------------------------------------------
def build_experiment(encode_circuit, add_feedforward_correction, logical, errors=(), data=DATA, ancillas=ANCILLAS, spectators: int = 0,
                     phase_flip: bool = False):
    """Circuit: prepare ``logical = (alpha, beta)`` on ``data[0]``, encode with ``encode_circuit()``, apply Pauli ``errors``,
    then call ``add_feedforward_correction(qc, data, ancillas, syn)``.

    ``errors`` is a list of ``(pauli, k)`` with ``pauli`` in ``"X", "Y", "Z"`` and ``k`` the position (0, 1, 2) in ``data``.
    ``spectators`` extra qubits are added at the end (they must stay untouched). With ``phase_flip=True`` the bit-flip machinery is
    used between two layers of Hadamards (a basis change turns Z errors into X errors) - for the phase-flip code of the bonus.
    Returns ``(circuit, syn_register)``.
    """
    n = 5 + spectators
    qc = QuantumCircuit(QuantumRegister(n, "q"), ClassicalRegister(2, "syn"))
    syn = qc.cregs[0]
    alpha, beta = logical
    qc.prepare_state([alpha, beta], data[0])
    qc.compose(encode_circuit(), qubits=list(data), inplace=True)
    for pauli, k in errors:
        getattr(qc, pauli.lower())(data[k])
    if phase_flip:
        for q in data:
            qc.h(q)
    add_feedforward_correction(qc, list(data), list(ancillas), syn)
    if phase_flip:
        for q in data:
            qc.h(q)
    return qc, syn


def run_recovery(encode_circuit, add_feedforward_correction, logical, errors=(), data=DATA, ancillas=ANCILLAS, phase_flip: bool = False) -> dict:
    """Run :func:`build_experiment` exactly (every measurement branch) and report, per syndrome outcome, the probability and the
    fidelity of the three data qubits with the ideal code word. Returns ``{'branches': [(syndrome, probability, fidelity)...],
    'min_fidelity': float}``."""
    qc, syn = build_experiment(encode_circuit, add_feedforward_correction, logical, errors, data, ancillas, phase_flip=phase_flip)
    target = code_state(*logical, phase_flip=phase_flip)
    rows = []
    for br in exact_branches(qc):
        fid = fidelity_with_pure(br.reduced_state(sorted(data)), target)
        rows.append((br.register_value(qc, syn), br.probability, fid))
    return {"branches": rows, "min_fidelity": min(f for _, _, f in rows)}


def observed_syndrome(syndrome_circuit, error_qubit: int | None):
    """Diagnostic: the syndrome YOUR ``syndrome_circuit()`` produces for the code word |000> with an X error on data qubit
    ``error_qubit`` (``None`` = no error). Returns ``(s0, s1)`` read from ancillas 3 and 4."""
    qc = QuantumCircuit(5)
    if error_qubit is not None:
        qc.x(error_qubit)
    qc.compose(syndrome_circuit(), inplace=True)
    state = Statevector(qc)
    index = int(np.argmax(np.abs(state.data)))
    return (index >> 3) & 1, (index >> 4) & 1


# ------------------------------------------------------------------------------------------------------------------
# plots
# ------------------------------------------------------------------------------------------------------------------
def plot_recovery(rows: dict, title: str = "Recovery of the logical qubit", *, show: bool = True):
    """Bar chart of ``{scenario: minimal fidelity with the ideal code word}`` (1 = fully recovered)."""
    import matplotlib.pyplot as plt

    names = list(rows)
    values = [rows[k] for k in names]
    colours = [viz.PALETTE[2] if v > 1 - 1e-9 else viz.PALETTE[1] for v in values]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    bars = ax.bar(names, values, color=colours, edgecolor="white")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.3f}", ha="center", fontsize=8)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("fidelity with the ideal code word")
    ax.set_title(title, fontweight="bold")
    ax.tick_params(axis="x", labelrotation=20, labelsize=8)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
