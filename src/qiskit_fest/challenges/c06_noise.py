"""Provided code for Challenge 6 - Fight the Noise.

Nothing here builds a noise model, runs a noisy experiment or computes a distance: those are your TODOs. The helpers provide

* the baseline circuit and the documented noise parameters,
* ``ideal_distribution`` - the *exact* outcome distribution of a measured circuit (no shots involved),
* two tiny probes that let you check your own noise model against the documentation,
* plotting helpers that call *your* functions.

Qiskit Aer is imported inside the functions that need it, so importing this module works without Aer installed.
"""
from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .. import viz

#: The transpilation target of ``run_counts`` (the usual IBM native gate set; ``rz`` is virtual, i.e. noiseless).
BASIS_GATES = ["id", "rz", "sx", "x", "cx"]

#: The documented noise parameters used throughout the notebook: orders of magnitude typical for superconducting devices,
#: NOT a model of one specific chip.
DOCUMENTED_NOISE = {"p1": 0.002, "p2": 0.015, "p_readout": 0.02}


def baseline_circuit(n: int = 3) -> QuantumCircuit:
    """GHZ preparation (H on qubit 0, then a chain of CNOTs) followed by measuring every qubit (qubit i -> classical bit i).

    Ideal outcomes: all zeros and all ones, each with probability 1/2.
    """
    if not isinstance(n, int) or n < 2:
        raise ValueError("n must be an integer >= 2")
    qc = QuantumCircuit(n)
    qc.h(0)
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.measure_all()
    return qc


def ideal_distribution(circuit: QuantumCircuit) -> dict[str, float]:
    """Exact outcome distribution ``{bit-string: probability}`` of a circuit that measures every qubit at the very end.

    Requirements: all measurements are final and qubit i is measured into classical bit i (as ``measure_all()`` does).
    Outcomes with probability below 1e-12 are left out, so the keys are exactly the *ideal support*.
    """
    n = circuit.num_qubits
    body = QuantumCircuit(n)
    measured = {}
    for inst in circuit.data:
        name = inst.operation.name
        if name == "barrier":
            continue
        if name == "measure":
            measured[circuit.find_bit(inst.qubits[0]).index] = circuit.find_bit(inst.clbits[0]).index
            continue
        if measured:
            raise ValueError("gates after a measurement are not supported (all measurements must be at the end)")
        body.append(inst.operation, [circuit.find_bit(q).index for q in inst.qubits])
    if measured != {q: q for q in range(n)}:
        raise ValueError("every qubit must be measured into the classical bit with the same index (use measure_all())")
    body.global_phase = circuit.global_phase
    probs = np.abs(Statevector(body).data) ** 2
    return {format(i, f"0{n}b"): float(p) for i, p in enumerate(probs) if p > 1e-12}


# ------------------------------------------------------------------------------------------------------------------
# probes: check your noise model against the documentation
# ------------------------------------------------------------------------------------------------------------------
def probe_x_gate(noise_model) -> float:
    """EXACT probability of finding |1> after a single ``x`` gate applied to |0> under ``noise_model`` (density-matrix
    simulation, no shots, readout error not applied). Without noise this is 1; with a depolarising error p1 it is 1 - p1/2."""
    from qiskit_aer import AerSimulator  # noqa: F401  (also registers qc.save_density_matrix)

    qc = QuantumCircuit(1)
    qc.x(0)
    qc.save_density_matrix()
    result = AerSimulator(method="density_matrix", noise_model=noise_model).run(qc, shots=1).result()
    return float(np.real(np.asarray(result.data(0)["density_matrix"])[1, 1]))


def probe_readout(noise_model, shots: int = 20000, seed: int = 7) -> float:
    """Fraction of shots in which a qubit that is in |0> and measured *without any gate* is read as 1."""
    from qiskit_aer import AerSimulator

    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)
    counts = AerSimulator(noise_model=noise_model, seed_simulator=seed).run(qc, shots=shots, seed_simulator=seed).result().get_counts()
    return counts.get("1", 0) / shots


# ------------------------------------------------------------------------------------------------------------------
# plots (they call YOUR functions)
# ------------------------------------------------------------------------------------------------------------------
def plot_histograms(exact: dict, counts_ideal: dict, counts_noisy: dict, title: str = "Ideal versus noisy outcomes", *, show: bool = True):
    """Grouped bars: the exact ideal distribution, the sampled ideal run and the sampled noisy run (counts are normalised)."""
    def norm(counts):
        total = float(sum(counts.values()))
        return {k: v / total for k, v in counts.items()}

    return viz.plot_distributions({"exact ideal": exact, "ideal run (sampled)": norm(counts_ideal), "noisy run (sampled)": norm(counts_noisy)},
                                  title=title, show=show, figsize=(8.5, 3.8))


def noise_scales(base: dict | None = None, scale: float = 1.0, parts=("p1", "p2", "p_readout")) -> dict:
    """``base`` noise parameters multiplied by ``scale`` for the chosen ``parts`` (others set to 0), capped at 1."""
    base = base or DOCUMENTED_NOISE
    return {k: (min(1.0, base[k] * scale) if k in parts else 0.0) for k in base}


def tvd_sweep(circuit, noise_report, build_noise_model, scales=(0.0, 0.5, 1.0, 2.0, 4.0), shots: int = 4000, seeds=(1, 2, 3),
              base: dict | None = None, parts=("p1", "p2", "p_readout")) -> dict:
    """Run YOUR ``noise_report`` for several noise strengths and seeds. Returns ``{'scales', 'noisy': [[tvd per seed]...], 'floor': [...]}``."""
    noisy, floor = [], []
    for s in scales:
        model = build_noise_model(**noise_scales(base, s, parts))
        reps = [noise_report(circuit, model, shots=shots, seed=seed) for seed in seeds]
        noisy.append([r["tvd_noisy"] for r in reps])
        floor.append([r["tvd_ideal"] for r in reps])
    return {"scales": list(scales), "noisy": noisy, "floor": floor}


def plot_tvd_sweep(sweep: dict, title: str = "Deviation from the ideal distribution versus noise strength", *, show: bool = True):
    """TVD against the exact ideal distribution (mean and range over seeds) with the shot-noise floor of the ideal runs."""
    import matplotlib.pyplot as plt

    s = np.asarray(sweep["scales"], dtype=float)
    noisy, floor = np.asarray(sweep["noisy"]), np.asarray(sweep["floor"])
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.fill_between(s, noisy.min(axis=1), noisy.max(axis=1), color=viz.PALETTE[1], alpha=0.25, label="noisy runs: range over seeds")
    ax.plot(s, noisy.mean(axis=1), "o-", color=viz.PALETTE[1], lw=2, label="noisy runs: mean TVD")
    ax.axhline(float(floor.mean()), color="k", ls="--", lw=1, label="shot-noise floor (ideal runs)")
    ax.set_xlabel("noise strength (1 = documented parameters)")
    ax.set_ylabel("TVD to the exact ideal distribution")
    ax.set_title(title, fontweight="bold")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_mitigation(exact: dict, raw_counts: dict, mitigated: dict, title: str = "Readout mitigation", *, show: bool = True):
    """Grouped bars: exact ideal distribution, raw noisy frequencies and the mitigated distribution."""
    total = float(sum(raw_counts.values()))
    raw = {k: v / total for k, v in raw_counts.items()}
    return viz.plot_distributions({"exact ideal": exact, "raw noisy": raw, "mitigated": mitigated}, title=title, show=show, figsize=(8.5, 3.8))
