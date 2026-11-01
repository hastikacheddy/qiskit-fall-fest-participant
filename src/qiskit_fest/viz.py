"""Small plotting helpers shared by the notebooks (Matplotlib only; Okabe-Ito colour-blind-safe palette)."""
from __future__ import annotations

from typing import Mapping, Sequence

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#999999"]


def _in_notebook() -> bool:
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False


def _finish(fig, show: bool):
    """Display the figure (and close it) when ``show`` is true; otherwise hand it back.

    Qiskit's drawers return figures that pyplot has already closed, so a notebook needs an explicit ``display``.
    """
    if not show:
        return fig
    if _in_notebook():
        from IPython.display import display

        display(fig)
        plt.close(fig)
        return None
    if matplotlib.get_backend().lower() == "agg":  # headless run (tests): nothing to display
        plt.close(fig)
        return None
    plt.show()
    return None


def draw_circuit(circuit, title: str | None = None, *, show: bool = True, fold: int = -1, scale: float = 0.8):
    """Draw a Qiskit circuit (Matplotlib drawer; falls back to text if the drawer's optional dependency is missing)."""
    try:
        fig = circuit.draw("mpl", fold=fold, scale=scale)
    except Exception:  # e.g. pylatexenc missing
        print(circuit.draw("text"))
        return None
    if title:
        fig.suptitle(title, fontweight="bold")
    return _finish(fig, show)


def plot_distributions(dists: Mapping[str, Mapping[str, float]], title: str = "", ylabel: str = "probability",
                       *, show: bool = True, ylim: tuple[float, float] | None = (0, 1.05), figsize=(7, 3.6)):
    """Grouped bar chart of several probability distributions over the same bit-strings (keys are bit-strings)."""
    keys = sorted({k for d in dists.values() for k in d})
    width = 0.8 / max(len(dists), 1)
    crowded = len(dists) >= 3  # three or more bars per outcome: write the value labels vertically so they do not overlap
    fig, ax = plt.subplots(figsize=figsize)
    top = 0.0
    for i, (label, d) in enumerate(dists.items()):
        vals = [float(d.get(k, 0.0)) for k in keys]
        top = max([top] + vals)
        bars = ax.bar(np.arange(len(keys)) + (i - (len(dists) - 1) / 2) * width, vals, width, label=label,
                      color=PALETTE[i % len(PALETTE)], edgecolor="white")
        if len(keys) <= 8:
            for b, v in zip(bars, vals):
                if crowded:
                    ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", va="bottom", fontsize=7, rotation=90)
                else:
                    ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}", ha="center", fontsize=8)
    ax.set_xticks(np.arange(len(keys)), keys)
    ax.set_xlabel("outcome (bit-string, qubit 0 on the right)")
    ax.set_ylabel(ylabel)
    if ylim:
        ax.set_ylim(ylim[0], max(ylim[1], top + 0.22) if crowded and len(keys) <= 8 else ylim[1])
    ax.set_title(title, fontweight="bold")
    if len(dists) > 1:
        ax.legend()
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return _finish(fig, show)


def plot_bloch(vector: Sequence[float], title: str = "", *, show: bool = True):
    """Bloch-sphere picture of a single-qubit state given by its Bloch vector (<X>, <Y>, <Z>)."""
    from qiskit.visualization import plot_bloch_vector

    fig = plot_bloch_vector(list(vector), title=title, figsize=(3.6, 3.6))
    return _finish(fig, show)


def plot_lines(series: Mapping[str, tuple[Sequence[float], Sequence[float]]], title: str = "", xlabel: str = "",
               ylabel: str = "", *, show: bool = True, figsize=(7, 3.6), markers: bool = True):
    """Simple line chart; ``series`` maps a label to ``(x_values, y_values)``."""
    fig, ax = plt.subplots(figsize=figsize)
    for i, (label, (x, y)) in enumerate(series.items()):
        ax.plot(x, y, marker="o" if markers else None, ms=4, lw=2, label=label, color=PALETTE[i % len(PALETTE)])
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if len(series) > 1:
        ax.legend()
    fig.tight_layout()
    return _finish(fig, show)


def plot_bars(values: Mapping[str, float], title: str = "", ylabel: str = "", *, show: bool = True, figsize=(5.5, 3.4),
              colors: Sequence[str] | None = None):
    """Single bar chart with value labels."""
    fig, ax = plt.subplots(figsize=figsize)
    labels = list(values)
    bars = ax.bar(labels, [values[k] for k in labels], color=colors or PALETTE[: len(labels)], edgecolor="white")
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{b.get_height():.3g}", ha="center", va="bottom", fontsize=9)
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return _finish(fig, show)
