# Challenge 4: Teleport the Qubit

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_04_teleportation/challenge_04_teleportation.ipynb)

**Tier 2 - Quantum Algorithms and Applications** · **Estimated time 40-60 min** · folder `challenges/challenge_04_teleportation/`

> Alice must send an unknown qubit state to Bob. She may not look at it, copy it, or fly it over - but she can share an entangled pair in advance and send two ordinary bits by phone.

## Learning objectives
- Implement the three stages of teleportation: entanglement, Bell-basis measurement, correction.
- Explain why two classical bits are necessary and why nothing travels faster than light.
- Use classically controlled gates in Qiskit.
- Verify a protocol on many input states, not on a single lucky one.

## Prerequisites
- Challenges 1-3 or equivalent
- Bell states
- Mid-circuit measurement and classical control (`if_test`) are introduced in the notebook

## Files
- `challenge_04_teleportation.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
**Alice** holds a qubit in an unknown state |ψ⟩. **Bob** is far away. They share an entangled pair prepared in advance, and Alice may send **two ordinary classical bits** (a phone call).
Complete the three stages of the *teleportation protocol* so that Bob's qubit ends up in exactly the state |ψ⟩:

1. **Entanglement** - Alice and Bob share a Bell pair (`create_bell_pair`).
2. **Bell-basis measurement** - Alice entangles her message qubit with her half of the pair, rotates, and measures both qubits (`alice_bell_measurement`). Two classical bits result.
3. **Correction** - Bob applies Pauli gates *controlled by the classical bits* (`bob_correction`).

**Roles in the 3-qubit circuit:** qubit 0 = message, qubit 1 = Alice's half, qubit 2 = Bob. The two classical bits are named `mz` (outcome of measuring the *message* qubit; controls Z) and `mx` (outcome of measuring *Alice's half*; controls X).

### Function contracts
All three functions **modify the given circuit `qc` in place** (their return value is ignored) and must use the qubit indices they are given - never hard-coded numbers.

| Function | What it must do | Invalid input |
|---|---|---|
| `create_bell_pair(qc, a, b)` | gates only: turn qubits `a`, `b` (starting in &#124;00⟩) into &#124;Φ+⟩ = (&#124;00⟩+&#124;11⟩)/√2; all other qubits untouched | equal / negative / out-of-range indices raise `ValueError` or Qiskit's `CircuitError` |
| `alice_bell_measurement(qc, msg, alice, z_bit, x_bit)` | `CX(msg → alice)`, `H(msg)`, then measure `msg` into `z_bit` and `alice` into `x_bit` (`z_bit`, `x_bit` are `Clbit` objects) | equal / out-of-range qubit indices raise `ValueError` or `CircuitError` |
| `bob_correction(qc, bob, z_bit, x_bit)` | classically controlled gates: apply X if `x_bit` is 1, then Z if `z_bit` is 1 (use `qc.if_test`) | out-of-range `bob` raises `ValueError` or `CircuitError` |
| *(bonus)* `average_bob_state_without_correction(prep)` | `DensityMatrix` of Bob's qubit **averaged over Alice's outcomes**, if Bob never hears from Alice | - |

**Tolerances.** The whole protocol is simulated *exactly* (no sampling): Bob's state in every branch must match |ψ⟩ with fidelity ≥ 1 − 1e-9.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `create_bell_pair` leaves the message qubit untouched and puts the two named qubits in |Phi+>.
- `alice_bell_measurement` performs CNOT, H and both measurements; all four outcomes are equally likely and Bob's state in branch (z, x) is X^x Z^z |psi>.
- `bob_correction` restores |psi> for each of the four classical outcomes using classically controlled gates.
- The assembled protocol teleports many different states with fidelity >= 1 - 1e-9 in every branch.
- The functions work for any distinct qubit indices (nothing hard-coded) and reject invalid ones.

**Bonus (optional, never required to pass):**
- Without the classical bits Bob's average state is maximally mixed for every input (no signalling).

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c04_public.py --impl challenges/challenge_04_teleportation/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
