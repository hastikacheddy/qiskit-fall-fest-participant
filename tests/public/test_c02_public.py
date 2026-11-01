"""Public checks for Challenge 2 - The Entanglement Detective (smoke checks only; hidden tests use many more states)."""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

pytestmark = [pytest.mark.challenge(2), pytest.mark.tier("smoke")]

R = 1 / np.sqrt(2)
BELL = Statevector([R, 0, 0, R])
ZERO = Statevector([1, 0, 0, 0])


@pytest.mark.covers("C02-R1")
def test_bell_circuit_prepares_the_bell_state(impl):
    """bell_circuit() prepares (|00> + |11>)/sqrt(2)"""
    qc = impl.bell_circuit()
    assert isinstance(qc, QuantumCircuit) and qc.num_qubits == 2, "bell_circuit() must return a two-qubit QuantumCircuit"
    assert "measure" not in qc.count_ops(), "use gates only - no measurements"
    assert Statevector(qc).equiv(BELL, atol=1e-9), "the circuit does not prepare (|00> + |11>)/sqrt(2)"


@pytest.mark.covers("C02-R2")
def test_bell_circuit_is_not_two_independent_coins(impl):
    """the Bell circuit is not the independent superposition H (x) H"""
    overlap = abs(np.vdot(Statevector(impl.bell_circuit()).data, [0.5] * 4)) ** 2
    assert overlap < 0.9, "your state looks like two independent coins, not an entangled pair"


@pytest.mark.covers("C02-R3")
def test_joint_probabilities_of_the_bell_state(impl):
    """joint_probabilities lists all four outcomes of the Bell state"""
    out = impl.joint_probabilities(BELL)
    assert set(out) == {"00", "01", "10", "11"}, "include every bit-string, also the impossible ones"
    assert all(abs(out[k] - v) < 1e-9 for k, v in {"00": 0.5, "01": 0.0, "10": 0.0, "11": 0.5}.items())


@pytest.mark.covers("C02-R4")
def test_correlation_in_basis_of_the_bell_state(impl):
    """the Bell state is perfectly correlated in Z and in X"""
    assert abs(impl.correlation_in_basis(BELL, "Z") - 1) < 1e-9
    assert abs(impl.correlation_in_basis(BELL, "X") - 1) < 1e-9


@pytest.mark.covers("C02-R5")
def test_is_entangled_on_two_basic_cases(impl):
    """is_entangled says True for the Bell state and False for |00>"""
    assert impl.is_entangled(BELL) is True
    assert impl.is_entangled(ZERO) is False


@pytest.mark.covers("C02-R6")
def test_correlation_in_basis_rejects_an_unknown_basis(impl):
    """correlation_in_basis raises ValueError for an unknown basis"""
    with pytest.raises(ValueError):
        impl.correlation_in_basis(BELL, "Q")


@pytest.mark.tier("bonus")
@pytest.mark.covers("C02-R7")
def test_bonus_chsh_value_of_the_bell_state(impl):
    """(bonus) the Bell state reaches the quantum CHSH maximum 2*sqrt(2)"""
    assert abs(impl.chsh_value(BELL) - 2 * np.sqrt(2)) < 1e-9
