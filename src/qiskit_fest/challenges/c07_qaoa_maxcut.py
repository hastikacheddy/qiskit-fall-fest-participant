"""Provided code for Challenge 7 - The Quantum Network Cut (Max-Cut with QAOA).

The provided pieces are input checks (``validate_graph``, ``validate_parameters``), the public example graph and plotting
helpers that call *your* functions. Nothing here evaluates a cut, builds a Hamiltonian or a QAOA circuit.

Conventions (identical in the problem statement and in every test)
* A graph is ``(num_nodes, edges)`` with nodes ``0 .. num_nodes - 1`` and ``edges`` a list of ``(u, v, weight)`` triples.
* Node ``u`` is qubit ``u``. In a bit-string (Qiskit order) node ``u`` is the character ``u`` from the RIGHT.
"""
from __future__ import annotations

import math
import numbers

import numpy as np

from .. import viz

#: Public example: five data centres (0-4) and six links with traffic weight 1. The classical optimum is 5.
EXAMPLE_NUM_NODES = 5
EXAMPLE_EDGES = [(0, 1, 1.0), (0, 2, 1.0), (1, 2, 1.0), (1, 3, 1.0), (2, 4, 1.0), (3, 4, 1.0)]
EXAMPLE_OPTIMUM = 5.0


def _is_integer(value) -> bool:
    return isinstance(value, numbers.Integral) and not isinstance(value, bool)


def validate_graph(num_nodes, edges) -> list[tuple[int, int, float]]:
    """Check a graph and return its edges as a list of ``(u, v, weight)`` with Python ``int`` / ``float`` entries.

    Raises ``ValueError`` if ``num_nodes`` is not an integer >= 1, an edge is not a triple, an endpoint is not an integer in
    ``[0, num_nodes - 1]``, an edge is a self-loop, a weight is not a finite real number, or the same undirected edge appears twice.
    """
    if not _is_integer(num_nodes) or num_nodes < 1:
        raise ValueError(f"num_nodes must be an integer >= 1, got {num_nodes!r}")
    try:
        items = list(edges)
    except TypeError:
        raise ValueError("edges must be a list of (u, v, weight) triples") from None
    clean, seen = [], set()
    for edge in items:
        try:
            u, v, w = edge
        except (TypeError, ValueError):
            raise ValueError(f"every edge must be a (u, v, weight) triple, got {edge!r}") from None
        if not (_is_integer(u) and _is_integer(v)) or not (0 <= u < num_nodes and 0 <= v < num_nodes):
            raise ValueError(f"edge endpoints must be integers in [0, {num_nodes - 1}], got {edge!r}")
        if u == v:
            raise ValueError(f"self-loops are not allowed, got {edge!r}")
        if isinstance(w, bool) or not isinstance(w, numbers.Real) or not math.isfinite(w):
            raise ValueError(f"the weight must be a finite real number, got {edge!r}")
        key = (min(int(u), int(v)), max(int(u), int(v)))
        if key in seen:
            raise ValueError(f"the edge {key} appears more than once")
        seen.add(key)
        clean.append((int(u), int(v), float(w)))
    return clean


def validate_parameters(gammas, betas) -> tuple[list[float], list[float]]:
    """Check QAOA parameters and return them as two lists of floats (``ValueError``: unequal lengths, non-finite entries or
    entries that are not real numbers). The empty lists (depth p = 0) are valid."""
    try:
        g = [x for x in gammas]
        b = [x for x in betas]
    except TypeError:
        raise ValueError("gammas and betas must be sequences of numbers") from None
    if len(g) != len(b):
        raise ValueError(f"gammas and betas need the same length (got {len(g)} and {len(b)})")
    for x in g + b:
        if isinstance(x, bool) or not isinstance(x, numbers.Real) or not math.isfinite(x):
            raise ValueError(f"QAOA parameters must be finite real numbers, got {x!r}")
    return [float(x) for x in g], [float(x) for x in b]


# ------------------------------------------------------------------------------------------------------------------
# plots (they call YOUR functions)
# ------------------------------------------------------------------------------------------------------------------
def plot_graph(num_nodes: int, edges, bitstring: str | None = None, title: str = "", *, show: bool = True):
    """Draw the graph on a circle. With a bit-string (Qiskit order) the two groups get two colours and the CUT edges are drawn
    solid and thick, the others dashed."""
    import matplotlib.pyplot as plt

    edges = validate_graph(num_nodes, edges)
    n = int(num_nodes)
    angles = np.pi / 2 + 2 * np.pi * np.arange(n) / n
    pos = {u: (np.cos(a), np.sin(a)) for u, a in enumerate(angles)}
    side = {u: int(bitstring[n - 1 - u]) for u in range(n)} if bitstring else {u: 0 for u in range(n)}
    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    for u, v, w in edges:
        cut = bitstring is not None and side[u] != side[v]
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=viz.PALETTE[1] if cut else "0.6",
                lw=3 if cut else 1.2, ls="-" if cut or bitstring is None else "--", zorder=1)
        if w != 1.0:
            ax.text((pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2, f"{w:g}", fontsize=8, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    for u in range(n):
        ax.scatter(*pos[u], s=520, color=viz.PALETTE[0] if side[u] == 0 else viz.PALETTE[2], edgecolor="white", zorder=2)
        ax.text(*pos[u], str(u), color="white", fontweight="bold", ha="center", va="center", zorder=3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_landscape(qaoa_expectation, num_nodes: int, edges, optimum: float | None = None, points: int = 31, title: str = "", *,
                   show: bool = True):
    """Heat map of YOUR ``qaoa_expectation`` for p = 1 over gamma in [0, 2 pi] and beta in [0, pi/2]; the best grid point is marked."""
    import matplotlib.pyplot as plt

    gammas = np.linspace(0, 2 * np.pi, points)
    betas = np.linspace(0, np.pi / 2, points)
    grid = np.array([[qaoa_expectation(num_nodes, edges, [g], [b]) for g in gammas] for b in betas])
    j, i = np.unravel_index(np.argmax(grid), grid.shape)
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    im = ax.imshow(grid, origin="lower", aspect="auto", extent=[0, 2 * np.pi, 0, np.pi / 2], cmap="viridis")
    ax.plot(gammas[i], betas[j], "*", color="white", ms=14, mec="k")
    cb = fig.colorbar(im, ax=ax)
    cb.set_label("<H_C>")
    ax.set_xlabel("gamma")
    ax.set_ylabel("beta")
    ax.set_title(title or f"p = 1 landscape: best grid value {grid.max():.3f}" + (f" of optimum {optimum:g}" if optimum is not None else ""),
                 fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_cut_histogram(num_nodes: int, edges, probabilities: dict, cut_value, title: str = "", *, show: bool = True, top: int = 16):
    """Bar chart of the most probable bit-strings of a QAOA state, coloured by their cut value (``cut_value`` is YOUR function)."""
    import matplotlib.pyplot as plt

    ranked = sorted(probabilities.items(), key=lambda kv: -kv[1])[:top]
    values = [cut_value(bits, edges) for bits, _ in ranked]
    levels = sorted(set(values))
    colour = {v: viz.PALETTE[i % len(viz.PALETTE)] for i, v in enumerate(levels)}
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.bar(range(len(ranked)), [p for _, p in ranked], color=[colour[v] for v in values], edgecolor="white")
    ax.set_xticks(range(len(ranked)), [bits for bits, _ in ranked], rotation=90, fontsize=8)
    ax.set_ylabel("probability")
    ax.set_title(title or "Most probable outcomes of the QAOA state (colour = cut value)", fontweight="bold")
    handles = [plt.Rectangle((0, 0), 1, 1, color=colour[v]) for v in levels]
    ax.legend(handles, [f"cut {v:g}" for v in levels], loc="upper right", fontsize=8)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
