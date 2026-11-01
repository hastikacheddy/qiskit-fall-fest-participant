# Challenge 9: Protect the Logical Qubit

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_09_error_correction/challenge_09_error_correction.ipynb)

**Tier 3 - Advanced Challenges** · **Estimated time 50-80 min** · folder `challenges/challenge_09_error_correction/`

> A memory qubit sits idle and an occasional bit flip sneaks in. Spread one logical qubit over three physical ones, detect the flip without looking at the data, and undo it.

## Learning objectives
- Encode a logical qubit in the three-qubit bit-flip repetition code.
- Extract an error syndrome without disturbing the encoded information.
- Decode the syndrome and apply the correction with classical feed-forward.
- State precisely what this code can and cannot protect against.

## Prerequisites
- Challenges 1-4 or equivalent
- CNOT and Pauli X
- Mid-circuit measurement and `if_test` (introduced in the notebook)

## Files
- `challenge_09_error_correction.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
A memory qubit sits idle and now and then a **bit flip** (an X error) sneaks in. You will protect **one logical qubit** with the **three-qubit repetition code**: spread it over three physical qubits, **detect** a flip without ever looking at the data, **decode** the evidence and **undo** the error with classical feed-forward.

1. `encode_circuit` - α|0⟩ + β|1⟩ ↦ α|000⟩ + β|111⟩.
2. `syndrome_circuit` - write two parity checks into two ancilla qubits.
3. `decode_syndrome` - from the two syndrome bits to the qubit that was flipped.
4. `correction_circuit` - the gate that undoes the flip.
5. `add_feedforward_correction` - the whole recovery step as a *dynamic circuit*: measure the ancillas, apply X controlled by the classical result.
6. *(Bonus)* `phase_flip_encode_circuit` - the same idea for phase flips.

### Layout and conventions (used by the notebook and by every test)
* **Data qubits** 0, 1, 2 hold the code word; **ancilla qubits** 3 and 4 start in |0⟩. The logical state is placed on qubit 0 *before* encoding; qubits 1 and 2 start in |0⟩.
* **Code words:** |0_L⟩ = |000⟩ and |1_L⟩ = |111⟩, so the encoded state of α|0⟩ + β|1⟩ is α|000⟩ + β|111⟩ (an entangled state - the qubit is *spread out*, not copied).
* **Syndrome** `(s0, s1)`: `s0` is the parity of data qubits 0 and 1 (stored in ancilla qubit 3), `s1` the parity of data qubits 1 and 2 (stored in ancilla qubit 4); the parity is 0 if the two bits agree and 1 if they differ.
* **Feed-forward:** a 2-bit classical register `syn` is passed to `add_feedforward_correction`; `syn[0]` receives the measurement of ancilla 0 (= `s0`), `syn[1]` that of ancilla 1 (= `s1`). The register holds the integer `s0 + 2·s1`, and conditions are written `with qc.if_test((syn, value)):` (a register or a single `Clbit` as the first element of the tuple; expression-based conditions are not supported by the exact simulator).
* All simulations in the tests are **exact** (every measurement outcome is enumerated, no sampling); tolerance 1e-9.

### Function contracts
The helper `validate_layout(qc, data, ancillas, syndrome)` is **provided**: it raises `ValueError` for an invalid layout and returns clean lists.

| Function | Input | Output | Raises `ValueError` when |
|---|---|---|---|
| `encode_circuit()` | - | 3-qubit circuit, unitary (no measurements), mapping (α\|0⟩ + β\|1⟩) ⊗ \|00⟩ to α\|000⟩ + β\|111⟩ for every α, β | - |
| `syndrome_circuit()` | - | 5-qubit circuit (data 0-2, ancillas 3-4), unitary: for ancillas in \|00⟩ it leaves the data unchanged and writes `s0` into qubit 3 and `s1` into qubit 4, for every basis state of the data qubits | - |
| `decode_syndrome(syndrome)` | two 0/1 integers (tuple, list or NumPy array) | `None` (no error) or the index 0, 1, 2 of the data qubit that was flipped | not exactly two integers equal to 0 or 1 |
| `correction_circuit(error_qubit)` | `None` or 0, 1, 2 | 3-qubit circuit that applies X to that qubit (nothing for `None`) | any other value |
| `add_feedforward_correction(qc, data, ancillas, syndrome)` | circuit `qc`, three data qubit indices, two ancilla indices, a 2-bit `ClassicalRegister` that is part of `qc` | modifies `qc` **in place** (return value ignored): syndrome extraction, measurement of the ancillas into `syndrome`, X corrections controlled by the register; touches no other qubit | invalid layout (use `validate_layout`) |
| *(bonus)* `phase_flip_encode_circuit()` | - | 3-qubit circuit mapping (α\|0⟩ + β\|1⟩) ⊗ \|00⟩ to α\|+++⟩ + β\|---⟩ | - |

### What this code can and cannot do (the documented limitations)
1. It corrects **at most one bit flip** per round. Two flips look like one flip of the *third* qubit: the decoder then adds a third flip and the logical qubit is **flipped** (a logical X error).
2. It does **not** protect against **phase flips** (Z errors): they change no parity, the syndrome stays (0, 0) and the logical phase is corrupted. (The bonus code swaps the roles.)
3. The syndrome extraction and the correction themselves are assumed **perfect** - this is a textbook model, not a fault-tolerant scheme.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `encode_circuit` maps alpha|0>+beta|1> (on qubit 0) to alpha|000>+beta|111>.
- `syndrome_circuit` writes the two parity checks into the ancillas without disturbing the logical information.
- `decode_syndrome` identifies each single bit-flip location, and 'no error', from the syndrome.
- `correction_circuit` applies X to the requested qubit (or nothing).
- `add_feedforward_correction` recovers the logical state after any single bit flip, for many logical states.
- Invalid syndromes and qubit indices raise ValueError.

**Bonus (optional, never required to pass):**
- `phase_flip_encode_circuit` yields a code that corrects any single Z error.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c09_public.py --impl challenges/challenge_09_error_correction/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
