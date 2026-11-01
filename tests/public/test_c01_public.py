"""Public checks for Challenge 1 - Superposition Under the Microscope.

These are *smoke* checks: they use only the published example inputs. The instructors run additional hidden tests with
many other inputs and edge cases, so passing these is necessary but not sufficient.
"""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from qiskit_fest.challenges.c01_superposition import EXAMPLE_AMPLITUDES, EXAMPLE_PROBABILITIES

pytestmark = [pytest.mark.challenge(1), pytest.mark.tier("smoke")]


@pytest.mark.covers("C01-R1")
def test_superposition_circuit_is_a_one_qubit_circuit_without_measurements(impl):
    """superposition_circuit() returns a one-qubit circuit without measurements"""
    qc = impl.superposition_circuit()
    assert isinstance(qc, QuantumCircuit), "superposition_circuit() must return a QuantumCircuit"
    assert qc.num_qubits == 1, "the circuit must have exactly one qubit"
    assert "measure" not in qc.count_ops(), "do not add measurements - we look at the state vector"


@pytest.mark.covers("C01-R2")
def test_superposition_circuit_gives_fifty_fifty(impl):
    """superposition_circuit() gives P(0) = P(1) = 1/2"""
    probs = Statevector(impl.superposition_circuit()).probabilities()
    assert np.allclose(probs, [0.5, 0.5], atol=1e-9), "the outcome probabilities are not (0.5, 0.5)"


@pytest.mark.covers("C01-R3")
def test_born_probabilities_worked_example(impl):
    """born_probabilities reproduces the worked example (0.6, 0.8i) -> (0.36, 0.64)"""
    out = np.asarray(impl.born_probabilities(EXAMPLE_AMPLITUDES))
    assert out.shape == (2,), "the result must have one entry per amplitude"
    assert np.allclose(out, EXAMPLE_PROBABILITIES, atol=1e-9), "probabilities are |amplitude|^2"


@pytest.mark.covers("C01-R4")
def test_born_probabilities_rejects_an_unnormalised_vector(impl):
    """born_probabilities raises ValueError for a vector that is not normalised"""
    with pytest.raises(ValueError):
        impl.born_probabilities([1.0, 1.0])


@pytest.mark.covers("C01-R5")
def test_exact_probabilities_of_an_x_gate(impl):
    """exact_probabilities of an X gate on qubit 0 of two qubits is [0, 1, 0, 0]"""
    qc = QuantumCircuit(2)
    qc.x(0)
    out = np.asarray(impl.exact_probabilities(qc))
    assert np.allclose(out, [0, 1, 0, 0], atol=1e-9), "index i is the bit-string with integer value i (qubit 0 = least significant)"


@pytest.mark.covers("C01-R6")
def test_exact_probabilities_rejects_measurements(impl):
    """exact_probabilities raises ValueError for a circuit that measures"""
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()
    with pytest.raises(ValueError):
        impl.exact_probabilities(qc)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C01-R7")
def test_bonus_circuit_for_probability_example(impl):
    """(bonus) circuit_for_probability(0.2) gives P(0) = 0.2"""
    probs = Statevector(impl.circuit_for_probability(0.2)).probabilities()
    assert np.allclose(probs, [0.2, 0.8], atol=1e-9)
