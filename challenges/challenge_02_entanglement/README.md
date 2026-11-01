# Challenge 2: The Entanglement Detective

**Tier 1 - Foundations** · **Estimated time 20-30 min** · folder `challenges/challenge_02_entanglement/`

> Two qubits always give matching answers. Is that entanglement - or just two coins that were set to the same face? Collect the evidence like a detective.

## Learning objectives
- Construct a Bell state and read its joint measurement outcomes.
- Show that correlation in a single basis is not proof of entanglement.
- Measure correlations in several bases (Z, X, Y).
- Decide entanglement of a pure two-qubit state from the purity of one qubit.

## Prerequisites
- Challenge 1 or equivalent: gates, exact simulation, probabilities
- The H and CNOT gates

## Files
- `challenge_02_entanglement.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
Two qubits always give matching answers when measured. Is that **entanglement** - or two coins that were simply set to the same face?
Collect the evidence like a detective:

1. **Build** the Bell state $|\Phi^+\rangle = (|00\rangle+|11\rangle)/\sqrt2$.
2. **Analyse the joint outcomes** exactly: the probability of every bit-string.
3. **Measure correlations in more than one basis** (Z, X, Y).
4. **Decide** whether a pure two-qubit state is entangled - and do not be fooled by suspects that look entangled in one basis.
5. *(Bonus)* Compute the CHSH quantity.

### Function contracts
States are Qiskit `Statevector` objects. **Qubit 0 is the least significant bit** (the rightmost character of a bit-string).

| Function | Input | Output | Must raise `ValueError` when |
|---|---|---|---|
| `bell_circuit()` | none | 2-qubit `QuantumCircuit`, gates only (no measurement), preparing &#124;Φ+⟩ from &#124;00⟩ up to a global phase | - |
| `joint_probabilities(state)` | a `Statevector` of qubits | `dict` mapping **every** bit-string of length n (including impossible ones) to its exact probability (plain Python `str` keys and `float` values) | the argument is not a `Statevector` of qubits |
| `correlation_in_basis(state, basis)` | 2-qubit `Statevector`; `basis` is `"Z"`, `"X"` or `"Y"` | float E = P(equal outcomes) − P(different outcomes) when **both** qubits are measured in that basis (outcome bit 0 = eigenvalue +1) | not a 2-qubit state, or `basis` not in `{"Z","X","Y"}` |
| `is_entangled(state, tol=1e-9)` | pure 2-qubit `Statevector` | `bool`: True iff 1 − purity of qubit 0's reduced state exceeds `tol` | not a 2-qubit state |
| *(bonus)* `chsh_value(state)` | 2-qubit `Statevector` | S = ⟨A0B0⟩+⟨A0B1⟩+⟨A1B0⟩−⟨A1B1⟩ with Alice = qubit 0, Bob = qubit 1, A0 = Z, A1 = X, B0 = (Z+X)/√2, B1 = (Z−X)/√2 | not a 2-qubit state |

**Tolerances.** Exact comparisons use 1e-9. `tol=1e-9` in `is_entangled` also protects against floating-point noise: a *product* state has purity 1 only up to ~1e-16.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `bell_circuit()` prepares |Phi+> = (|00>+|11>)/sqrt(2) (up to global phase) with unitary gates only.
- Independent superposition (H on both qubits) is not accepted: in the Bell state each qubit alone is maximally mixed.
- `joint_probabilities` returns the exact probability of all 2^n outcomes in Qiskit bit order.
- `correlation_in_basis` equals <sigma x sigma> for sigma in {Z, X, Y} on arbitrary two-qubit states.
- `is_entangled` separates entangled from product states, including perfectly Z-correlated product states.
- Inputs that are not two-qubit states, and unknown bases, raise ValueError; the tolerance is respected.

**Bonus (optional, never required to pass):**
- `chsh_value` reproduces the CHSH quantity (2*sqrt(2) for the Bell state, at most 2 for product states).

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c02_public.py --impl challenges/challenge_02_entanglement/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
