"""Public checks for Challenge 5 - Find the Hidden State (smoke checks on the public example "110" and tiny cases only).

The expected operators are written down from the problem statement (a sign flip, and the reflection 2|s><s| - I); no check
here depends on *how* you build your circuits - only on the unitary they implement.
"""
import numpy as np
import pytest
from qiskit.quantum_info import Operator

from qiskit_fest.challenges.c05_grover import EXAMPLE_MARKED, success_probability, theoretical_success

pytestmark = [pytest.mark.challenge(5), pytest.mark.tier("smoke")]


def _sign_flip(*marked):
    """diag(+1, ..., -1 at the marked indices, ..., +1)"""
    n = len(marked[0])
    d = np.ones(2**n)
    for m in marked:
        d[int(m, 2)] = -1
    return Operator(np.diag(d))


def _inversion_about_the_mean(n):
    s = np.full(2**n, 2 ** (-n / 2))
    return Operator(2 * np.outer(s, s) - np.eye(2**n))


@pytest.mark.covers("C05-R1")
def test_phase_oracle_flips_the_sign_of_the_public_example(impl):
    """the oracle for "110" flips the sign of the amplitude of |110> (index 6) and of nothing else"""
    qc = impl.phase_oracle(EXAMPLE_MARKED)
    assert Operator(qc).equiv(_sign_flip(EXAMPLE_MARKED), atol=1e-9), (
        "the unitary is not 'minus one on the marked basis state, plus one elsewhere' - check the bit order and the final X gates")


@pytest.mark.covers("C05-R1")
def test_phase_oracle_uses_only_the_data_qubits_and_no_measurements(impl):
    """the oracle for a 3-bit string acts on exactly 3 qubits (no ancillas) and has no classical bits"""
    qc = impl.phase_oracle(EXAMPLE_MARKED)
    assert qc.num_qubits == 3 and qc.num_clbits == 0
    assert "measure" not in qc.count_ops()


@pytest.mark.covers("C05-R5")
def test_phase_oracle_rejects_an_invalid_marked_string(impl):
    """a string that is not made of 0 and 1 raises ValueError"""
    with pytest.raises(ValueError):
        impl.phase_oracle("12")


@pytest.mark.covers("C05-R2")
def test_diffuser_for_three_qubits_is_the_inversion_about_the_mean(impl):
    """for three qubits the diffuser is 2|s><s| - I (up to a global phase)"""
    assert Operator(impl.diffuser(3)).equiv(_inversion_about_the_mean(3), atol=1e-9), (
        "the unitary is not the reflection about the uniform superposition")


@pytest.mark.covers("C05-R5")
def test_diffuser_rejects_a_size_below_one(impl):
    """n = 0 raises ValueError"""
    with pytest.raises(ValueError):
        impl.diffuser(0)


@pytest.mark.covers("C05-R3")
def test_optimal_iterations_matches_the_values_in_the_problem_statement(impl):
    """N = 8 -> 2 iterations, N = 16 -> 3 iterations (one marked state; num_marked defaults to 1)"""
    assert impl.optimal_iterations(3) == 2
    assert impl.optimal_iterations(4) == 3


@pytest.mark.covers("C05-R5")
def test_optimal_iterations_rejects_invalid_arguments(impl):
    """num_marked = 0 raises ValueError"""
    with pytest.raises(ValueError):
        impl.optimal_iterations(3, 0)


@pytest.mark.covers("C05-R4")
def test_grover_circuit_amplifies_the_public_example(impl):
    """with the default number of iterations the marked string is measured with probability above 94 %"""
    p = success_probability(impl.grover_circuit(EXAMPLE_MARKED), EXAMPLE_MARKED)
    assert p > 0.94, f"success probability is only {p:.3f}"


@pytest.mark.covers("C05-R4")
@pytest.mark.parametrize("iterations", [0, 1, 2, 3, 4])
def test_grover_circuit_follows_the_theory_curve_for_the_public_example(impl, iterations):
    """the success probability after k iterations equals sin^2((2k+1) theta), also beyond the optimum"""
    p = success_probability(impl.grover_circuit(EXAMPLE_MARKED, iterations), EXAMPLE_MARKED)
    assert abs(p - theoretical_success(3, 1, iterations)) < 1e-9


@pytest.mark.covers("C05-R5")
def test_grover_circuit_for_the_public_example_has_three_qubits_and_no_measurements(impl):
    """the circuit has one qubit per bit of the marked string and no measurements or classical bits"""
    qc = impl.grover_circuit(EXAMPLE_MARKED)
    assert qc.num_qubits == 3 and qc.num_clbits == 0
    assert "measure" not in qc.count_ops()


@pytest.mark.covers("C05-R5")
def test_grover_circuit_rejects_invalid_arguments(impl):
    """an empty marked string and a negative iteration count raise ValueError"""
    with pytest.raises(ValueError):
        impl.grover_circuit("")
    with pytest.raises(ValueError):
        impl.grover_circuit("101", -1)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C05-R6")
def test_bonus_multi_oracle_flips_every_listed_state(impl):
    """the bonus oracle for ["011", "101"] flips the sign of exactly the amplitudes of |011> and |101>"""
    qc = impl.phase_oracle_multi(["011", "101"])
    assert qc.num_qubits == 3
    assert Operator(qc).equiv(_sign_flip("011", "101"), atol=1e-9)
