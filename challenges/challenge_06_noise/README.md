# Challenge 6: Fight the Noise

**Tier 2 - Quantum Algorithms and Applications** · **Estimated time 40-60 min** · folder `challenges/challenge_06_noise/`

> Your ideal circuit works perfectly - on paper. Real devices are noisy. Quantify exactly how much damage a documented noise model does, and test whether a mitigation trick really helps.

## Learning objectives
- Build a noise model with gate (depolarising) and readout errors.
- Run ideal and noisy experiments under identical, reproducible settings.
- Quantify the deviation with the total variation distance.
- Evaluate - not assume - a simple mitigation technique.

## Prerequisites
- Challenges 1-2 or equivalent
- Measurement counts
- Qiskit Aer (installed as an optional extra)

## Files
- `challenge_06_noise.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
Your circuit works perfectly - on paper. A real quantum computer makes small errors with every gate and every measurement. In this challenge you **quantify exactly how much damage a documented noise model does** to a baseline circuit - reproducibly - and, as a bonus, you **test instead of assume** whether a mitigation trick helps.

1. `build_noise_model(p1, p2, p_readout)` - build the documented noise model with Qiskit Aer.
2. `run_counts(circuit, noise_model, shots, seed)` - run a circuit ideal (no noise model) or noisy, under *identical and reproducible* settings.
3. `total_variation_distance(counts_a, counts_b)` - a distance between two outcome histograms.
4. `noise_report(circuit, noise_model, shots, seed)` - quantify the noise: deviation from the exact ideal distribution and probability mass in outcomes that can only occur because of noise.
5. *(Bonus)* `calibration_matrix`, `mitigate_readout`, `evaluate_mitigation` - readout-error mitigation, judged by measured numbers.

### The documented noise model
| Where | Error |
|---|---|
| after every `sx` and every `x` gate, on any qubit | depolarising error with parameter **p1** |
| after every `cx` gate, on any ordered pair of qubits | two-qubit depolarising error with parameter **p2** |
| when a qubit is measured | symmetric readout error: P(read 1 &#124; qubit is 0) = P(read 0 &#124; qubit is 1) = **p_readout**, independently for every qubit |
| everything else, e.g. `rz` (a *virtual* gate on IBM hardware) | noiseless |

A *depolarising error with parameter p on k qubits* is the channel ρ → (1 − p)·ρ + p·(I/2ᵏ ⊗ Tr_S ρ) (S = the k qubits it acts on). It is exactly what `qiskit_aer.noise.depolarizing_error(p, k)` implements. All three parameters are real numbers in [0, 1]. The values `DOCUMENTED_NOISE = {p1: 0.002, p2: 0.015, p_readout: 0.02}` have the order of magnitude of today's superconducting devices; they are **not** a model of any specific chip.

### Run configuration (identical for ideal and noisy runs)
`run_counts` always transpiles with `generate_preset_pass_manager(optimization_level=0, basis_gates=BASIS_GATES, seed_transpiler=seed)`, where `BASIS_GATES = ['id', 'rz', 'sx', 'x', 'cx']`, and runs the result on `AerSimulator(noise_model=noise_model, seed_simulator=seed)` with the requested number of shots (`noise_model=None` means ideal). A noise model is attached to gate *names*, so the circuit must be rewritten into the gates the model talks about - in **both** runs, otherwise the comparison is not fair.

### Function contracts
| Function | Input | Output | Raises `ValueError` when |
|---|---|---|---|
| `build_noise_model(p1, p2, p_readout)` | three real numbers in [0, 1] | `qiskit_aer.noise.NoiseModel` exactly as documented above | a parameter is not a real number in [0, 1] (NaN included) |
| `run_counts(circuit, noise_model=None, shots=4000, seed=1234)` | circuit whose measurements are at the end (one classical register), a `NoiseModel` or `None`, a positive `int`, an `int` | `dict` bit-string → count (Qiskit bit order, counts add up to `shots`). Equal arguments give identical output. The `circuit` you pass in is **not modified** | `shots` is not a positive integer, or the circuit contains no measurement |
| `total_variation_distance(counts_a, counts_b)` | two dicts bit-string → non-negative number (counts *or* probabilities) | float in [0, 1]: ½·Σ&#124;p(x) − q(x)&#124; after dividing each dict by its own total; a missing key counts as 0 | a dict is empty, has a negative or non-finite value, or sums to 0 |
| `noise_report(circuit, noise_model, shots=4000, seed=1234)` | as for `run_counts` | `dict` with the keys listed below | as for `run_counts` |
| *(bonus)* `calibration_matrix(n, noise_model, shots=4000, seed=1234)` | integer 1 ≤ n ≤ 6 | NumPy array, shape (2ⁿ, 2ⁿ): column *j* = measured probabilities after preparing basis state *j* (X on qubit *q* iff bit *q* of *j* is 1) and measuring all qubits via `run_counts`; entry [i, j] = P(read i &#124; prepared j) with i, j = `int(bit-string, 2)` | *n* is not an integer in [1, 6] |
| *(bonus)* `mitigate_readout(counts, matrix)` | counts or probabilities of n-bit strings; a (2ⁿ, 2ⁿ) matrix | `dict` over **all** 2ⁿ bit-strings: solve `matrix · q = p_measured`, set negative entries to 0, divide by the sum | shapes do not match, matrix singular (condition number > 10¹²), counts empty or invalid |
| *(bonus)* `evaluate_mitigation(circuit, noise_model, shots=4000, seed=1234)` | as for `run_counts` | `dict` with `tvd_raw`, `tvd_mitigated` and `improvement = tvd_raw − tvd_mitigated`, all measured against the exact ideal distribution | as for `run_counts` |

**The keys of `noise_report`:** `counts_ideal` = `run_counts(circuit, None, shots, seed)`; `counts_noisy` = `run_counts(circuit, noise_model, shots, seed)`; `tvd_noisy` = TVD between `counts_noisy` and the **exact** ideal distribution (`ideal_distribution(circuit)`, provided); `tvd_ideal` = the same for `counts_ideal` - the **shot-noise floor**: even a perfect machine does not reproduce a distribution exactly with finitely many shots; `outside_support` = fraction of the noisy shots whose bit-string has ideal probability 0.

**Randomness and tolerances.** Counts are random, so the tests never demand one exact histogram. They check (i) deterministic quantities *exactly* (the distance between two given dictionaries, the exact channel of one gate, equal seeds giving equal counts) and (ii) sampled counts against the exact expected distribution with **exact binomial intervals** (a correct implementation violates one with probability below 10⁻⁷ per outcome).

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `build_noise_model` attaches depolarising errors with the documented parameters to sx, x and cx and a symmetric readout error to every qubit.
- `run_counts` configures ideal and noisy runs consistently (same transpilation, shots and seed) and is reproducible.
- `total_variation_distance` is a correct distance between count dictionaries.
- `noise_report` quantifies noise: TVD against the exact ideal distribution and probability mass outside the ideal support.
- Stronger noise gives a larger measured deviation (controlled seed, statistical tolerance).
- Invalid probabilities, shots and empty inputs raise ValueError; `run_counts` does not modify the circuit it is given.

**Bonus (optional, never required to pass):**
- `calibration_matrix` / `mitigate_readout` invert a known readout channel exactly and return valid distributions.
- `evaluate_mitigation` reports measured numbers: mitigation helps for readout-only noise and is not claimed to fix gate noise.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c06_public.py --impl challenges/challenge_06_noise/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
