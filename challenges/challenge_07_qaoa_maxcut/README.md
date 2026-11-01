# Challenge 7: The Quantum Network Cut

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/hastikacheddy/qiskit-fall-fest-participant/blob/main/challenges/challenge_07_qaoa_maxcut/challenge_07_qaoa_maxcut.ipynb)

**Tier 2 - Quantum Algorithms and Applications** · **Estimated time 45-60 min** · folder `challenges/challenge_07_qaoa_maxcut/`

> Split a small network into two data centres so that as many links as possible cross between them (Max-Cut). Compare a brute-force answer with a variational quantum approach (QAOA).

## Learning objectives
- Define the Max-Cut objective and compute it classically.
- Express it as a cost Hamiltonian made of Pauli Z operators.
- Build a QAOA circuit and optimise its parameters with a classical optimiser.
- Separate correctness checks from solution-quality benchmarks.

## Prerequisites
- Challenges 1-3 or equivalent
- Pauli Z and rotation gates
- A basic idea of optimisation (minimising a function)

## Files
- `challenge_07_qaoa_maxcut.ipynb` - the guided notebook (open this one)
- `starter.py` - the same TODO stubs as a plain Python file (for editors / the command line)

## The problem
A company runs a network of **data centres** connected by links; every link carries traffic with a known weight. The network is to be split into **two groups** of data centres. The traffic of all links *between* the groups is what the split **cuts**. Find a split that cuts as much traffic as possible - the **Max-Cut** problem. You will

1. compute the cut classically (`cut_value`, `brute_force_maxcut`),
2. write the problem as a **cost Hamiltonian** (`cost_hamiltonian`),
3. build the **QAOA** circuit (`qaoa_circuit`) and its exact energy (`qaoa_expectation`),
4. let a classical optimiser tune the circuit parameters (`solve_maxcut_qaoa`) and judge the result against the exact optimum.
5. *(Bonus)* ask how likely it is to *sample* an optimal cut, not just how good the average is (`optimal_cut_probability`).

### Conventions (used by the notebook and by every test)
* A **graph** is `(num_nodes, edges)`: nodes are `0 … num_nodes − 1`, `edges` is a list of `(u, v, weight)` triples (weights are finite real numbers; an undirected edge appears once; no self-loops). The helper `validate_graph(num_nodes, edges)` is provided: it raises `ValueError` for invalid graphs and returns the clean edge list.
* **Node `u` is qubit `u`.** A **bit-string** `z` is written in Qiskit order, so node `u` is the character `u` **from the right**: `z_u = z[n − 1 − u]`. The bit tells the group (0 or 1) of the node.
* **Cut value:** C(z) = Σ over edges (u, v, w) of w · [z_u ≠ z_v].
* **Cost Hamiltonian:** H_C = Σ w · (I − Z_u Z_v) / 2. Its eigenvalue on the basis state |z⟩ is exactly C(z); we *maximise* ⟨H_C⟩.
* **QAOA state with p layers** and parameters γ₁ … γ_p, β₁ … β_p:
  |γ, β⟩ = U_B(β_p) U_C(γ_p) ⋯ U_B(β₁) U_C(γ₁) · H^{⊗n} |0…0⟩,  with  U_C(γ) = exp(−i γ H_C)  and  U_B(β) = exp(−i β Σ_u X_u).
  Layer 1 is applied first; inside a layer the cost operator comes before the mixer. Global phases do not matter.

### Function contracts
| Function | Input | Output | Raises `ValueError` when |
|---|---|---|---|
| `cut_value(bitstring, edges)` | bit-string (its length is the number of nodes), edge list | `float` C(z) | bit-string empty / not 0-1, invalid edges (endpoints must be nodes of the bit-string) |
| `brute_force_maxcut(num_nodes, edges)` | graph with 1 … 16 nodes | `(best_value, optimal_strings)`: the maximum cut (`float`) and **all** bit-strings reaching it (within 1e-9), sorted as strings | invalid graph, more than 16 nodes |
| `cost_hamiltonian(num_nodes, edges)` | graph | `qiskit.quantum_info.SparsePauliOp` on `num_nodes` qubits with `diag(H_C)[int(z, 2)] = C(z)` | invalid graph |
| `qaoa_circuit(num_nodes, edges, gammas, betas)` | graph, two equally long lists of floats (p ≥ 0 layers) | `QuantumCircuit` on `num_nodes` qubits **without measurements**, preparing the QAOA state above (any gate decomposition) | invalid graph, unequal lengths, non-finite parameters |
| `qaoa_expectation(num_nodes, edges, gammas, betas)` | as above | `float` ⟨γ,β\|H_C\|γ,β⟩, exact | as above |
| `solve_maxcut_qaoa(num_nodes, edges, p=1, restarts=5, seed=0)` | graph, depth p ≥ 1, number of random restarts ≥ 1, integer seed ≥ 0 | `dict` with `gammas`, `betas` (lists of length p), `expectation` (= ⟨H_C⟩ at these parameters), `bitstring` (the **most probable** bit-string of the final state; among bit-strings within 1e-9 of the largest probability the one with the smaller integer value), `cut_value` (= C of that bit-string). Same arguments → same result | invalid graph, `p` / `restarts` not a positive integer, `seed` not a non-negative integer |
| *(bonus)* `optimal_cut_probability(num_nodes, edges, gammas, betas)` | as for `qaoa_expectation` | `float` in [0, 1]: the exact total probability of **all optimal bit-strings** (those reaching the maximum cut, within 1e-9 - the strings `brute_force_maxcut` lists) in the QAOA state | as for `qaoa_expectation` |

**Correctness versus quality.** The correctness tests are exact (tolerance 1e-9) and never depend on how good your optimiser is: the returned numbers must be *consistent* (the reported expectation is the expectation of the returned parameters, the reported cut is the cut of the returned bit-string, nothing exceeds the true optimum). **Quality benchmarks** are reported separately and are *not* part of correctness: with `p = 1` and `restarts = 15` (i) the returned expectation reaches at least 95 % of the best value of a dense (γ, β) grid, (ii) the returned cut has at least 80 % of the optimal cut weight. (The landscape has several local maxima; a single start finds the best one only about 40 % of the time on the example graph - that is what the restarts are for.)

## Acceptance criteria
Your solution is accepted when all **core** and **edge-case** requirements hold:
- `cut_value` evaluates the (weighted) cut of a bit-string in Qiskit bit order.
- `brute_force_maxcut` returns the exact optimum and all optimal bit-strings.
- `cost_hamiltonian` is the diagonal operator whose eigenvalue for each bit-string equals its cut value.
- `qaoa_circuit` prepares exactly the documented QAOA state (convention fixed in the problem statement).
- `qaoa_expectation` equals <psi|H_C|psi> and is invariant under node relabelling.
- `solve_maxcut_qaoa` is self-consistent: the reported cut value and expectation are recomputed from the returned bit-string and parameters.
- Invalid graphs, bit-strings and parameter lists raise ValueError.

**Quality benchmarks** (reported separately from correctness - a stochastic optimiser is not required to be perfect):
- p=1 QAOA with restarts reaches a good fraction of the best p=1 expectation (benchmark, not correctness).
- The returned bit-string is a high-quality cut relative to the exact optimum (benchmark, not correctness).

**Bonus (optional, never required to pass):**
- `optimal_cut_probability` is the exact probability that one measurement of the QAOA state returns an optimal cut (every bit-string that reaches the maximum cut, ties included): the share of optimal strings at zero parameters, unchanged by relabelling the nodes.

## Check your work
- In the notebook: run the *public checks* cell (`run_public_checks`).
- From a terminal, with the starter file: `pytest tests/public/test_c07_public.py --impl challenges/challenge_07_qaoa_maxcut/starter.py`
- The instructors also run hidden tests (different inputs, edge cases) - passing the public checks is necessary, not sufficient.
