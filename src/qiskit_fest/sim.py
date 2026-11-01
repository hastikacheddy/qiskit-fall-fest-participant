"""Exact simulation of small circuits with mid-circuit measurement and classical control.

Qiskit's ``Statevector`` cannot run a circuit that measures a qubit or branches on a classical bit, and sampling such a
circuit with a finite number of shots gives statistical (not exact) answers. This module simulates them **exactly** by
enumerating the possible measurement outcomes ("branches"). Each branch is one pure post-measurement state together with
its probability and the classical bit values that were recorded.

Typical uses in this challenge bank:

* Challenge 4 (teleportation): after Alice's measurement there are four branches (probability 1/4 each); after Bob's
  classically-controlled correction every branch must hold the teleported state.
* Challenge 9 (error correction): the syndrome measurement and feed-forward correction are simulated exactly.
* Any circuit that ends in ``measure`` gates: :func:`measured_distribution` returns the exact probability of each
  classical bit-string (no sampling noise).

Conventions
-----------
* Qiskit bit order: qubit 0 / clbit 0 is the *least* significant bit. Bit-strings are written with bit 0 on the
  **right**, exactly as in ``counts`` dictionaries.
* The global phase of a circuit is ignored (it is physically unobservable).
* Supported: all unitary gates and instructions that ``Statevector.evolve`` supports, ``measure``, ``reset``,
  ``barrier``/``delay`` (ignored), ``initialize`` and ``if_test`` / ``IfElseOp`` whose condition is either
  ``(Clbit, value)`` or ``(ClassicalRegister, value)`` (nested blocks and else-branches work).
* Not supported (raises ``NotImplementedError`` with an explanation): ``for_loop``, ``while_loop``, ``switch``,
  and ``expr``-based conditions.

The simulator itself is validated against closed-form results and (when Qiskit Aer is installed) against Aer sampling in
``tests/tools/test_sim.py``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ClassicalRegister, Clbit, ForLoopOp, IfElseOp, SwitchCaseOp, WhileLoopOp
from qiskit.quantum_info import DensityMatrix, Statevector, partial_trace

#: Branches with probability below this are discarded (they are numerical dust, e.g. 1e-33).
PRUNE = 1e-12

__all__ = [
    "Branch",
    "exact_branches",
    "measured_distribution",
    "average_reduced_state",
    "fidelity_with_pure",
    "bitstring",
]


def bitstring(value: int, width: int) -> str:
    """Return ``value`` as a ``width``-character bit-string, bit 0 on the right (Qiskit order)."""
    return format(int(value), f"0{width}b") if width > 0 else ""


@dataclass(frozen=True)
class Branch:
    """One measurement branch: a pure state of *all* circuit qubits, its probability and the recorded clbits."""

    probability: float
    state: Statevector
    clbits: tuple[int, ...]

    def clbit_string(self) -> str:
        """Classical bits as a bit-string with clbit 0 on the right (the order used by ``counts``)."""
        return "".join(str(b) for b in reversed(self.clbits))

    def register_value(self, circuit: QuantumCircuit, register: ClassicalRegister | str) -> int:
        """Integer value stored in a classical register (register bit 0 = least significant)."""
        if isinstance(register, str):
            register = next(r for r in circuit.cregs if r.name == register)
        return sum(self.clbits[circuit.find_bit(bit).index] << k for k, bit in enumerate(register))

    def reduced_state(self, keep: Iterable[int]) -> DensityMatrix:
        """Reduced density matrix on the qubits ``keep`` (kept qubits stay in ascending index order)."""
        return _reduced(self.state, keep)


# --------------------------------------------------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------------------------------------------------
def exact_branches(circuit: QuantumCircuit, initial_state=None) -> list[Branch]:
    """Simulate ``circuit`` exactly and return every measurement branch.

    ``initial_state`` may be anything ``Statevector`` accepts (default: all qubits in ``|0>``). Branch probabilities sum
    to 1. A circuit without measurements or reset returns a single branch with probability 1.
    """
    n, m = circuit.num_qubits, circuit.num_clbits
    if initial_state is None:
        data = np.zeros(2**n, dtype=complex)
        data[0] = 1.0
    else:
        data = np.asarray(Statevector(initial_state).data, dtype=complex)
        if data.size != 2**n:
            raise ValueError(f"initial_state has dimension {data.size}, but the circuit has {n} qubits")
    branches = [(1.0, data, (0,) * m)]
    branches = _run(circuit, list(range(n)), list(range(m)), branches, n)
    branches.sort(key=lambda b: (b[2][::-1], -b[0]))
    total = sum(p for p, _, _ in branches)
    return [Branch(float(p / total), Statevector(d), c) for p, d, c in branches]


def measured_distribution(circuit: QuantumCircuit, initial_state=None) -> dict[str, float]:
    """Exact probability of every recorded classical bit-string (clbit 0 on the right).

    Unwritten clbits stay 0. Outcomes with probability ~0 are omitted.
    """
    dist: dict[str, float] = {}
    for br in exact_branches(circuit, initial_state):
        key = br.clbit_string()
        dist[key] = dist.get(key, 0.0) + br.probability
    return dict(sorted(dist.items()))


def average_reduced_state(branches: Sequence[Branch], keep: Iterable[int]) -> DensityMatrix:
    """Probability-weighted average of the reduced states of ``keep`` over all branches (the state *if the outcomes are
    not looked at*)."""
    keep = list(keep)
    rho = None
    for br in branches:
        part = br.reduced_state(keep).data * br.probability
        rho = part if rho is None else rho + part
    return DensityMatrix(rho)


def fidelity_with_pure(rho: DensityMatrix | Statevector, psi: Statevector) -> float:
    """``<psi| rho |psi>`` for a pure target ``psi`` (real number in [0, 1])."""
    if isinstance(rho, Statevector):
        return float(abs(np.vdot(psi.data, rho.data)) ** 2)
    return float(np.real(np.vdot(psi.data, rho.data @ psi.data)))


# --------------------------------------------------------------------------------------------------------------------
# implementation
# --------------------------------------------------------------------------------------------------------------------
def _reduced(state: Statevector, keep: Iterable[int]) -> DensityMatrix:
    keep = sorted(set(keep))
    n = state.num_qubits
    trace_out = [q for q in range(n) if q not in keep]
    return partial_trace(state, trace_out) if trace_out else DensityMatrix(state)


def _run(circ: QuantumCircuit, qmap: list[int], cmap: list[int], branches: list, n: int) -> list:
    """Apply every instruction of ``circ`` to ``branches``. ``qmap``/``cmap`` map ``circ``'s own bit indices to the
    indices of the outermost circuit (so that control-flow bodies can be run in place)."""
    for inst in circ.data:
        op = inst.operation
        name = op.name
        qidx = [qmap[circ.find_bit(q).index] for q in inst.qubits]
        cidx = [cmap[circ.find_bit(c).index] for c in inst.clbits]
        if name in ("barrier", "delay"):
            continue
        if name == "measure":
            branches = _measure(branches, qidx[0], cidx[0], n)
        elif name == "reset":
            branches = _reset(branches, qidx[0], n)
        elif isinstance(op, IfElseOp):
            branches = _if_else(circ, op, inst, qmap, cmap, branches, n)
        elif isinstance(op, (ForLoopOp, WhileLoopOp, SwitchCaseOp)):
            raise NotImplementedError(
                f"qiskit_fest.sim does not support the control-flow operation '{name}'. "
                "Use if_test blocks, or restructure the circuit."
            )
        else:
            branches = [(p, Statevector(d).evolve(op, qargs=qidx).data, c) for p, d, c in branches]
    return branches


def _split_by_outcome(data: np.ndarray, qubit: int, n: int):
    idx = np.arange(2**n)
    bit = (idx >> qubit) & 1
    for outcome in (0, 1):
        proj = np.where(bit == outcome, data, 0.0)
        p = float(np.vdot(proj, proj).real)
        yield outcome, p, proj


def _measure(branches: list, qubit: int, clbit: int, n: int) -> list:
    out = []
    for prob, data, clbits in branches:
        for outcome, p, proj in _split_by_outcome(data, qubit, n):
            if p * prob < PRUNE:
                continue
            new_clbits = clbits[:clbit] + (outcome,) + clbits[clbit + 1 :]
            out.append((prob * p, proj / np.sqrt(p), new_clbits))
    return out


def _reset(branches: list, qubit: int, n: int) -> list:
    out = []
    idx = np.arange(2**n)
    for prob, data, clbits in branches:
        for outcome, p, proj in _split_by_outcome(data, qubit, n):
            if p * prob < PRUNE:
                continue
            proj = proj / np.sqrt(p)
            if outcome == 1:  # flip the qubit back to |0>
                proj = proj[idx ^ (1 << qubit)]
            out.append((prob * p, proj, clbits))
    return out


def _condition_holds(circ: QuantumCircuit, condition, cmap: list[int], clbits: tuple[int, ...]) -> bool:
    try:
        target, value = condition
    except (TypeError, ValueError):
        raise NotImplementedError(
            "qiskit_fest.sim supports only (clbit, value) and (register, value) conditions in if_test, "
            "not expression-based conditions."
        ) from None
    if isinstance(target, Clbit):
        return clbits[cmap[circ.find_bit(target).index]] == int(bool(value))
    if isinstance(target, ClassicalRegister):
        reg_value = sum(clbits[cmap[circ.find_bit(bit).index]] << k for k, bit in enumerate(target))
        return reg_value == int(value)
    raise NotImplementedError(f"unsupported condition target of type {type(target).__name__}")


def _if_else(circ, op: IfElseOp, inst, qmap, cmap, branches: list, n: int) -> list:
    body_q = [qmap[circ.find_bit(q).index] for q in inst.qubits]
    body_c = [cmap[circ.find_bit(c).index] for c in inst.clbits]
    taken, not_taken = [], []
    for br in branches:
        (taken if _condition_holds(circ, op.condition, cmap, br[2]) else not_taken).append(br)
    true_body = op.blocks[0]
    false_body = op.blocks[1] if len(op.blocks) > 1 else None
    out = _run(true_body, body_q, body_c, taken, n) if taken else []
    if false_body is not None and not_taken:
        out += _run(false_body, body_q, body_c, not_taken, n)
    else:
        out += not_taken
    return out
