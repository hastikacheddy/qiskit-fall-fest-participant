"""Public checks for Challenge 10 - The Hardware Architect (smoke checks on tiny hand-counted circuits and the reference circuit).

Equivalence of a transpiled circuit is judged with ``Operator.from_circuit``, which takes the layout and the routing permutation
recorded in ``circuit.layout`` into account (up to a global phase).
"""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from qiskit_fest.challenges.c10_transpilation import BASIS_GATES, LINE6, baseline_transpile, line_edges, reference_circuit

pytestmark = [pytest.mark.challenge(10), pytest.mark.tier("smoke")]

LINE3 = line_edges(3)


# ------------------------------------------------------------------------------------------------ circuit_cost
@pytest.mark.covers("C10-R1")
def test_circuit_cost_of_a_hand_counted_circuit(impl):
    """h, cx, cx, barrier, x, measure: 4 gates (the barrier and the measurement are not gates), 2 of them two-qubit gates, depth 5"""
    qc = QuantumCircuit(3, 1)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.barrier()
    qc.x(2)
    qc.measure(2, 0)
    assert impl.circuit_cost(qc) == {"depth": 5, "two_qubit_gates": 2, "total_gates": 4}


@pytest.mark.covers("C10-R1")
def test_circuit_cost_does_not_count_a_two_qubit_barrier_as_a_two_qubit_gate(impl):
    """a barrier on two qubits is a directive, not a gate; parallel gates share one layer of depth"""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.h(1)
    qc.barrier(0, 1)
    qc.cz(0, 1)
    cost = impl.circuit_cost(qc)
    assert cost["two_qubit_gates"] == 1 and cost["total_gates"] == 3 and cost["depth"] == 2


# ------------------------------------------------------------------------------------------------ is_hardware_valid
@pytest.mark.covers("C10-R2")
def test_is_hardware_valid_accepts_basis_gates_on_coupled_qubits(impl):
    """rz, sx and cx on neighbouring qubits of a three-qubit line (cx in the reverse direction is fine)"""
    qc = QuantumCircuit(3)
    qc.rz(0.3, 0)
    qc.sx(1)
    qc.cx(0, 1)
    qc.cx(2, 1)
    assert impl.is_hardware_valid(qc, LINE3, BASIS_GATES) is True


@pytest.mark.covers("C10-R2")
def test_is_hardware_valid_rejects_a_two_qubit_gate_on_uncoupled_qubits(impl):
    """cx(0, 2) on a line 0-1-2 needs a SWAP: the circuit does not fit"""
    qc = QuantumCircuit(3)
    qc.cx(0, 2)
    assert impl.is_hardware_valid(qc, LINE3, BASIS_GATES) is False


@pytest.mark.covers("C10-R2")
def test_is_hardware_valid_rejects_a_gate_outside_the_basis(impl):
    """the Hadamard is not a native gate"""
    qc = QuantumCircuit(3)
    qc.h(0)
    assert impl.is_hardware_valid(qc, LINE3, BASIS_GATES) is False


# ------------------------------------------------------------------------------------------------ optimize_for_hardware
@pytest.mark.covers("C10-R3")
def test_optimize_for_hardware_returns_a_circuit_that_fits_the_chip(impl):
    """valid for the line and the native gates"""
    optimised = impl.optimize_for_hardware(reference_circuit(), LINE6, BASIS_GATES, seed=0)
    assert impl.is_hardware_valid(optimised, LINE6, BASIS_GATES)


@pytest.mark.covers("C10-R4")
def test_optimize_for_hardware_still_implements_the_same_unitary(impl):
    """Operator.from_circuit (which applies the recorded layout) equals the original unitary up to a global phase"""
    original = reference_circuit()
    optimised = impl.optimize_for_hardware(original, LINE6, BASIS_GATES, seed=0)
    assert Operator.from_circuit(optimised).equiv(Operator(original), atol=1e-8)


@pytest.mark.covers("C10-R5")
def test_optimize_for_hardware_is_reproducible_for_a_fixed_seed(impl):
    """the same arguments give the same circuit"""
    a = impl.optimize_for_hardware(reference_circuit(), LINE6, BASIS_GATES, seed=3)
    b = impl.optimize_for_hardware(reference_circuit(), LINE6, BASIS_GATES, seed=3)
    assert a == b


@pytest.mark.covers("C10-R7")
def test_optimize_for_hardware_is_not_worse_than_the_baseline_on_the_reference_circuit(impl):
    """never more two-qubit gates than the baseline transpilation (lowest optimisation level)"""
    original = reference_circuit()
    baseline = impl.circuit_cost(baseline_transpile(original, LINE6, BASIS_GATES, 0))["two_qubit_gates"]
    assert impl.circuit_cost(impl.optimize_for_hardware(original, LINE6, BASIS_GATES, seed=0))["two_qubit_gates"] <= baseline


@pytest.mark.covers("C10-R6")
def test_optimize_for_hardware_rejects_an_empty_coupling_map(impl):
    """no couplings, no chip: ValueError"""
    with pytest.raises(ValueError):
        impl.optimize_for_hardware(reference_circuit(), [], BASIS_GATES, seed=0)


# ------------------------------------------------------------------------------------------------ cost_reduction
@pytest.mark.covers("C10-R10")
def test_cost_reduction_known_values(impl):
    """10 -> 6 two-qubit gates is a 40 % saving, no change is 0, a worse circuit gives a negative number"""
    before, after = {"depth": 20, "two_qubit_gates": 10, "total_gates": 40}, {"depth": 12, "two_qubit_gates": 6, "total_gates": 30}
    assert impl.cost_reduction(before, after) == pytest.approx(0.4)
    assert impl.cost_reduction(before, before) == pytest.approx(0.0)
    assert impl.cost_reduction(after, before) == pytest.approx(-2 / 3)
    assert impl.cost_reduction(before, after, "depth") == pytest.approx(0.4)


@pytest.mark.covers("C10-R6")
def test_cost_reduction_rejects_an_unknown_metric(impl):
    """only depth, two_qubit_gates and total_gates exist"""
    cost = {"depth": 1, "two_qubit_gates": 1, "total_gates": 1}
    with pytest.raises(ValueError):
        impl.cost_reduction(cost, cost, "fidelity")


# ------------------------------------------------------------------------------------------------ bonus
@pytest.mark.tier("bonus")
@pytest.mark.covers("C10-R9")
def test_bonus_ghz_chain_uses_n_minus_one_cnots_between_neighbours(impl):
    """five qubits: four CNOTs, each between neighbouring qubits, preparing the GHZ state"""
    qc = impl.ghz_chain_rewrite(5)
    cnots = [tuple(sorted(qc.find_bit(q).index for q in inst.qubits)) for inst in qc.data if inst.operation.name == "cx"]
    assert len(cnots) == 4 and all(b - a == 1 for a, b in cnots)
    ghz = np.zeros(32, dtype=complex)
    ghz[0] = ghz[31] = 2 ** -0.5
    assert Statevector(qc).equiv(Statevector(ghz), atol=1e-9)
