# Challenge 1: Superposition Under the Microscope

**Tier 1 - Foundations** · **Estimated time 15-25 min** · folder `challenges/challenge_01_superposition/`

> A lab technician needs a one-qubit source that, when measured, gives 0 or 1 with equal probability - and wants to understand exactly what the *amplitudes* behind those probabilities are.

## Learning objectives
- Build a one-qubit circuit with Qiskit and simulate it exactly.
- Explain the difference between amplitudes (complex) and measurement probabilities (real, Born rule).
- Distinguish exact probabilities from finite-shot frequencies.
- Know that different phases can hide behind identical probabilities.

## Prerequisites
- Basic Python (functions, lists, NumPy arrays)
- What a qubit is: the states |0> and |1>
- No prior Qiskit experience required

## Files
- `challenge_01_superposition.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
You will build and analyse the simplest interesting quantum object: **one qubit in an equal superposition**.

1. **Build** a one-qubit circuit that gives `0` and `1` with probability ½ each when measured. Every correct construction is accepted.
2. **Convert amplitudes to probabilities** with the Born rule.
3. **Compute exact probabilities** of any circuit by simulating its state vector - *not* by sampling.
4. *(Bonus)* Hit a **non-uniform** target such as P(0) = 0.2, and show that identical probabilities can hide different states.

### Function contracts
| Function | Input | Output | Must raise `ValueError` when |
|---|---|---|---|
| `superposition_circuit()` | none | `QuantumCircuit` on 1 qubit, no measurements, no classical bits | - |
| `born_probabilities(amplitudes)` | 1-D sequence or array of complex amplitudes, length 2^n (n ≥ 1) | `numpy.ndarray` of floats, same length, entries ≥ 0, sum 1 | the vector is not normalised (‖a‖ differs from 1 by more than 1e-9), the length is not a power of two ≥ 2, the input is not 1-D, or contains NaN/inf. **Must not modify its input.** |
| `exact_probabilities(circuit)` | measurement-free `QuantumCircuit` on n qubits | `numpy.ndarray`, length 2^n; entry *i* is the probability of the bit-string whose integer value is *i* (qubit 0 is the **least** significant bit) | the circuit contains measurements |
| *(bonus)* `circuit_for_probability(p0)` | `p0` in [0, 1] | 1-qubit circuit with P(0) = p0 | `p0` is outside [0, 1] or not finite |
| *(bonus)* `circuit_for_phase_state(p0, phi)` | `p0` in [0, 1], real `phi` | 1-qubit circuit preparing √p0 &#124;0⟩ + e^{iφ} √(1-p0) &#124;1⟩ (up to global phase) | `p0` outside [0, 1] or an argument is not finite |

**Tolerances.** Exact quantities are compared with absolute tolerance **1e-9**. Finite-shot frequencies are never used as the only evidence of correctness.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `superposition_circuit()` returns a valid one-qubit circuit (no measurement or classical control).
- The circuit's exact outcome probabilities are (1/2, 1/2); every equivalent construction is accepted.
- `born_probabilities` applies the Born rule |amplitude|^2 to valid amplitude vectors of any length 2^n.
- `born_probabilities` rejects invalid input (not normalised, bad length or shape, non-finite) and never modifies its argument.
- `exact_probabilities` returns the exact outcome distribution of an n-qubit circuit in Qiskit bit order.
- `exact_probabilities` rejects circuits that contain measurements.

**Bonus (optional, never required to pass):**
- `circuit_for_probability(p0)` prepares any distribution with P(0) = p0 (non-uniform targets).
- `circuit_for_phase_state(p0, phi)` prepares the requested relative phase (same Z probabilities, different X/Y expectations).

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c01_public.py --impl challenges/challenge_01_superposition/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
