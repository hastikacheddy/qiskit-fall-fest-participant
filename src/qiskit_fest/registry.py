"""Metadata of the ten challenges (single source of truth).

The notebook builder, the public/hidden tests, the grading script and the documentation generators all read this
module, so titles, time estimates, function contracts and requirement ids cannot drift apart.

Nothing in here is secret: it describes *what* is asked, never *how* to solve it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TIER_NAMES = {1: "Foundations", 2: "Quantum Algorithms and Applications", 3: "Advanced Challenges"}

#: Test tiers used by the pytest markers of the public and the instructor test suites (see qiskit_fest.testing).
# "meta" tests validate the exercise itself (e.g. that a supplied buggy circuit really is wrong) - never graded.
TEST_TIERS = ("smoke", "core", "edge", "quality", "bonus", "meta")

#: Default scoring framework (percent). Individual challenges override it, see ``Challenge.rubric``.
DEFAULT_RUBRIC = {"core": 60, "edge": 20, "explanation": 10, "code": 10}
QUALITY_RUBRIC = {"core": 50, "edge": 15, "quality": 15, "explanation": 10, "code": 10}

#: The public participant repository (owner/name) and its default branch. The setup cell of every notebook fetches the project from here when a notebook is
#: opened straight from GitHub in Google Colab, and the "Open in Colab" badges of the notebooks and READMEs point to it. If the repository is renamed or moved,
#: change it here and run ``python scripts/build_notebooks.py`` (the README table must be updated by hand; a test compares it with these values).
PUBLIC_REPOSITORY = "hastikacheddy/qiskit-fall-fest-participant"
PUBLIC_BRANCH = "main"
COLAB_BADGE = "https://colab.research.google.com/assets/colab-badge.svg"


@dataclass(frozen=True)
class Requirement:
    id: str
    text: str
    tier: str  # one of TEST_TIERS


@dataclass(frozen=True)
class Challenge:
    number: int
    slug: str
    title: str
    tier: int
    minutes: tuple[int, int]
    scenario: str
    prerequisites: tuple[str, ...]
    objectives: tuple[str, ...]
    functions: tuple[str, ...]
    bonus_functions: tuple[str, ...]
    requirements: tuple[Requirement, ...]
    extra_packages: tuple[str, ...] = ()
    rubric: dict = field(default_factory=lambda: dict(DEFAULT_RUBRIC))

    @property
    def tier_name(self) -> str:
        return TIER_NAMES[self.tier]

    @property
    def folder(self) -> str:
        return f"challenge_{self.number:02d}_{self.slug}"

    @property
    def notebook_name(self) -> str:
        return f"{self.folder}.ipynb"

    @property
    def all_functions(self) -> tuple[str, ...]:
        return self.functions + self.bonus_functions

    def requirement(self, rid: str) -> Requirement:
        return next(r for r in self.requirements if r.id == rid)


def _r(cid: int, n: int, tier: str, text: str) -> Requirement:
    return Requirement(f"C{cid:02d}-R{n}", text, tier)


CHALLENGES: tuple[Challenge, ...] = (
    Challenge(
        number=1, slug="superposition", title="Superposition Under the Microscope", tier=1, minutes=(15, 25),
        scenario="A lab technician needs a one-qubit source that, when measured, gives 0 or 1 with equal probability - "
                 "and wants to understand exactly what the *amplitudes* behind those probabilities are.",
        prerequisites=("Basic Python (functions, lists, NumPy arrays)", "What a qubit is: the states |0> and |1>",
                       "No prior Qiskit experience required"),
        objectives=("Build a one-qubit circuit with Qiskit and simulate it exactly.",
                    "Explain the difference between amplitudes (complex) and measurement probabilities (real, Born rule).",
                    "Distinguish exact probabilities from finite-shot frequencies.",
                    "Know that different phases can hide behind identical probabilities."),
        functions=("superposition_circuit", "born_probabilities", "exact_probabilities"),
        bonus_functions=("circuit_for_probability", "circuit_for_phase_state"),
        requirements=(
            _r(1, 1, "core", "`superposition_circuit()` returns a valid one-qubit circuit (no measurement or classical control)."),
            _r(1, 2, "core", "The circuit's exact outcome probabilities are (1/2, 1/2); every equivalent construction is accepted."),
            _r(1, 3, "core", "`born_probabilities` applies the Born rule |amplitude|^2 to valid amplitude vectors of any length 2^n."),
            _r(1, 4, "edge", "`born_probabilities` rejects invalid input (not normalised, bad length or shape, non-finite) and never modifies its argument."),
            _r(1, 5, "core", "`exact_probabilities` returns the exact outcome distribution of an n-qubit circuit in Qiskit bit order."),
            _r(1, 6, "edge", "`exact_probabilities` rejects circuits that contain measurements."),
            _r(1, 7, "bonus", "`circuit_for_probability(p0)` prepares any distribution with P(0) = p0 (non-uniform targets)."),
            _r(1, 8, "bonus", "`circuit_for_phase_state(p0, phi)` prepares the requested relative phase (same Z probabilities, different X/Y expectations)."),
        ),
    ),
    Challenge(
        number=2, slug="entanglement", title="The Entanglement Detective", tier=1, minutes=(20, 30),
        scenario="Two qubits always give matching answers. Is that entanglement - or just two coins that were set to the "
                 "same face? Collect the evidence like a detective.",
        prerequisites=("Challenge 1 or equivalent: gates, exact simulation, probabilities", "The H and CNOT gates"),
        objectives=("Construct a Bell state and read its joint measurement outcomes.",
                    "Show that correlation in a single basis is not proof of entanglement.",
                    "Measure correlations in several bases (Z, X, Y).",
                    "Decide entanglement of a pure two-qubit state from the purity of one qubit."),
        functions=("bell_circuit", "joint_probabilities", "correlation_in_basis", "is_entangled"),
        bonus_functions=("chsh_value",),
        requirements=(
            _r(2, 1, "core", "`bell_circuit()` prepares |Phi+> = (|00>+|11>)/sqrt(2) (up to global phase) with unitary gates only."),
            _r(2, 2, "core", "Independent superposition (H on both qubits) is not accepted: in the Bell state each qubit alone is maximally mixed."),
            _r(2, 3, "core", "`joint_probabilities` returns the exact probability of all 2^n outcomes in Qiskit bit order."),
            _r(2, 4, "core", "`correlation_in_basis` equals <sigma x sigma> for sigma in {Z, X, Y} on arbitrary two-qubit states."),
            _r(2, 5, "core", "`is_entangled` separates entangled from product states, including perfectly Z-correlated product states."),
            _r(2, 6, "edge", "Inputs that are not two-qubit states, and unknown bases, raise ValueError; the tolerance is respected."),
            _r(2, 7, "bonus", "`chsh_value` reproduces the CHSH quantity (2*sqrt(2) for the Bell state, at most 2 for product states)."),
        ),
    ),
    Challenge(
        number=3, slug="gate_surgeon", title="Gate Surgeon", tier=1, minutes=(20, 30),
        scenario="Three circuits arrive at the clinic with symptoms: wrong states, wrong unitaries, wrong angles. "
                 "Diagnose the bugs and operate - without changing what each circuit is supposed to do.",
        prerequisites=("Challenges 1-2 or equivalent", "Qubit ordering in Qiskit (qubit 0 is the rightmost bit)"),
        objectives=("Read a circuit and predict the state it prepares.",
                    "Debug common mistakes: wrong qubit, reversed CNOT, stray gate, wrong rotation angle.",
                    "Verify a repair by comparing states and unitaries, not by eye.",
                    "Recognise that many different circuits can be correct."),
        functions=("patient_ghz", "patient_swap", "patient_tilted_pair"),
        bonus_functions=("patient_readout",),
        requirements=(
            _r(3, 1, "core", "`patient_ghz()` returns a three-qubit circuit preparing (|000>+|111>)/sqrt(2) (up to global phase)."),
            _r(3, 2, "core", "`patient_swap()` uses only CX gates (at most three) and implements SWAP (up to global phase)."),
            _r(3, 3, "core", "`patient_tilted_pair(theta)` prepares cos(theta/2)|00> + sin(theta/2)|11> for every theta."),
            _r(3, 4, "edge", "Non-finite theta is rejected with ValueError; the returned circuits are measurement-free and have the documented width."),
            _r(3, 5, "bonus", "`patient_readout()` yields the deterministic bit-string '110' with qubit i measured into clbit i."),
            _r(3, 6, "meta", "The supplied buggy circuits really violate their specifications (the exercise is well posed)."),
        ),
    ),
    Challenge(
        number=4, slug="teleportation", title="Teleport the Qubit", tier=2, minutes=(40, 60),
        scenario="Alice must send an unknown qubit state to Bob. She may not look at it, copy it, or fly it over - but she "
                 "can share an entangled pair in advance and send two ordinary bits by phone.",
        prerequisites=("Challenges 1-3 or equivalent", "Bell states", "Mid-circuit measurement and classical control (`if_test`) are introduced in the notebook"),
        objectives=("Implement the three stages of teleportation: entanglement, Bell-basis measurement, correction.",
                    "Explain why two classical bits are necessary and why nothing travels faster than light.",
                    "Use classically controlled gates in Qiskit.",
                    "Verify a protocol on many input states, not on a single lucky one."),
        functions=("create_bell_pair", "alice_bell_measurement", "bob_correction"),
        bonus_functions=("average_bob_state_without_correction",),
        requirements=(
            _r(4, 1, "core", "`create_bell_pair` leaves the message qubit untouched and puts the two named qubits in |Phi+>."),
            _r(4, 2, "core", "`alice_bell_measurement` performs CNOT, H and both measurements; all four outcomes are equally likely and Bob's state in branch (z, x) is X^x Z^z |psi>."),
            _r(4, 3, "core", "`bob_correction` restores |psi> for each of the four classical outcomes using classically controlled gates."),
            _r(4, 4, "core", "The assembled protocol teleports many different states with fidelity >= 1 - 1e-9 in every branch."),
            _r(4, 5, "edge", "The functions work for any distinct qubit indices (nothing hard-coded) and reject invalid ones."),
            _r(4, 6, "bonus", "Without the classical bits Bob's average state is maximally mixed for every input (no signalling)."),
        ),
    ),
    Challenge(
        number=5, slug="grover", title="Find the Hidden State", tier=2, minutes=(40, 60),
        scenario="A vault accepts exactly one n-bit code. Checking codes one by one takes ~2^n tries; Grover's algorithm "
                 "needs only ~sqrt(2^n) oracle calls. Build the search and watch the amplitude of the hidden code grow.",
        prerequisites=("Challenges 1-3 or equivalent", "Multi-controlled gates", "Superposition and phase"),
        objectives=("Implement a phase oracle that marks one basis state.",
                    "Implement the diffuser (inversion about the mean).",
                    "Explain phase marking and amplitude amplification geometrically.",
                    "Choose the number of iterations and observe what happens when you overshoot."),
        functions=("phase_oracle", "diffuser", "optimal_iterations", "grover_circuit"),
        bonus_functions=("phase_oracle_multi",),
        requirements=(
            _r(5, 1, "core", "`phase_oracle(marked)` flips the sign of exactly the marked basis state (up to global phase), in Qiskit bit order."),
            _r(5, 2, "core", "`diffuser(n)` implements the inversion about the uniform superposition, 2|s><s| - I (up to global phase)."),
            _r(5, 3, "core", "`optimal_iterations(n, num_marked)` returns an iteration count that maximises the ideal success probability."),
            _r(5, 4, "core", "`grover_circuit` reaches the theoretical success probability sin^2((2k+1)theta) for every marked state and iteration count."),
            _r(5, 5, "edge", "Invalid marked strings, sizes and iteration counts raise ValueError; returned circuits have the documented width, no measurements, and are independent objects."),
            _r(5, 6, "bonus", "`phase_oracle_multi` handles several marked states and Grover with M solutions matches theory."),
            _r(5, 7, "meta", "The provided helpers (`success_probability`, `theoretical_success`) agree with an independent matrix simulation, so the notebook plots can be trusted."),
        ),
    ),
    Challenge(
        number=6, slug="noise", title="Fight the Noise", tier=2, minutes=(40, 60),
        scenario="Your ideal circuit works perfectly - on paper. Real devices are noisy. Quantify exactly how much "
                 "damage a documented noise model does, and test whether a mitigation trick really helps.",
        prerequisites=("Challenges 1-2 or equivalent", "Measurement counts", "Qiskit Aer (installed as an optional extra)"),
        objectives=("Build a noise model with gate (depolarising) and readout errors.",
                    "Run ideal and noisy experiments under identical, reproducible settings.",
                    "Quantify the deviation with the total variation distance.",
                    "Evaluate - not assume - a simple mitigation technique."),
        functions=("build_noise_model", "run_counts", "total_variation_distance", "noise_report"),
        bonus_functions=("calibration_matrix", "mitigate_readout", "evaluate_mitigation"),
        extra_packages=("qiskit-aer==0.18.0",),
        requirements=(
            _r(6, 1, "core", "`build_noise_model` attaches depolarising errors with the documented parameters to sx, x and cx and a symmetric readout error to every qubit."),
            _r(6, 2, "core", "`run_counts` configures ideal and noisy runs consistently (same transpilation, shots and seed) and is reproducible."),
            _r(6, 3, "core", "`total_variation_distance` is a correct distance between count dictionaries."),
            _r(6, 4, "core", "`noise_report` quantifies noise: TVD against the exact ideal distribution and probability mass outside the ideal support."),
            _r(6, 5, "core", "Stronger noise gives a larger measured deviation (controlled seed, statistical tolerance)."),
            _r(6, 6, "edge", "Invalid probabilities, shots and empty inputs raise ValueError; `run_counts` does not modify the circuit it is given."),
            _r(6, 7, "bonus", "`calibration_matrix` / `mitigate_readout` invert a known readout channel exactly and return valid distributions."),
            _r(6, 8, "bonus", "`evaluate_mitigation` reports measured numbers: mitigation helps for readout-only noise and is not claimed to fix gate noise."),
            _r(6, 9, "meta", "The NumPy ground truth used by the tests agrees with Aer's exact density-matrix simulation (so the tests judge against correct numbers)."),
        ),
        rubric=dict(DEFAULT_RUBRIC),
    ),
    Challenge(
        number=7, slug="qaoa_maxcut", title="The Quantum Network Cut", tier=2, minutes=(45, 60),
        scenario="Split a small network into two data centres so that as many links as possible cross between them (Max-Cut). "
                 "Compare a brute-force answer with a variational quantum approach (QAOA).",
        prerequisites=("Challenges 1-3 or equivalent", "Pauli Z and rotation gates", "A basic idea of optimisation (minimising a function)"),
        objectives=("Define the Max-Cut objective and compute it classically.",
                    "Express it as a cost Hamiltonian made of Pauli Z operators.",
                    "Build a QAOA circuit and optimise its parameters with a classical optimiser.",
                    "Separate correctness checks from solution-quality benchmarks."),
        functions=("cut_value", "brute_force_maxcut", "cost_hamiltonian", "qaoa_circuit", "qaoa_expectation", "solve_maxcut_qaoa"),
        bonus_functions=("optimal_cut_probability",),
        requirements=(
            _r(7, 1, "core", "`cut_value` evaluates the (weighted) cut of a bit-string in Qiskit bit order."),
            _r(7, 2, "core", "`brute_force_maxcut` returns the exact optimum and all optimal bit-strings."),
            _r(7, 3, "core", "`cost_hamiltonian` is the diagonal operator whose eigenvalue for each bit-string equals its cut value."),
            _r(7, 4, "core", "`qaoa_circuit` prepares exactly the documented QAOA state (convention fixed in the problem statement)."),
            _r(7, 5, "core", "`qaoa_expectation` equals <psi|H_C|psi> and is invariant under node relabelling."),
            _r(7, 6, "core", "`solve_maxcut_qaoa` is self-consistent: the reported cut value and expectation are recomputed from the returned bit-string and parameters."),
            _r(7, 7, "edge", "Invalid graphs, bit-strings and parameter lists raise ValueError."),
            _r(7, 8, "quality", "p=1 QAOA with restarts reaches a good fraction of the best p=1 expectation (benchmark, not correctness)."),
            _r(7, 9, "quality", "The returned bit-string is a high-quality cut relative to the exact optimum (benchmark, not correctness)."),
            _r(7, 10, "bonus", "`optimal_cut_probability` is the exact probability that one measurement of the QAOA state returns an optimal cut (every bit-string that reaches the maximum cut, ties included): the share of optimal strings at zero parameters, unchanged by relabelling the nodes."),
            _r(7, 11, "meta", "The independent NumPy ground truth of the bonus quantity agrees with hand-derived values (single-edge closed form, ring, K4, the public example, an edgeless graph)."),
        ),
        rubric=dict(QUALITY_RUBRIC),
    ),
    Challenge(
        number=8, slug="quantum_ml", title="Teach a Quantum Circuit", tier=3, minutes=(60, 90),
        scenario="Train a two-qubit variational circuit to classify points in the plane, evaluate it honestly on held-out "
                 "data, and compare it with a classical baseline - without leaking test data into training.",
        prerequisites=("Challenges 1-3 and 7 or equivalent", "Parameterised circuits", "Train/test splits and accuracy"),
        objectives=("Encode classical features into a quantum circuit and read out a prediction.",
                    "Train circuit parameters with a classical optimiser.",
                    "Avoid train/test leakage and compute evaluation metrics correctly.",
                    "Compare fairly with a classical baseline and discuss what the comparison does (not) show."),
        functions=("scale_features", "variational_ansatz", "model_output", "mse_loss", "train_vqc", "binary_metrics", "run_experiment"),
        bonus_functions=("parameter_shift_gradient",),
        requirements=(
            _r(8, 1, "core", "`scale_features` fits min-max scaling to [0, pi] on the training data only (no train/test leakage)."),
            _r(8, 2, "core", "`variational_ansatz` returns a parameterised circuit with the documented dimensions."),
            _r(8, 3, "core", "`model_output` is the exact <Z_0> of feature map plus ansatz: finite and within [-1, 1]."),
            _r(8, 4, "core", "`mse_loss` equals the mean squared error between model outputs and +-1 labels."),
            _r(8, 5, "core", "`train_vqc` uses the documented seeded initialisation, is reproducible and never ends worse than it started."),
            _r(8, 6, "core", "`binary_metrics` computes accuracy, precision, recall and F1 correctly, including degenerate cases."),
            _r(8, 7, "core", "`run_experiment` is leakage-free: training never sees test data; reported test metrics are recomputed from the returned model."),
            _r(8, 8, "quality", "Held-out accuracy is clearly above chance on the supplied dataset and the training loss falls (benchmark, not correctness)."),
            _r(8, 9, "bonus", "`parameter_shift_gradient` matches finite differences."),
            _r(8, 10, "edge", "Invalid shapes, non-finite values, labels other than -1/+1, wrong parameter counts and invalid layer numbers raise ValueError; no function modifies its inputs."),
            _r(8, 11, "meta", "The NumPy ground truth agrees with the Qiskit circuit of the documented model, and the supplied dataset is reproducible, balanced and split without overlap."),
        ),
        rubric=dict(QUALITY_RUBRIC),
    ),
    Challenge(
        number=9, slug="error_correction", title="Protect the Logical Qubit", tier=3, minutes=(50, 80),
        scenario="A memory qubit sits idle and an occasional bit flip sneaks in. Spread one logical qubit over three "
                 "physical ones, detect the flip without looking at the data, and undo it.",
        prerequisites=("Challenges 1-4 or equivalent", "CNOT and Pauli X", "Mid-circuit measurement and `if_test` (introduced in the notebook)"),
        objectives=("Encode a logical qubit in the three-qubit bit-flip repetition code.",
                    "Extract an error syndrome without disturbing the encoded information.",
                    "Decode the syndrome and apply the correction with classical feed-forward.",
                    "State precisely what this code can and cannot protect against."),
        functions=("encode_circuit", "syndrome_circuit", "decode_syndrome", "correction_circuit", "add_feedforward_correction"),
        bonus_functions=("phase_flip_encode_circuit",),
        requirements=(
            _r(9, 1, "core", "`encode_circuit` maps alpha|0>+beta|1> (on qubit 0) to alpha|000>+beta|111>."),
            _r(9, 2, "core", "`syndrome_circuit` writes the two parity checks into the ancillas without disturbing the logical information."),
            _r(9, 3, "core", "`decode_syndrome` identifies each single bit-flip location, and 'no error', from the syndrome."),
            _r(9, 4, "core", "`correction_circuit` applies X to the requested qubit (or nothing)."),
            _r(9, 5, "core", "`add_feedforward_correction` recovers the logical state after any single bit flip, for many logical states."),
            _r(9, 6, "edge", "Invalid syndromes and qubit indices raise ValueError."),
            _r(9, 7, "meta", "Documented limitations hold: phase flips and double bit flips are NOT corrected (checks that the documentation is true)."),
            _r(9, 8, "bonus", "`phase_flip_encode_circuit` yields a code that corrects any single Z error."),
        ),
    ),
    Challenge(
        number=10, slug="transpilation", title="The Hardware Architect", tier=3, minutes=(45, 75),
        scenario="Your algorithm assumes every qubit can talk to every other. The chip's qubits sit on a line. Re-engineer the "
                 "circuit for this hardware - cheaper, shallower, and still doing exactly the same thing.",
        prerequisites=("Challenges 1-5 or equivalent", "Circuit depth and gate counts", "The idea of a coupling map (which qubits are connected)"),
        objectives=("Measure circuit cost with depth and two-qubit gate count.",
                    "Check that a circuit respects a coupling map and a basis-gate set.",
                    "Use the transpiler (layout, routing, optimisation level, seeds) to reduce cost.",
                    "Verify that an optimised circuit still implements the same unitary."),
        functions=("circuit_cost", "is_hardware_valid", "optimize_for_hardware", "cost_reduction"),
        bonus_functions=("ghz_chain_rewrite",),
        requirements=(
            _r(10, 1, "core", "`circuit_cost` reports depth, two-qubit gate count and total gate count exactly as documented."),
            _r(10, 2, "core", "`is_hardware_valid` accepts exactly the circuits that use only basis gates on coupled qubit pairs."),
            _r(10, 3, "core", "`optimize_for_hardware` returns hardware-valid circuits."),
            _r(10, 4, "core", "The optimised circuit implements the same unitary (up to global phase and the reported qubit layout)."),
            _r(10, 5, "core", "Optimisation is reproducible for a fixed seed."),
            _r(10, 6, "edge", "Invalid inputs (too many qubits, empty coupling map, negative seed) raise ValueError."),
            _r(10, 7, "quality", "The optimised circuit is never worse than the baseline transpilation in two-qubit gates."),
            _r(10, 8, "quality", "On the supplied reference circuit the two-qubit gate count falls by at least 25% versus the baseline."),
            _r(10, 9, "bonus", "`ghz_chain_rewrite` hand-optimises the star-shaped GHZ preparation into a chain with n-1 two-qubit gates (state-equivalent)."),
            _r(10, 10, "core", "`cost_reduction` returns (baseline - optimised) / baseline for the chosen metric: 0.0 for an empty baseline, negative for a worse circuit, ValueError for unknown metrics or bad cost dictionaries."),
            _r(10, 11, "meta", "The independent cost counter and validity checker of the tests agree with hand-labelled cases, and the quality benchmark of the reference circuit is reachable with the transpiler."),
        ),
        rubric=dict(QUALITY_RUBRIC),
    ),
)


def get(number: int) -> Challenge:
    """Return the challenge with the given number (1-10)."""
    for ch in CHALLENGES:
        if ch.number == number:
            return ch
    raise KeyError(f"no challenge number {number}")


def all_requirement_ids() -> list[str]:
    return [r.id for ch in CHALLENGES for r in ch.requirements]


def repository_url() -> str:
    """The HTTPS address ``git clone`` uses for the public participant repository."""
    return f"https://github.com/{PUBLIC_REPOSITORY}.git"


def colab_url(challenge: int | Challenge) -> str:
    """The address that opens the participant notebook of ``challenge`` (number or :class:`Challenge`) straight from GitHub in Google Colab."""
    ch = get(challenge) if isinstance(challenge, int) else challenge
    return f"https://colab.research.google.com/github/{PUBLIC_REPOSITORY}/blob/{PUBLIC_BRANCH}/challenges/{ch.folder}/{ch.notebook_name}"


def colab_badge(challenge: int | Challenge) -> str:
    """Markdown for the "Open in Colab" badge of a challenge."""
    return f"[![Open In Colab]({COLAB_BADGE})]({colab_url(challenge)})"
