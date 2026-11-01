"""Public checks for Challenge 6 - Fight the Noise (smoke checks on the public baseline circuit).

Each part is checked in isolation: the tests that need a noise model use a tiny *readout-only* model built here, never your
``build_noise_model``, so a bug in Part 1 cannot make Part 2 look broken. Statistical checks use exact binomial intervals
(a correct implementation fails one with probability below 1e-7) and fixed seeds.

Qiskit Aer is imported inside the helpers so that the file can be collected (and the tests skipped) without Aer installed.
"""
import numpy as np
import pytest

from qiskit_fest.challenges.c06_noise import DOCUMENTED_NOISE, baseline_circuit, probe_readout, probe_x_gate

pytestmark = [pytest.mark.challenge(6), pytest.mark.tier("smoke"), pytest.mark.needs_aer]

GHZ = baseline_circuit(3)
ALPHA = 1e-7


def readout_only_model(r):
    """A noise model with nothing but a symmetric readout error r (independent of your solution)."""
    from qiskit_aer.noise import NoiseModel, ReadoutError

    model = NoiseModel()
    model.add_all_qubit_readout_error(ReadoutError([[1 - r, r], [r, 1 - r]]))
    return model


def within_binomial(count, shots, p):
    from scipy import stats

    lo, hi = stats.binom.interval(1 - ALPHA, shots, p)
    return lo <= count <= hi


# ------------------------------------------------------------------------------------------------ build_noise_model
@pytest.mark.covers("C06-R1")
def test_build_noise_model_returns_a_noise_model_that_is_not_ideal(impl):
    """the documented parameters give a qiskit_aer NoiseModel that contains errors"""
    from qiskit_aer.noise import NoiseModel

    model = impl.build_noise_model(**DOCUMENTED_NOISE)
    assert isinstance(model, NoiseModel)
    assert not model.is_ideal()


@pytest.mark.covers("C06-R1")
def test_build_noise_model_depolarises_the_x_gate_as_documented(impl):
    """with p1 = 0.2 one x gate leaves |1> with exact probability 1 - p1/2 = 0.9 (density-matrix simulation, no shots)"""
    model = impl.build_noise_model(0.2, 0.0, 0.0)
    assert probe_x_gate(model) == pytest.approx(0.9, abs=1e-9)


@pytest.mark.covers("C06-R1")
def test_build_noise_model_readout_error_flips_zero_to_one_with_probability_p_readout(impl):
    """with p_readout = 0.1 a measured |0> is read as 1 in 10 % of 20000 shots (exact binomial interval)"""
    model = impl.build_noise_model(0.0, 0.0, 0.1)
    assert within_binomial(round(probe_readout(model, shots=20000, seed=7) * 20000), 20000, 0.1)


@pytest.mark.covers("C06-R6")
def test_build_noise_model_rejects_a_probability_above_one(impl):
    """a parameter outside [0, 1] raises ValueError"""
    with pytest.raises(ValueError):
        impl.build_noise_model(0.01, 1.5, 0.01)


# ------------------------------------------------------------------------------------------------ run_counts
@pytest.mark.covers("C06-R2")
def test_run_counts_counts_add_up_to_the_shots(impl):
    """the histogram has one entry per observed 3-bit string and its counts sum to the number of shots"""
    counts = impl.run_counts(GHZ, readout_only_model(0.05), shots=1000, seed=3)
    assert isinstance(counts, dict) and sum(counts.values()) == 1000
    assert all(len(key) == 3 for key in counts)


@pytest.mark.covers("C06-R2")
def test_run_counts_is_reproducible_for_a_fixed_seed(impl):
    """the same arguments give identical counts, also with noise"""
    model = readout_only_model(0.05)
    assert impl.run_counts(GHZ, model, 2000, 5) == impl.run_counts(GHZ, model, 2000, 5)


@pytest.mark.covers("C06-R2")
def test_run_counts_ideal_ghz_produces_only_000_and_111(impl):
    """noise_model=None is an ideal run: only the two GHZ outcomes, each about half of the shots"""
    counts = impl.run_counts(GHZ, None, shots=4000, seed=11)
    assert set(counts) <= {"000", "111"}
    assert within_binomial(counts.get("000", 0), 4000, 0.5)


@pytest.mark.covers("C06-R6")
def test_run_counts_rejects_non_positive_shots(impl):
    """shots = 0 raises ValueError"""
    with pytest.raises(ValueError):
        impl.run_counts(GHZ, None, shots=0, seed=1)


# ------------------------------------------------------------------------------------------------ total_variation_distance
@pytest.mark.covers("C06-R3")
def test_total_variation_distance_known_values(impl):
    """70/30 against 50/50 is 0.2, identical histograms are 0, disjoint ones are 1 (counts are normalised)"""
    tvd = impl.total_variation_distance
    assert tvd({"0": 70, "1": 30}, {"0": 50, "1": 50}) == pytest.approx(0.2, abs=1e-12)
    assert tvd({"0": 7, "1": 3}, {"0": 700, "1": 300}) == pytest.approx(0.0, abs=1e-12)
    assert tvd({"00": 5}, {"11": 9}) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.covers("C06-R6")
def test_total_variation_distance_rejects_an_empty_histogram(impl):
    """an empty dictionary raises ValueError"""
    with pytest.raises(ValueError):
        impl.total_variation_distance({}, {"0": 1})


# ------------------------------------------------------------------------------------------------ noise_report
@pytest.mark.covers("C06-R4")
def test_noise_report_has_the_documented_keys_and_plausible_values(impl):
    """GHZ with a 5 % readout error: tvd_noisy and outside_support around 0.14, the shot-noise floor tvd_ideal below 0.05"""
    report = impl.noise_report(GHZ, readout_only_model(0.05), shots=4000, seed=1234)
    assert {"counts_ideal", "counts_noisy", "tvd_ideal", "tvd_noisy", "outside_support"} <= set(report)
    assert 0 <= report["tvd_ideal"] < 0.05
    assert 0.10 < report["tvd_noisy"] < 0.20
    assert 0.10 < report["outside_support"] < 0.20


@pytest.mark.covers("C06-R5")
def test_noise_report_deviation_grows_with_the_noise_strength(impl):
    """a 10 % readout error deviates more from the exact ideal distribution than a 2 % one (same shots, same seed)"""
    weak = impl.noise_report(GHZ, readout_only_model(0.02), shots=4000, seed=1234)["tvd_noisy"]
    strong = impl.noise_report(GHZ, readout_only_model(0.10), shots=4000, seed=1234)["tvd_noisy"]
    assert strong > weak


# ------------------------------------------------------------------------------------------------ bonus
@pytest.mark.tier("bonus")
@pytest.mark.covers("C06-R7")
def test_bonus_mitigate_readout_inverts_a_known_one_qubit_channel(impl):
    """measured = A p_true with A = [[0.9, 0.2], [0.1, 0.8]] and p_true = (0.7, 0.3) is mapped back to p_true"""
    matrix = np.array([[0.9, 0.2], [0.1, 0.8]])
    mitigated = impl.mitigate_readout({"0": 0.69, "1": 0.31}, matrix)
    assert mitigated["0"] == pytest.approx(0.7, abs=1e-9) and mitigated["1"] == pytest.approx(0.3, abs=1e-9)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C06-R7")
def test_bonus_calibration_matrix_of_a_readout_only_model(impl):
    """for one qubit and a 5 % readout error the columns are (0.95, 0.05) and (0.05, 0.95) up to shot noise"""
    shots = 20000
    matrix = impl.calibration_matrix(1, readout_only_model(0.05), shots=shots, seed=9)
    assert matrix.shape == (2, 2)
    assert np.allclose(matrix.sum(axis=0), 1.0, atol=1e-9)
    assert within_binomial(round(matrix[1, 0] * shots), shots, 0.05)
    assert within_binomial(round(matrix[0, 1] * shots), shots, 0.05)


@pytest.mark.tier("bonus")
@pytest.mark.covers("C06-R8")
def test_bonus_evaluate_mitigation_reports_consistent_numbers_and_helps_against_readout_noise(impl):
    """improvement = tvd_raw - tvd_mitigated, and for a pure 5 % readout error the mitigated TVD is far below the raw one"""
    result = impl.evaluate_mitigation(GHZ, readout_only_model(0.05), shots=4000, seed=1234)
    assert result["improvement"] == pytest.approx(result["tvd_raw"] - result["tvd_mitigated"], abs=1e-12)
    assert result["tvd_raw"] > 0.10
    assert result["tvd_mitigated"] < 0.5 * result["tvd_raw"]
