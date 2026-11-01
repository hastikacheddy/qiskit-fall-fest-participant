# Challenge 8: Teach a Quantum Circuit

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_08_quantum_ml/challenge_08_quantum_ml.ipynb)

**Tier 3 - Advanced Challenges** · **Estimated time 60-90 min** · folder `challenges/challenge_08_quantum_ml/`

> Train a two-qubit variational circuit to classify points in the plane, evaluate it honestly on held-out data, and compare it with a classical baseline - without leaking test data into training.

## Learning objectives
- Encode classical features into a quantum circuit and read out a prediction.
- Train circuit parameters with a classical optimiser.
- Avoid train/test leakage and compute evaluation metrics correctly.
- Compare fairly with a classical baseline and discuss what the comparison does (not) show.

## Prerequisites
- Challenges 1-3 and 7 or equivalent
- Parameterised circuits
- Train/test splits and accuracy

## Files
- `challenge_08_quantum_ml.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
A sensor delivers **two measurements** per sample and a label **+1 or −1**. You will teach a **two-qubit variational circuit** to predict the label, **evaluate it honestly** on data it has never seen, and compare it with classical baselines - without letting test information leak into training.

1. `scale_features` - map the raw features to angles in [0, π], with statistics from the **training data only**.
2. `variational_ansatz` - the trainable part of the circuit.
3. `model_output` - the model: feature encoding + ansatz, read out as ⟨Z₀⟩.
4. `mse_loss` - mean squared error against the ±1 labels.
5. `train_vqc` - fit the circuit parameters with a classical optimiser (seeded, reproducible).
6. `binary_metrics` - accuracy, precision, recall, F1 (including the degenerate cases).
7. `run_experiment` - the whole pipeline, leakage-free.
8. *(Bonus)* `parameter_shift_gradient` - the exact gradient of the loss from circuit evaluations.

### Conventions (used by the notebook and by every test)
* **Data:** `X` has shape `(n, 2)`; labels `y` are `-1` or `+1` (labels 0 / 1 are invalid). The positive class is `+1`.
* **Scaling:** feature *j* ↦ `π · (x − min_j) / (max_j − min_j)` with `min_j`, `max_j` taken from the **training** data and applied unchanged to the test data (test values may leave [0, π]; no clipping). A feature that is constant in the training data maps to `π/2`.
* **The model** has two qubits that start in |00⟩ (qubit 0 is the rightmost bit):
  1. *feature encoding:* `RY(x₀)` on qubit 0 and `RY(x₁)` on qubit 1, with the **scaled** features as angles (radians);
  2. *ansatz with L layers:* layer *l* applies `RY(θ[4l])` on qubit 0, `RY(θ[4l+1])` on qubit 1, `RZ(θ[4l+2])` on qubit 0, `RZ(θ[4l+3])` on qubit 1, then `CX` with control qubit 0 and target qubit 1;
  3. *output:* f(x; θ) = ⟨Z₀⟩ ∈ [−1, 1] (exact, no sampling).
  The parameter vector θ has `4·L` entries in exactly this order.
* **Prediction:** `+1` if f ≥ 0, else `−1`. **Loss:** mean of (f(xᵢ) − yᵢ)².
* **Seeded start:** `train_vqc` begins at `rng = np.random.default_rng(seed)`, `θ₀ = rng.uniform(−π, π, 4·L)`.
* **Metrics:** TP, FP, TN, FN count the positive class `+1`; precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2PR/(P+R); a quotient with a zero denominator is `0.0`.

### Function contracts
The helpers `validate_features`, `validate_sample`, `validate_labels`, `validate_params`, `validate_num_layers` are **provided**: they raise `ValueError` for invalid input and return clean NumPy arrays.

| Function | Input | Output | Raises `ValueError` when |
|---|---|---|---|
| `scale_features(X_train, X_test)` | two 2-D arrays with the same number of columns | `(train_scaled, test_scaled)`, new float arrays | shapes / feature counts invalid, non-finite entries, no rows |
| `variational_ansatz(num_layers)` | integer L ≥ 1 | `QuantumCircuit` on 2 qubits with `4L` free parameters (a `ParameterVector`, so that `circuit.parameters` follows the documented order), no measurements | L is not an integer ≥ 1 |
| `model_output(x, params, num_layers)` | one scaled sample (length 2), `4L` parameters | `float` f(x; θ) | wrong length, non-finite values, invalid L |
| `mse_loss(X, y, params, num_layers)` | scaled samples `(n, 2)`, labels ±1, parameters | `float` mean squared error | shapes invalid, labels not ±1, invalid parameters |
| `train_vqc(X_train, y_train, num_layers=2, seed=0, maxiter=100)` | scaled training data, labels ±1 | `dict` with `params` (array of 4L), `initial_loss` (the loss at the seeded start), `final_loss` (= loss at `params`, never larger than `initial_loss`); an optional `history` list is ignored by the tests. Equal arguments → equal result | invalid data, `seed` not a non-negative integer, `maxiter` not a positive integer |
| `binary_metrics(y_true, y_pred)` | two label arrays of equal length | `dict` with `accuracy`, `precision`, `recall`, `f1` (floats) and `tp`, `fp`, `tn`, `fn` (ints) | empty / unequal length, labels not ±1 |
| `run_experiment(X_train, y_train, X_test, y_test, num_layers=2, seed=0, maxiter=100)` | **raw** train and test data | `dict`: `params`, `num_layers`, `feature_min`, `feature_max` (the **training** minima / maxima), `initial_loss`, `train_loss`, `test_loss` (MSE on the scaled data), `train_metrics`, `test_metrics` (as `binary_metrics`) | any invalid input |
| *(bonus)* `parameter_shift_gradient(X, y, params, num_layers)` | as `mse_loss` | NumPy array of the `4L` partial derivatives of the loss, from the parameter-shift rule | as `mse_loss` |

**Correctness versus quality.** The correctness tests never ask for an accuracy: they check scaling, circuit, model output, loss, metrics, reproducibility and the absence of leakage *exactly* (tolerance 1e-9). The **quality benchmark** is reported separately: with the defaults (`num_layers=2, seed=0, maxiter=100`) on the supplied dataset the held-out accuracy should be clearly above chance (≥ 70 %), and the training loss should fall by at least 30 %.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `scale_features` fits min-max scaling to [0, pi] on the training data only (no train/test leakage).
- `variational_ansatz` returns a parameterised circuit with the documented dimensions.
- `model_output` is the exact <Z_0> of feature map plus ansatz: finite and within [-1, 1].
- `mse_loss` equals the mean squared error between model outputs and +-1 labels.
- `train_vqc` uses the documented seeded initialisation, is reproducible and never ends worse than it started.
- `binary_metrics` computes accuracy, precision, recall and F1 correctly, including degenerate cases.
- `run_experiment` is leakage-free: training never sees test data; reported test metrics are recomputed from the returned model.
- Invalid shapes, non-finite values, labels other than -1/+1, wrong parameter counts and invalid layer numbers raise ValueError; no function modifies its inputs.

**Quality benchmarks** (reported separately from correctness - a stochastic optimiser is not required to be perfect):
- Held-out accuracy is clearly above chance on the supplied dataset and the training loss falls (benchmark, not correctness).

**Bonus (optional, never required to pass):**
- `parameter_shift_gradient` matches finite differences.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c08_public.py --impl challenges/challenge_08_quantum_ml/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
