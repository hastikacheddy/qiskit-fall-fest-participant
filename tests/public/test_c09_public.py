"""Public checks for Challenge 9 - Protect the Logical Qubit (smoke checks on basis states and the public examples).

All simulations are exact. The recovery checks use the provided harness (``run_recovery``), which builds: prepare the logical
state on qubit 0, encode, apply the error, then call ``add_feedforward_correction`` on a 5-qubit circuit with a 2-bit register.
"""
import numpy as np
import pytest
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Operator, Statevector

from qiskit_fest.challenges.c09_error_correction import LOGICAL_STATES, code_state, run_recovery

pytestmark = [pytest.mark.challenge(9), pytest.mark.tier("smoke")]

ALPHA, BETA = LOGICAL_STATES["generic"]


# ------------------------------------------------------------------------------------------------ encode_circuit
@pytest.mark.covers("C09-R1")
def test_encode_circuit_maps_the_basis_states_to_the_code_words(impl):
    """|0> on qubit 0 becomes |000>; |1> on qubit 0 becomes |111> (qubits 1 and 2 start in |00>)"""
    qc = impl.encode_circuit()
    assert qc.num_qubits == 3
    assert Statevector.from_label("000").evolve(qc).equiv(Statevector.from_label("000"), atol=1e-9)
    assert Statevector.from_label("001").evolve(qc).equiv(Statevector.from_label("111"), atol=1e-9)


@pytest.mark.covers("C09-R1")
def test_encode_circuit_spreads_a_superposition_over_the_two_code_words(impl):
    """alpha|0> + beta|1> becomes alpha|000> + beta|111> - an entangled state, not three copies"""
    start = Statevector.from_label("00").tensor(Statevector([ALPHA, BETA]))
    assert start.evolve(impl.encode_circuit()).equiv(code_state(ALPHA, BETA), atol=1e-9)


# ------------------------------------------------------------------------------------------------ syndrome_circuit
@pytest.mark.covers("C09-R2")
@pytest.mark.parametrize("data,expected", [(0b000, 0b00000), (0b001, 0b01001), (0b010, 0b11010), (0b111, 0b00111)])
def test_syndrome_circuit_writes_the_parities_into_the_ancillas(impl, data, expected):
    """data bits (q2 q1 q0): 001 -> parities (1, 0), 010 -> (1, 1), 111 and 000 -> (0, 0); ancillas are qubits 3 and 4"""
    out = Statevector.from_int(data, 32).evolve(impl.syndrome_circuit())
    assert out.equiv(Statevector.from_int(expected, 32), atol=1e-9)


@pytest.mark.covers("C09-R2")
def test_syndrome_circuit_acts_on_five_qubits_and_does_not_measure(impl):
    """three data qubits and two ancillas; no measurement and no classical bits (the measurement is part of the feed-forward step)"""
    qc = impl.syndrome_circuit()
    assert qc.num_qubits == 5 and qc.num_clbits == 0
    assert "measure" not in qc.count_ops()


# ------------------------------------------------------------------------------------------------ decode_syndrome
@pytest.mark.covers("C09-R3")
def test_decode_syndrome_recognises_no_error_and_a_flip_of_the_middle_qubit(impl):
    """(0, 0) means no error (None, not 0); (1, 1) - both parities violated - points to the middle qubit"""
    assert impl.decode_syndrome((0, 0)) is None
    assert impl.decode_syndrome((1, 1)) == 1


@pytest.mark.covers("C09-R6")
def test_decode_syndrome_rejects_a_three_bit_syndrome(impl):
    """a syndrome has exactly two bits"""
    with pytest.raises(ValueError):
        impl.decode_syndrome((0, 1, 0))


# ------------------------------------------------------------------------------------------------ correction_circuit
@pytest.mark.covers("C09-R4")
def test_correction_circuit_applies_x_to_the_requested_qubit_and_nothing_for_none(impl):
    """correction_circuit(2) flips qubit 2 (|000> -> |100>); correction_circuit(None) changes nothing"""
    flip = impl.correction_circuit(2)
    assert flip.num_qubits == 3
    assert Statevector.from_label("000").evolve(flip).equiv(Statevector.from_label("100"), atol=1e-9)
    assert Operator(impl.correction_circuit(None)).equiv(Operator(np.eye(8)), atol=1e-9)


@pytest.mark.covers("C09-R6")
def test_correction_circuit_rejects_an_invalid_qubit(impl):
    """only None, 0, 1 and 2 are valid"""
    with pytest.raises(ValueError):
        impl.correction_circuit(3)


# ------------------------------------------------------------------------------------------------ add_feedforward_correction
@pytest.mark.covers("C09-R5")
def test_add_feedforward_correction_repairs_a_bit_flip_on_the_middle_qubit(impl):
    """X error on data qubit 1: one measurement branch (syndrome register value 3 = s0 + 2 s1 with s0 = s1 = 1), the data return to the code word"""
    result = run_recovery(impl.encode_circuit, impl.add_feedforward_correction, (ALPHA, BETA), [("X", 1)])
    assert result["min_fidelity"] > 1 - 1e-9
    assert [(s, round(p, 9)) for s, p, _ in result["branches"]] == [(3, 1.0)]


@pytest.mark.covers("C09-R5")
def test_add_feedforward_correction_leaves_a_clean_code_word_alone(impl):
    """no error: syndrome 0 with probability 1, no correction applied"""
    result = run_recovery(impl.encode_circuit, impl.add_feedforward_correction, (ALPHA, BETA), [])
    assert result["min_fidelity"] > 1 - 1e-9
    assert [(s, round(p, 9)) for s, p, _ in result["branches"]] == [(0, 1.0)]


@pytest.mark.covers("C09-R6")
def test_add_feedforward_correction_rejects_a_register_that_is_not_part_of_the_circuit(impl):
    """the 2-bit register must have been added to the circuit"""
    qc = QuantumCircuit(QuantumRegister(5, "q"))
    with pytest.raises(ValueError):
        impl.add_feedforward_correction(qc, [0, 1, 2], [3, 4], ClassicalRegister(2, "syn"))


# ------------------------------------------------------------------------------------------------ bonus
@pytest.mark.tier("bonus")
@pytest.mark.covers("C09-R8")
def test_bonus_phase_flip_code_words_are_the_plus_and_minus_states(impl):
    """|0> on qubit 0 becomes |+++>; |1> on qubit 0 becomes |--->"""
    qc = impl.phase_flip_encode_circuit()
    assert qc.num_qubits == 3
    plus, minus = Statevector.from_label("+++"), Statevector.from_label("---")
    assert Statevector.from_label("000").evolve(qc).equiv(plus, atol=1e-9)
    assert Statevector.from_label("001").evolve(qc).equiv(minus, atol=1e-9)
