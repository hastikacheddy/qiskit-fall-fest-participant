# Challenge 5: Find the Hidden State

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_05_grover/challenge_05_grover.ipynb)

**Tier 2 - Quantum Algorithms and Applications** · **Estimated time 40-60 min** · folder `challenges/challenge_05_grover/`

> A vault accepts exactly one n-bit code. Checking codes one by one takes ~2^n tries; Grover's algorithm needs only ~sqrt(2^n) oracle calls. Build the search and watch the amplitude of the hidden code grow.

## Learning objectives
- Implement a phase oracle that marks one basis state.
- Implement the diffuser (inversion about the mean).
- Explain phase marking and amplitude amplification geometrically.
- Choose the number of iterations and observe what happens when you overshoot.

## Prerequisites
- Challenges 1-3 or equivalent
- Multi-controlled gates
- Superposition and phase

## Files
- `challenge_05_grover.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
A vault accepts exactly one n-bit code (the **marked** bit-string). Trying codes one by one needs about N/2 tries on average, N = 2ⁿ.
**Grover's algorithm** finds it with about √N oracle calls. You will build it for a handful of qubits and watch the amplitude of the hidden code grow:

1. `phase_oracle(marked)` - **phase marking**: flip the sign of the amplitude of the marked state, leave all others alone.
2. `diffuser(n)` - **amplitude amplification**: reflect all amplitudes about their mean, so the sign flip becomes a *growth* of the marked amplitude.
3. `optimal_iterations(n, num_marked)` - how many (oracle, diffuser) rounds to run.
4. `grover_circuit(marked, iterations)` - the complete search circuit.
5. *(Bonus)* `phase_oracle_multi(marked_states)` - several marked states at once.

### Function contracts
**Bit order:** `marked` is a string of `'0'`/`'1'` in **Qiskit order** - the *rightmost* character is qubit 0 - so the marked basis state has index `int(marked, 2)`. The number of qubits is `n = len(marked)`.

| Function | Input | Output | Must raise `ValueError` when |
|---|---|---|---|
| `phase_oracle(marked)` | string of 0/1, length n ≥ 1 | n-qubit circuit (**no ancillas, no measurements**) whose unitary is diagonal with −1 on the marked state and +1 elsewhere (up to a global phase) | `marked` is not a non-empty string of `'0'`/`'1'` |
| `diffuser(n)` | `int` n ≥ 1 | n-qubit circuit implementing 2&#124;s⟩⟨s&#124; − I (up to a global phase), &#124;s⟩ = uniform superposition | n is not an integer ≥ 1 |
| `optimal_iterations(n, num_marked=1)` | `int` n ≥ 1, `int` 1 ≤ num_marked < 2ⁿ | non-negative `int` k that maximises the ideal success probability among k = 0 … ⌈π/(4θ)⌉, where θ = arcsin√(M/N) | invalid n or num_marked (not an integer, < 1, or ≥ 2ⁿ) |
| `grover_circuit(marked, iterations=None)` | as above; `iterations=None` means `optimal_iterations(n, 1)` | n-qubit circuit (**no measurements**): H on all qubits, then `iterations` times (oracle, diffuser) | invalid `marked`; `iterations` not a non-negative integer |
| *(bonus)* `phase_oracle_multi(marked_states)` | non-empty sequence of distinct bit-strings of equal length | n-qubit circuit flipping the sign of every listed state | empty list, duplicates, mixed lengths, invalid strings |

**Tolerances.** Operators and states are compared exactly (up to a global phase) with absolute tolerance 1e-9. "Success probability" always means the *exact* probability of the marked outcome.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `phase_oracle(marked)` flips the sign of exactly the marked basis state (up to global phase), in Qiskit bit order.
- `diffuser(n)` implements the inversion about the uniform superposition, 2|s><s| - I (up to global phase).
- `optimal_iterations(n, num_marked)` returns an iteration count that maximises the ideal success probability.
- `grover_circuit` reaches the theoretical success probability sin^2((2k+1)theta) for every marked state and iteration count.
- Invalid marked strings, sizes and iteration counts raise ValueError; returned circuits have the documented width, no measurements, and are independent objects.

**Bonus (optional, never required to pass):**
- `phase_oracle_multi` handles several marked states and Grover with M solutions matches theory.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c05_public.py --impl challenges/challenge_05_grover/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
