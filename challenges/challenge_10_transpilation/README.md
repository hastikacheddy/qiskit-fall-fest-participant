# Challenge 10: The Hardware Architect

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_10_transpilation/challenge_10_transpilation.ipynb)

**Tier 3 - Advanced Challenges** · **Estimated time 45-75 min** · folder `challenges/challenge_10_transpilation/`

> Your algorithm assumes every qubit can talk to every other. The chip's qubits sit on a line. Re-engineer the circuit for this hardware - cheaper, shallower, and still doing exactly the same thing.

## Learning objectives
- Measure circuit cost with depth and two-qubit gate count.
- Check that a circuit respects a coupling map and a basis-gate set.
- Use the transpiler (layout, routing, optimisation level, seeds) to reduce cost.
- Verify that an optimised circuit still implements the same unitary.

## Prerequisites
- Challenges 1-5 or equivalent
- Circuit depth and gate counts
- The idea of a coupling map (which qubits are connected)

## Files
- `challenge_10_transpilation.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
Your algorithm assumes that **every qubit can talk to every other qubit**. The chip it must run on is a **line**: only neighbouring qubits can run a two-qubit gate, and it only knows a handful of native gates. Moving quantum information around costs extra gates (SWAPs), and every two-qubit gate is the noisiest operation on the device. Re-engineer the circuit for this hardware - **cheaper, shallower, and still doing exactly the same thing**.

1. `circuit_cost` - measure a circuit: depth, two-qubit gates, total gates.
2. `is_hardware_valid` - does a circuit respect the basis gates and the coupling map?
3. `optimize_for_hardware` - transpile for the device and keep the best of several seeded attempts.
4. `cost_reduction` - how much cheaper than the baseline is your result?
5. *(Bonus)* `ghz_chain_rewrite` - beat the transpiler by hand on the GHZ circuit.

### The device model (used by the notebook and by every test)
* Qubits `0 … n−1`; the **coupling map** is a list of pairs `(a, b)` that can run a two-qubit gate. Couplings are **bidirectional**. The number of device qubits is `max(node) + 1`, and the circuits of this challenge have **exactly that many qubits** (otherwise `ValueError`).
* The **basis gates** are the only gates the chip runs (default `BASIS_GATES = ['rz', 'sx', 'x', 'cx']`). `measure` and `barrier` are always allowed.
* `LINE6 = [(0,1), (1,2), (2,3), (3,4), (4,5)]`. The helper `validate_device(coupling_edges, basis_gates)` is **provided**: it raises `ValueError` for an invalid device (empty coupling map, repeated or self couplings, empty basis) and returns `(edges, basis, num_qubits)`.
* The **baseline** is `baseline_transpile(circuit, edges, basis, seed)` (provided): Qiskit's lowest optimisation level - trivial layout, no optimisation - with the same device and seed.

### Function contracts
| Function | Input | Output | Raises `ValueError` when |
|---|---|---|---|
| `circuit_cost(circuit)` | a `QuantumCircuit` (counted **as it is**, nothing is decomposed) | `dict` with `depth` = `circuit.depth()` (Qiskit's definition: the longest chain of dependent operations, barriers do not count, measurements do), `two_qubit_gates` = gates acting on exactly two qubits, `total_gates` = all gates; **barriers, measurements and resets are not gates**. A composite gate counts as one gate | not a `QuantumCircuit` |
| `is_hardware_valid(circuit, coupling_edges, basis_gates)` | circuit, device | `bool`: `True` iff every instruction is a barrier, a measurement or a basis gate, every gate acts on qubits `< num_qubits` of the device, no gate acts on three or more qubits, and every two-qubit gate acts on a coupled pair (either direction) | invalid device, not a circuit |
| `optimize_for_hardware(circuit, coupling_edges, basis_gates=BASIS_GATES, seed=0, attempts=8)` | a unitary circuit with exactly as many qubits as the device | a `QuantumCircuit` that is hardware valid and implements the **same unitary** (up to a global phase) *including the layout and routing permutation the transpiler records in `circuit.layout`* - return the transpiler's circuit as it is. Equal arguments give equal circuits | too many / too few qubits, invalid device, `seed` not a non-negative integer, `attempts` not a positive integer |
| `cost_reduction(baseline, optimised, metric='two_qubit_gates')` | two cost dictionaries, `metric` in `depth`, `two_qubit_gates`, `total_gates` | `float` (baseline − optimised) / baseline; `0.0` if the baseline value is 0; negative if the result is *worse* | unknown metric, missing key, negative or non-finite value |
| *(bonus)* `ghz_chain_rewrite(n)` | integer n ≥ 2 | circuit on n qubits using only `h` and `cx`: H on qubit 0 and `n − 1` CNOTs between **neighbouring** qubits, preparing (\|0…0⟩ + \|1…1⟩)/√2 from \|0…0⟩ | n not an integer ≥ 2 |

**Correctness versus quality.** Correctness (exact checks): costs counted exactly as documented, validity decided exactly, the optimised circuit is valid, reproducible and equivalent (`Operator.from_circuit(...)` equals the original unitary up to a global phase, tolerance 1e-8). **Quality** (reported separately, never part of correctness): your result is *never worse than the baseline* in two-qubit gates on a set of test circuits and devices, and on the supplied reference circuit it needs **at least 25 % fewer two-qubit gates** than the baseline. The tests never look at the order or the names of gates inside your circuit.

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `circuit_cost` reports depth, two-qubit gate count and total gate count exactly as documented.
- `is_hardware_valid` accepts exactly the circuits that use only basis gates on coupled qubit pairs.
- `optimize_for_hardware` returns hardware-valid circuits.
- The optimised circuit implements the same unitary (up to global phase and the reported qubit layout).
- Optimisation is reproducible for a fixed seed.
- Invalid inputs (too many qubits, empty coupling map, negative seed) raise ValueError.
- `cost_reduction` returns (baseline - optimised) / baseline for the chosen metric: 0.0 for an empty baseline, negative for a worse circuit, ValueError for unknown metrics or bad cost dictionaries.

**Quality benchmarks** (reported separately from correctness - a stochastic optimiser is not required to be perfect):
- The optimised circuit is never worse than the baseline transpilation in two-qubit gates.
- On the supplied reference circuit the two-qubit gate count falls by at least 25% versus the baseline.

**Bonus (optional, never required to pass):**
- `ghz_chain_rewrite` hand-optimises the star-shaped GHZ preparation into a chain with n-1 two-qubit gates (state-equivalent).

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c10_public.py --impl challenges/challenge_10_transpilation/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
