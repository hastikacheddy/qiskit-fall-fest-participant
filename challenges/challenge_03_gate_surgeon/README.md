# Challenge 3: Gate Surgeon

**Tier 1 - Foundations** · **Estimated time 20-30 min** · folder `challenges/challenge_03_gate_surgeon/`

> Three circuits arrive at the clinic with symptoms: wrong states, wrong unitaries, wrong angles. Diagnose the bugs and operate - without changing what each circuit is supposed to do.

## Learning objectives
- Read a circuit and predict the state it prepares.
- Debug common mistakes: wrong qubit, reversed CNOT, stray gate, wrong rotation angle.
- Verify a repair by comparing states and unitaries, not by eye.
- Recognise that many different circuits can be correct.

## Prerequisites
- Challenges 1-2 or equivalent
- Qubit ordering in Qiskit (qubit 0 is the rightmost bit)

## Files
- `challenge_03_gate_surgeon.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
Three circuits (and one bonus patient) arrive at the clinic. Each *runs*, but does the wrong thing. Your job is to **repair them without
changing what they are supposed to do**, and to prove the repair with state vectors and unitaries - not by staring at the drawing.

| Patient | Must become | Constraint |
|---|---|---|
| 1 · `patient_ghz()` | the 3-qubit GHZ state (&#124;000⟩ + &#124;111⟩)/√2 | 3 qubits, gates only |
| 2 · `patient_swap()` | the SWAP unitary on 2 qubits | **only CX gates, at most 3** |
| 3 · `patient_tilted_pair(theta)` | cos(θ/2)&#124;00⟩ + sin(θ/2)&#124;11⟩ **for every θ** | 2 qubits, gates only; non-finite θ raises `ValueError` |
| 4 · `patient_readout()` *(bonus)* | a 3-qubit circuit with 3 classical bits whose measurement gives **`110` with certainty** | qubit *i* is measured into classical bit *i* |

### Function contracts
* "Prepares a state" means: starting from &#124;0…0⟩ the circuit's state vector equals the target **up to a global phase**. Many different circuits are correct.
* Circuits returned for patients 1-3 contain **no measurements and no classical bits**.
* Qiskit's bit order: qubit 0 is the **rightmost** character of a bit-string.
* `patient_tilted_pair` must work for *any* finite real θ (negative, larger than 2π, integers, NumPy floats). `float('nan')` and `inf` must raise `ValueError`.

**Tolerances.** States and unitaries are compared exactly (up to global phase) with absolute tolerance 1e-9.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `patient_ghz()` returns a three-qubit circuit preparing (|000>+|111>)/sqrt(2) (up to global phase).
- `patient_swap()` uses only CX gates (at most three) and implements SWAP (up to global phase).
- `patient_tilted_pair(theta)` prepares cos(theta/2)|00> + sin(theta/2)|11> for every theta.
- Non-finite theta is rejected with ValueError; the returned circuits are measurement-free and have the documented width.

**Bonus (optional, never required to pass):**
- `patient_readout()` yields the deterministic bit-string '110' with qubit i measured into clbit i.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c03_public.py --impl challenges/challenge_03_gate_surgeon/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
