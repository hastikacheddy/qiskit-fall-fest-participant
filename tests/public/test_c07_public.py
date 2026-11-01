"""Public checks for Challenge 7 - The Quantum Network Cut (smoke checks on the public example graph and tiny graphs).

The expected values are worked out by hand from the conventions in the problem statement (node u = character u from the RIGHT of a
bit-string; cut value = total weight of the edges between the groups; QAOA state as defined there).
"""
import math

import numpy as np
import pytest
from qiskit.quantum_info import SparsePauliOp, Statevector

from qiskit_fest.challenges.c07_qaoa_maxcut import EXAMPLE_EDGES, EXAMPLE_NUM_NODES, EXAMPLE_OPTIMUM

pytestmark = [pytest.mark.challenge(7), pytest.mark.tier("smoke")]

N, EDGES = EXAMPLE_NUM_NODES, EXAMPLE_EDGES


# ------------------------------------------------------------------------------------------------ cut_value
@pytest.mark.covers("C07-R1")
@pytest.mark.parametrize("bits,expected", [("00000", 0.0), ("00001", 2.0), ("10000", 2.0), ("00110", 4.0), ("01100", 5.0)])
def test_cut_value_of_hand_checked_splits_of_the_public_example(impl, bits, expected):
    """node 0 alone cuts its two links (2); nodes 1 and 2 together cut 4; '01100' is optimal (5) and differs from its reversal '00110'"""
    assert impl.cut_value(bits, EDGES) == pytest.approx(expected, abs=1e-12)


@pytest.mark.covers("C07-R1")
def test_cut_value_adds_up_the_weights_of_the_cut_edges(impl):
    """a single edge of weight 2.5 is cut by '01' and '10' and not by '00' or '11'"""
    edge = [(0, 1, 2.5)]
    assert impl.cut_value("01", edge) == pytest.approx(2.5) and impl.cut_value("10", edge) == pytest.approx(2.5)
    assert impl.cut_value("00", edge) == 0 and impl.cut_value("11", edge) == 0


# ------------------------------------------------------------------------------------------------ brute_force_maxcut
@pytest.mark.covers("C07-R2")
def test_brute_force_maxcut_finds_the_known_optimum_of_the_public_example(impl):
    """maximum 5; a split and its complement are both optimal, so the list holds both"""
    value, strings = impl.brute_force_maxcut(N, EDGES)
    assert value == pytest.approx(EXAMPLE_OPTIMUM)
    assert "01100" in strings and "10011" in strings
    assert len(strings) == 4


@pytest.mark.covers("C07-R2")
def test_brute_force_maxcut_of_a_single_edge_returns_both_splits(impl):
    """one edge: value 1, optimal strings '01' and '10'"""
    value, strings = impl.brute_force_maxcut(2, [(0, 1, 1.0)])
    assert value == pytest.approx(1.0) and sorted(strings) == ["01", "10"]


# ------------------------------------------------------------------------------------------------ cost_hamiltonian
@pytest.mark.covers("C07-R3")
def test_cost_hamiltonian_is_a_pauli_operator_on_one_qubit_per_node(impl):
    """a SparsePauliOp on 5 qubits"""
    h = impl.cost_hamiltonian(N, EDGES)
    assert isinstance(h, SparsePauliOp) and h.num_qubits == N


@pytest.mark.covers("C07-R3")
def test_cost_hamiltonian_diagonal_holds_the_cut_weights(impl):
    """the matrix is diagonal; its entries are the cut values (e.g. 0 for '00000', 4 for '00110', 5 for '01100')"""
    matrix = impl.cost_hamiltonian(N, EDGES).to_matrix()
    assert np.allclose(matrix, np.diag(np.diag(matrix)), atol=1e-12)
    diagonal = np.real(np.diag(matrix))
    assert diagonal[0] == pytest.approx(0.0, abs=1e-12)
    assert diagonal[int("00110", 2)] == pytest.approx(4.0, abs=1e-12)
    assert diagonal[int("01100", 2)] == pytest.approx(5.0, abs=1e-12)
    assert diagonal.max() == pytest.approx(EXAMPLE_OPTIMUM, abs=1e-12)


# ------------------------------------------------------------------------------------------------ qaoa_circuit
@pytest.mark.covers("C07-R4")
def test_qaoa_circuit_without_layers_is_the_uniform_superposition(impl):
    """p = 0 means: only the Hadamard layer"""
    qc = impl.qaoa_circuit(3, [(0, 1, 1.0), (1, 2, 1.0)], [], [])
    assert qc.num_qubits == 3
    assert np.allclose(Statevector(qc).probabilities(), 1 / 8, atol=1e-12)


@pytest.mark.covers("C07-R4")
def test_qaoa_circuit_has_one_qubit_per_node_and_no_measurements(impl):
    """no measurements, no classical bits"""
    qc = impl.qaoa_circuit(N, EDGES, [0.4], [0.3])
    assert qc.num_qubits == N and qc.num_clbits == 0
    assert "measure" not in qc.count_ops()


@pytest.mark.covers("C07-R4")
def test_qaoa_circuit_probabilities_of_a_single_edge_follow_the_closed_form(impl):
    """one edge, p = 1: P(cut) = P('01') + P('10') = 1/2 + 1/2 sin(4 beta) sin(gamma)"""
    gamma, beta = 0.7, 0.3
    probabilities = Statevector(impl.qaoa_circuit(2, [(0, 1, 1.0)], [gamma], [beta])).probabilities()
    assert probabilities[1] + probabilities[2] == pytest.approx(0.5 + 0.5 * math.sin(4 * beta) * math.sin(gamma), abs=1e-9)


# ------------------------------------------------------------------------------------------------ qaoa_expectation
@pytest.mark.covers("C07-R5")
def test_qaoa_expectation_of_a_single_edge_follows_the_closed_form(impl):
    """<H_C> = 1/2 + 1/2 sin(4 beta) sin(gamma) for one edge of weight 1 and p = 1"""
    for gamma, beta in [(0.7, 0.3), (math.pi / 2, math.pi / 8), (1.9, 1.1)]:
        assert impl.qaoa_expectation(2, [(0, 1, 1.0)], [gamma], [beta]) == pytest.approx(0.5 + 0.5 * math.sin(4 * beta) * math.sin(gamma), abs=1e-9)


@pytest.mark.covers("C07-R5")
def test_qaoa_expectation_is_the_random_split_value_when_a_parameter_is_zero(impl):
    """gamma = 0 or beta = 0 leaves a uniform distribution: <H_C> = half the total weight = 3 for the public example"""
    assert impl.qaoa_expectation(N, EDGES, [0.0], [0.9]) == pytest.approx(3.0, abs=1e-9)
    assert impl.qaoa_expectation(N, EDGES, [1.3], [0.0]) == pytest.approx(3.0, abs=1e-9)


# ------------------------------------------------------------------------------------------------ solve_maxcut_qaoa
@pytest.mark.covers("C07-R6")
def test_solve_maxcut_qaoa_returns_consistent_numbers_for_the_public_example(impl):
    """documented keys, parameter lists of length p, a bit-string of the right length, cut and energy never above the optimum"""
    result = impl.solve_maxcut_qaoa(N, EDGES, p=1, restarts=3, seed=1)
    assert {"gammas", "betas", "expectation", "bitstring", "cut_value"} <= set(result)
    assert len(result["gammas"]) == 1 and len(result["betas"]) == 1
    assert len(result["bitstring"]) == N and set(result["bitstring"]) <= {"0", "1"}
    assert result["cut_value"] == pytest.approx(impl.cut_value(result["bitstring"], EDGES), abs=1e-12)
    assert 0 <= result["cut_value"] <= EXAMPLE_OPTIMUM + 1e-9
    assert result["expectation"] <= EXAMPLE_OPTIMUM + 1e-9


# ------------------------------------------------------------------------------------------------ bonus: optimal_cut_probability
@pytest.mark.tier("bonus")
@pytest.mark.covers("C07-R10")
def test_bonus_optimal_cut_probability_is_the_share_of_optimal_strings_for_the_uniform_state(impl):
    """no layers (uniform superposition): 4 of the 32 bit-strings of the public example are optimal, so the probability is 4/32 = 0.125"""
    assert impl.optimal_cut_probability(N, EDGES, [], []) == pytest.approx(4 / 32, abs=1e-9)
    assert impl.optimal_cut_probability(N, EDGES, [0.0], [0.9]) == pytest.approx(4 / 32, abs=1e-9)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C07-R10")
def test_bonus_optimal_cut_probability_of_a_single_edge_follows_the_closed_form(impl):
    """one edge, p = 1: both splits are optimal, so the probability is P(cut) = 1/2 + 1/2 sin(4 beta) sin(gamma)"""
    gamma, beta = 0.7, 0.3
    assert impl.optimal_cut_probability(2, [(0, 1, 1.0)], [gamma], [beta]) == pytest.approx(0.5 + 0.5 * math.sin(4 * beta) * math.sin(gamma), abs=1e-9)


# ------------------------------------------------------------------------------------------------ invalid input
@pytest.mark.covers("C07-R7")
def test_cut_value_rejects_an_invalid_bit_string_and_an_edge_outside_it(impl):
    """characters other than 0 / 1, the empty string and an endpoint beyond the bit-string raise ValueError"""
    with pytest.raises(ValueError):
        impl.cut_value("0120", EDGES)
    with pytest.raises(ValueError):
        impl.cut_value("", [])
    with pytest.raises(ValueError):
        impl.cut_value("01", [(0, 5, 1.0)])


@pytest.mark.covers("C07-R7")
def test_brute_force_maxcut_rejects_a_self_loop(impl):
    """an edge from a node to itself is not a valid link"""
    with pytest.raises(ValueError):
        impl.brute_force_maxcut(3, [(1, 1, 1.0)])


@pytest.mark.covers("C07-R7")
def test_cost_hamiltonian_rejects_a_self_loop(impl):
    """an edge from a node to itself is not a valid link"""
    with pytest.raises(ValueError):
        impl.cost_hamiltonian(3, [(1, 1, 1.0)])


@pytest.mark.covers("C07-R7")
def test_qaoa_circuit_rejects_parameter_lists_of_different_length(impl):
    """gammas and betas must have the same length"""
    with pytest.raises(ValueError):
        impl.qaoa_circuit(3, [(0, 1, 1.0)], [0.1, 0.2], [0.3])


@pytest.mark.covers("C07-R7")
def test_qaoa_expectation_rejects_parameter_lists_of_different_length(impl):
    """gammas and betas must have the same length"""
    with pytest.raises(ValueError):
        impl.qaoa_expectation(3, [(0, 1, 1.0)], [0.1], [0.3, 0.4])


@pytest.mark.covers("C07-R7")
def test_solve_maxcut_qaoa_rejects_a_depth_below_one(impl):
    """p = 0 is not a valid depth for the optimiser"""
    with pytest.raises(ValueError):
        impl.solve_maxcut_qaoa(3, [(0, 1, 1.0)], p=0)
