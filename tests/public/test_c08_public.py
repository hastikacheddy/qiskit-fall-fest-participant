"""Public checks for Challenge 8 - Teach a Quantum Circuit (smoke checks on tiny hand-made data; no accuracy is demanded).

Expected values are worked out by hand from the conventions in the problem statement. Training checks use six points and a few
iterations so that they run in a second.
"""
import numpy as np
import pytest

pytestmark = [pytest.mark.challenge(8), pytest.mark.tier("smoke")]

X_SMALL = np.array([[0.2, 0.4], [1.0, 2.0], [2.2, 0.8], [3.0, 2.6], [0.7, 1.5], [2.6, 2.9]])  # already angles in [0, pi]
Y_SMALL = np.array([1, 1, -1, -1, 1, -1])
RAW_TRAIN = np.array([[10.0, -4.0], [12.0, -3.0], [14.0, -2.0], [16.0, -1.0], [11.0, -3.5], [15.0, -1.5]])
RAW_TEST = np.array([[12.5, -2.5], [13.5, -1.0], [9.0, -4.5]])
RAW_LABELS = np.array([1, 1, -1, -1, 1, -1])
TEST_LABELS = np.array([1, -1, 1])


# ------------------------------------------------------------------------------------------------ scale_features
@pytest.mark.covers("C08-R1")
def test_scale_features_maps_the_training_range_to_zero_pi_and_applies_it_to_the_test_data(impl):
    """training [0, 5, 10] -> [0, pi/2, pi]; a test value of 40 in a feature trained on 10..30 lands at 1.5 pi (not clipped)"""
    train = np.array([[0.0, 10.0], [5.0, 20.0], [10.0, 30.0]])
    test = np.array([[2.5, 40.0]])
    scaled_train, scaled_test = impl.scale_features(train, test)
    assert np.allclose(scaled_train, [[0, 0], [np.pi / 2, np.pi / 2], [np.pi, np.pi]], atol=1e-12)
    assert np.allclose(scaled_test, [[np.pi / 4, 1.5 * np.pi]], atol=1e-12)


@pytest.mark.covers("C08-R1")
def test_scale_features_statistics_come_from_the_training_data_only(impl):
    """leakage tripwire: changing the test set must not change the scaled training data"""
    a, _ = impl.scale_features(RAW_TRAIN, RAW_TEST)
    b, _ = impl.scale_features(RAW_TRAIN, np.array([[100.0, 50.0], [-30.0, -80.0]]))
    assert np.allclose(a, b, atol=1e-12)


@pytest.mark.covers("C08-R10")
def test_scale_features_rejects_a_one_dimensional_array(impl):
    """features must be a 2-D array"""
    with pytest.raises(ValueError):
        impl.scale_features(np.array([1.0, 2.0, 3.0]), np.array([[1.0]]))


# ------------------------------------------------------------------------------------------------ variational_ansatz
@pytest.mark.covers("C08-R2")
@pytest.mark.parametrize("layers", [1, 2, 3])
def test_variational_ansatz_has_four_parameters_per_layer_on_two_qubits(impl, layers):
    """two qubits, 4 * layers free parameters, no measurements"""
    qc = impl.variational_ansatz(layers)
    assert qc.num_qubits == 2 and qc.num_parameters == 4 * layers and qc.num_clbits == 0


@pytest.mark.covers("C08-R10")
def test_variational_ansatz_rejects_zero_layers(impl):
    """num_layers = 0 raises ValueError"""
    with pytest.raises(ValueError):
        impl.variational_ansatz(0)


# ------------------------------------------------------------------------------------------------ model_output
@pytest.mark.covers("C08-R3")
def test_model_output_with_zero_parameters_is_the_cosine_of_the_first_feature(impl):
    """one layer with all angles 0 is just a CNOT: <Z_0> = cos(x_0) (and not cos(x_1))"""
    assert impl.model_output([0.7, 2.1], np.zeros(4), 1) == pytest.approx(np.cos(0.7), abs=1e-9)


@pytest.mark.covers("C08-R3")
def test_model_output_is_always_between_minus_one_and_one(impl):
    """an expectation value of Z: a float in [-1, 1] for any parameters"""
    rng = np.random.default_rng(3)
    for _ in range(5):
        out = impl.model_output(rng.uniform(0, np.pi, 2), rng.uniform(-np.pi, np.pi, 8), 2)
        assert isinstance(out, (float, np.floating)) and -1 - 1e-9 <= out <= 1 + 1e-9


@pytest.mark.covers("C08-R10")
def test_model_output_rejects_a_wrong_number_of_parameters(impl):
    """two layers need eight parameters"""
    with pytest.raises(ValueError):
        impl.model_output([0.5, 0.5], np.zeros(4), 2)


# ------------------------------------------------------------------------------------------------ mse_loss
@pytest.mark.covers("C08-R4")
def test_mse_loss_is_zero_for_a_perfect_model_and_four_for_the_opposite_labels(impl):
    """zero parameters, one layer: outputs cos(0) = 1 and cos(pi) = -1 for the first features 0 and pi"""
    X = np.array([[0.0, 0.5], [np.pi, 1.0]])
    assert impl.mse_loss(X, [1, -1], np.zeros(4), 1) == pytest.approx(0.0, abs=1e-9)
    assert impl.mse_loss(X, [-1, 1], np.zeros(4), 1) == pytest.approx(4.0, abs=1e-9)


@pytest.mark.covers("C08-R10")
def test_mse_loss_rejects_labels_that_are_not_plus_or_minus_one(impl):
    """labels 0 / 1 are invalid"""
    with pytest.raises(ValueError):
        impl.mse_loss(X_SMALL, [1, 0, 1, 0, 1, 0], np.zeros(4), 1)


# ------------------------------------------------------------------------------------------------ train_vqc
@pytest.mark.covers("C08-R5")
def test_train_vqc_returns_parameters_and_never_increases_the_loss(impl):
    """documented keys, 4 * layers parameters, final loss at most the initial loss and equal to the loss of the returned parameters"""
    result = impl.train_vqc(X_SMALL, Y_SMALL, num_layers=1, seed=0, maxiter=12)
    assert {"params", "initial_loss", "final_loss"} <= set(result)
    assert np.asarray(result["params"]).shape == (4,)
    assert result["final_loss"] <= result["initial_loss"] + 1e-12
    assert result["final_loss"] == pytest.approx(impl.mse_loss(X_SMALL, Y_SMALL, result["params"], 1), abs=1e-9)


@pytest.mark.covers("C08-R5")
def test_train_vqc_is_reproducible_for_a_fixed_seed(impl):
    """the same arguments give the same parameters"""
    a = impl.train_vqc(X_SMALL, Y_SMALL, num_layers=1, seed=4, maxiter=10)
    b = impl.train_vqc(X_SMALL, Y_SMALL, num_layers=1, seed=4, maxiter=10)
    assert np.allclose(a["params"], b["params"], atol=1e-12) and a["final_loss"] == pytest.approx(b["final_loss"], abs=1e-12)


# ------------------------------------------------------------------------------------------------ binary_metrics
@pytest.mark.covers("C08-R6")
def test_binary_metrics_on_a_hand_checked_example(impl):
    """true [1,1,1,1,-1,-1] against predicted [1,1,-1,-1,1,-1]: tp 2, fp 1, tn 1, fn 2 -> accuracy 3/6, precision 2/3, recall 1/2, F1 4/7"""
    m = impl.binary_metrics([1, 1, 1, 1, -1, -1], [1, 1, -1, -1, 1, -1])
    assert (m["tp"], m["fp"], m["tn"], m["fn"]) == (2, 1, 1, 2)
    assert m["accuracy"] == pytest.approx(3 / 6) and m["precision"] == pytest.approx(2 / 3)
    assert m["recall"] == pytest.approx(1 / 2) and m["f1"] == pytest.approx(4 / 7)


@pytest.mark.covers("C08-R6")
def test_binary_metrics_handles_a_model_that_never_predicts_the_positive_class(impl):
    """no predicted positives: precision, recall and F1 are 0.0 (no division by zero), accuracy is still defined"""
    m = impl.binary_metrics([1, -1, -1], [-1, -1, -1])
    assert m["precision"] == 0.0 and m["recall"] == 0.0 and m["f1"] == 0.0
    assert m["accuracy"] == pytest.approx(2 / 3)


@pytest.mark.covers("C08-R10")
def test_binary_metrics_rejects_labels_zero_and_one(impl):
    """the convention is -1 / +1: 0 / 1 labels raise ValueError"""
    with pytest.raises(ValueError):
        impl.binary_metrics([0, 1, 1], [0, 1, 0])


# ------------------------------------------------------------------------------------------------ run_experiment
@pytest.mark.covers("C08-R7")
def test_run_experiment_reports_the_documented_keys_and_the_training_statistics(impl):
    """keys present; feature_min / feature_max are the minima / maxima of the RAW TRAINING data"""
    r = impl.run_experiment(RAW_TRAIN, RAW_LABELS, RAW_TEST, TEST_LABELS, num_layers=1, seed=0, maxiter=8)
    for key in ("params", "num_layers", "feature_min", "feature_max", "initial_loss", "train_loss", "test_loss", "train_metrics", "test_metrics"):
        assert key in r, f"missing key {key!r}"
    assert np.allclose(r["feature_min"], RAW_TRAIN.min(axis=0)) and np.allclose(r["feature_max"], RAW_TRAIN.max(axis=0))
    assert {"accuracy", "precision", "recall", "f1"} <= set(r["test_metrics"])


@pytest.mark.covers("C08-R7")
def test_run_experiment_training_does_not_depend_on_the_test_set(impl):
    """leakage tripwire: with a completely different test set the parameters and the training results stay exactly the same"""
    a = impl.run_experiment(RAW_TRAIN, RAW_LABELS, RAW_TEST, TEST_LABELS, num_layers=1, seed=1, maxiter=8)
    b = impl.run_experiment(RAW_TRAIN, RAW_LABELS, np.array([[500.0, 90.0], [-70.0, -20.0]]), np.array([-1, 1]), num_layers=1, seed=1, maxiter=8)
    assert np.allclose(a["params"], b["params"], atol=1e-12)
    assert a["train_loss"] == pytest.approx(b["train_loss"], abs=1e-12)
    assert a["train_metrics"]["accuracy"] == pytest.approx(b["train_metrics"]["accuracy"])


# ------------------------------------------------------------------------------------------------ bonus
@pytest.mark.tier("bonus")
@pytest.mark.covers("C08-R9")
def test_bonus_parameter_shift_gradient_matches_finite_differences(impl):
    """the exact parameter-shift gradient of the loss agrees with central finite differences (step 1e-6)"""
    params = np.random.default_rng(5).uniform(-np.pi, np.pi, 4)
    gradient = np.asarray(impl.parameter_shift_gradient(X_SMALL, Y_SMALL, params, 1))
    eps = 1e-6
    finite = np.array([(impl.mse_loss(X_SMALL, Y_SMALL, params + eps * e, 1) - impl.mse_loss(X_SMALL, Y_SMALL, params - eps * e, 1)) / (2 * eps)
                       for e in np.eye(4)])
    assert gradient.shape == (4,) and np.allclose(gradient, finite, atol=1e-6)
