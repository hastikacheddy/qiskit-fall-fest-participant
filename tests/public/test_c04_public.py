"""Public checks for Challenge 4 - Teleport the Qubit (smoke checks on the public example states only).

The Bell pair is prepared with ``prepare_state`` here (not with gates), so reading this file does not give away Part 1.
"""
import numpy as np
import pytest
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.quantum_info import Statevector

from qiskit_fest.challenges.c04_teleportation import EXAMPLE_STATES, assemble, branch_report, prep_circuit
from qiskit_fest.sim import exact_branches, fidelity_with_pure

pytestmark = [pytest.mark.challenge(4), pytest.mark.tier("smoke")]

R = 1 / np.sqrt(2)
PHI_PLUS = [R, 0, 0, R]
PSI = EXAMPLE_STATES["generic"]


def _frame(psi, z, x):
    """X^x Z^z |psi>"""
    qc = QuantumCircuit(1)
    if z:
        qc.z(0)
    if x:
        qc.x(0)
    return psi.evolve(qc)


@pytest.mark.covers("C04-R1")
def test_create_bell_pair_makes_phi_plus_on_the_named_qubits(impl):
    """create_bell_pair(qc, 1, 2) puts qubits 1 and 2 into (|00> + |11>)/sqrt(2) and leaves qubit 0 alone"""
    qc = QuantumCircuit(3)
    impl.create_bell_pair(qc, 1, 2)
    expected = Statevector(PHI_PLUS).tensor(Statevector.from_label("0"))  # qubits (2, 1) = Phi+, qubit 0 = |0>
    assert Statevector(qc).equiv(expected, atol=1e-9), "qubits 1 and 2 are not in the Bell state (or qubit 0 was disturbed)"


def _alice_circuit(impl, psi):
    qc = QuantumCircuit(QuantumRegister(3, "q"), ClassicalRegister(1, "mz"), ClassicalRegister(1, "mx"))
    qc.prepare_state(psi.data, 0)
    qc.prepare_state(PHI_PLUS, [1, 2])
    impl.alice_bell_measurement(qc, 0, 1, qc.cregs[0][0], qc.cregs[1][0])
    return qc


@pytest.mark.covers("C04-R2")
def test_alice_bell_measurement_has_four_equally_likely_outcomes(impl):
    """after Alice's Bell-basis measurement there are four outcomes, each with probability 1/4"""
    branches = exact_branches(_alice_circuit(impl, PSI))
    assert len(branches) == 4, "expected four measurement outcomes (did you measure both qubits?)"
    assert all(abs(b.probability - 0.25) < 1e-9 for b in branches)


@pytest.mark.covers("C04-R2")
def test_alice_bell_measurement_leaves_bob_with_a_pauli_scrambled_state(impl):
    """in the branch with bits (z, x) Bob holds X^x Z^z |psi>"""
    qc = _alice_circuit(impl, PSI)
    for br in exact_branches(qc):
        z, x = br.register_value(qc, "mz"), br.register_value(qc, "mx")
        assert fidelity_with_pure(br.reduced_state([2]), _frame(PSI, z, x)) > 1 - 1e-9, (
            f"for (z, x) = ({z}, {x}) Bob's qubit is not X^x Z^z|psi> - check CNOT direction, the Hadamard and which bit is which")


def _bob_circuit(impl, psi, z, x, bob=2):
    helpers = [i for i in range(3) if i != bob]
    qc = QuantumCircuit(QuantumRegister(3, "q"), ClassicalRegister(1, "mz"), ClassicalRegister(1, "mx"))
    qc.prepare_state(psi.data, bob)
    if z:
        qc.z(bob)
    if x:
        qc.x(bob)
    if z:
        qc.x(helpers[0])
    if x:
        qc.x(helpers[1])
    qc.measure(helpers[0], qc.cregs[0][0])
    qc.measure(helpers[1], qc.cregs[1][0])
    impl.bob_correction(qc, bob, qc.cregs[0][0], qc.cregs[1][0])
    return qc


@pytest.mark.covers("C04-R3")
@pytest.mark.parametrize("z,x", [(0, 0), (0, 1), (1, 0), (1, 1)])
def test_bob_correction_restores_the_message_for_each_classical_outcome(impl, z, x):
    """for each of the four classical outcomes Bob's qubit is brought back to |psi>"""
    (branch,) = exact_branches(_bob_circuit(impl, PSI, z, x))
    assert fidelity_with_pure(branch.reduced_state([2]), PSI) > 1 - 1e-9, "Bob's qubit is not restored for this outcome"


@pytest.mark.covers("C04-R4")
@pytest.mark.parametrize("name", list(EXAMPLE_STATES))
def test_protocol_teleports_the_public_example_states(impl, name):
    """the assembled protocol delivers each public example state with fidelity 1 in every branch"""
    psi = EXAMPLE_STATES[name]
    circuit = assemble(prep_circuit(psi), impl.create_bell_pair, impl.alice_bell_measurement, impl.bob_correction)
    rows = branch_report(circuit, psi)
    assert len(rows) == 4
    assert all(f > 1 - 1e-9 for _, _, f in rows), "some branch does not deliver the message"


@pytest.mark.covers("C04-R5")
def test_create_bell_pair_rejects_invalid_qubit_indices(impl):
    """create_bell_pair with equal indices raises ValueError (or Qiskit's CircuitError)"""
    from qiskit.circuit.exceptions import CircuitError

    with pytest.raises((ValueError, CircuitError)):
        impl.create_bell_pair(QuantumCircuit(3), 1, 1)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C04-R6")
def test_bonus_bob_alone_learns_nothing(impl):
    """(bonus) without the classical bits Bob's averaged state is maximally mixed"""
    rho = impl.average_bob_state_without_correction(prep_circuit(PSI))
    assert np.allclose(np.asarray(rho.data), np.eye(2) / 2, atol=1e-9)
