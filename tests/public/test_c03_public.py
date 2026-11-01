"""Public checks for Challenge 3 - Gate Surgeon (smoke checks; hidden tests try many more angles and inputs)."""
import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from qiskit_fest.challenges.c03_gate_surgeon import GHZ_TARGET, SWAP_TARGET, tilted_target
from qiskit_fest.sim import measured_distribution

pytestmark = [pytest.mark.challenge(3), pytest.mark.tier("smoke")]


@pytest.mark.covers("C03-R1")
def test_patient_ghz_prepares_the_ghz_state(impl):
    """patient_ghz() prepares (|000> + |111>)/sqrt(2)"""
    qc = impl.patient_ghz()
    assert isinstance(qc, QuantumCircuit) and qc.num_qubits == 3, "patient_ghz() must return a three-qubit circuit"
    assert Statevector(qc).equiv(GHZ_TARGET, atol=1e-9), "the circuit does not prepare the GHZ state (compare with describe_state)"


@pytest.mark.covers("C03-R2")
def test_patient_swap_is_a_cx_only_swap(impl):
    """patient_swap() uses only CX gates and equals SWAP"""
    qc = impl.patient_swap()
    ops = {k for k in qc.count_ops() if k != "barrier"}
    assert ops <= {"cx"}, "only CX gates are allowed"
    assert Operator(qc).equiv(SWAP_TARGET, atol=1e-9), "the circuit is not the SWAP unitary"


@pytest.mark.covers("C03-R3")
def test_patient_tilted_pair_at_pi_over_two(impl):
    """patient_tilted_pair(pi/2) prepares (|00> + |11>)/sqrt(2)"""
    assert Statevector(impl.patient_tilted_pair(np.pi / 2)).equiv(tilted_target(np.pi / 2), atol=1e-9)


@pytest.mark.covers("C03-R4")
def test_patient_tilted_pair_rejects_nan(impl):
    """patient_tilted_pair raises ValueError for theta = nan"""
    with pytest.raises(ValueError):
        impl.patient_tilted_pair(float("nan"))


@pytest.mark.tier("bonus")
@pytest.mark.covers("C03-R5")
def test_bonus_patient_readout_gives_110(impl):
    """(bonus) patient_readout() yields the bit-string 110 with certainty"""
    dist = measured_distribution(impl.patient_readout())
    assert dist.get("110", 0) == pytest.approx(1.0, abs=1e-9), "the measured bit-string should be 110"
