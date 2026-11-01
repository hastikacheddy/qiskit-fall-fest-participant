"""Provided code for Challenge 8 - Teach a Quantum Circuit (a variational quantum classifier).

The provided pieces are the synthetic dataset, two small classical baselines and plotting helpers. Nothing here scales features,
builds the quantum model, trains it or computes a metric: those are your TODOs.

Conventions (identical in the problem statement and in every test)
* Data: ``X`` has shape ``(n, 2)`` (raw features), labels ``y`` are ``-1`` or ``+1``.
* The model has 2 qubits; the output is the expectation value of Z on qubit 0.
"""
from __future__ import annotations

import math

import numpy as np

from .. import viz

NUM_QUBITS = 2
PARAMS_PER_LAYER = 4


# ------------------------------------------------------------------------------------------------------------------
# input checks (provided: they raise ValueError and return clean NumPy arrays)
# ------------------------------------------------------------------------------------------------------------------
def validate_num_layers(num_layers) -> int:
    """``num_layers`` must be an integer >= 1 (NumPy integers are fine, booleans are not). Returns it as ``int``."""
    if isinstance(num_layers, bool) or not isinstance(num_layers, (int, np.integer)) or num_layers < 1:
        raise ValueError(f"num_layers must be an integer >= 1, got {num_layers!r}")
    return int(num_layers)


def validate_features(X, n_features: int | None = None) -> np.ndarray:
    """A finite 2-D array of floats with at least one row (and exactly ``n_features`` columns if given)."""
    try:
        array = np.asarray(X, dtype=float)
    except (TypeError, ValueError):
        raise ValueError("features must be numbers") from None
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise ValueError(f"features must be a 2-D array with at least one row and one column, got shape {array.shape}")
    if n_features is not None and array.shape[1] != n_features:
        raise ValueError(f"expected {n_features} feature columns, got {array.shape[1]}")
    if not np.all(np.isfinite(array)):
        raise ValueError("features must be finite")
    return array


def validate_sample(x) -> np.ndarray:
    """One sample: a finite 1-D array with exactly 2 numbers."""
    try:
        array = np.asarray(x, dtype=float)
    except (TypeError, ValueError):
        raise ValueError("a sample must consist of numbers") from None
    if array.shape != (NUM_QUBITS,) or not np.all(np.isfinite(array)):
        raise ValueError(f"a sample must be a finite vector of length {NUM_QUBITS}, got shape {array.shape}")
    return array


def validate_labels(y, n: int | None = None) -> np.ndarray:
    """A 1-D array of labels that are all -1 or +1 (labels 0 / 1 are rejected), with length ``n`` if given."""
    try:
        array = np.asarray(y, dtype=float)
    except (TypeError, ValueError):
        raise ValueError("labels must be numbers") from None
    if array.ndim != 1 or array.size < 1:
        raise ValueError("labels must be a non-empty 1-D array")
    if n is not None and array.size != n:
        raise ValueError(f"expected {n} labels, got {array.size}")
    if not np.all((array == 1) | (array == -1)):
        raise ValueError("labels must be -1 or +1")
    return array.astype(int)


def validate_params(params, num_layers: int) -> np.ndarray:
    """A finite 1-D array with exactly ``4 * num_layers`` parameters."""
    layers = validate_num_layers(num_layers)
    try:
        array = np.asarray(params, dtype=float)
    except (TypeError, ValueError):
        raise ValueError("parameters must be numbers") from None
    if array.shape != (PARAMS_PER_LAYER * layers,) or not np.all(np.isfinite(array)):
        raise ValueError(f"expected {PARAMS_PER_LAYER * layers} finite parameters for {layers} layer(s), got shape {array.shape}")
    return array


def make_dataset(n_train: int = 60, n_test: int = 60, seed: int = 3, noise: float = 0.12):
    """Synthetic 'two moons' data in raw (unscaled) units: ``(X_train, y_train, X_test, y_test)``.

    Two interleaving half circles with Gaussian noise, labels +1 and -1, classes balanced (``n`` must be even). The training and
    the test points come from *independent* random streams derived from ``seed``, so no test point is a copy of a training
    point, and the same seed always gives the same data. The raw coordinates are deliberately not in [0, pi]: scaling is part of
    the task.
    """
    if n_train % 2 or n_test % 2 or n_train < 2 or n_test < 2:
        raise ValueError("n_train and n_test must be even and at least 2")

    def draw(n: int, stream: int):
        rng = np.random.default_rng([seed, stream])
        half = n // 2
        t = rng.uniform(0, math.pi, half)
        upper = np.column_stack([np.cos(t), np.sin(t)])
        lower = np.column_stack([1 - np.cos(t), 0.5 - np.sin(t)])
        points = np.vstack([upper, lower]) + rng.normal(0, noise, size=(2 * half, 2))
        labels = np.concatenate([np.ones(half), -np.ones(half)]).astype(int)
        order = rng.permutation(2 * half)
        raw = points[order] * np.array([4.0, 2.5]) + np.array([12.0, -3.0])  # "sensor units": not in [0, pi]
        return raw, labels[order]

    X_train, y_train = draw(n_train, 0)
    X_test, y_test = draw(n_test, 1)
    return X_train, y_train, X_test, y_test


# ------------------------------------------------------------------------------------------------------------------
# classical baselines (for the fair comparison in the notebook)
# ------------------------------------------------------------------------------------------------------------------
def _standardise(X_train: np.ndarray, X_test: np.ndarray):
    mean, std = X_train.mean(axis=0), X_train.std(axis=0)
    std = np.where(std == 0, 1.0, std)
    return (X_train - mean) / std, (X_test - mean) / std  # statistics of the TRAINING data only


def knn_baseline(X_train, y_train, X_test, k: int = 5) -> np.ndarray:
    """k-nearest-neighbour labels (+-1) for ``X_test`` (features standardised with the training statistics)."""
    train, test = _standardise(np.asarray(X_train, float), np.asarray(X_test, float))
    y = np.asarray(y_train)
    labels = []
    for point in test:
        nearest = np.argsort(np.linalg.norm(train - point, axis=1))[:k]
        labels.append(1 if y[nearest].sum() >= 0 else -1)
    return np.array(labels)


def logistic_baseline(X_train, y_train, X_test, steps: int = 800, rate: float = 0.5) -> np.ndarray:
    """Logistic regression (a linear decision boundary) by gradient descent; labels +-1 for ``X_test``."""
    train, test = _standardise(np.asarray(X_train, float), np.asarray(X_test, float))
    y01 = (np.asarray(y_train) > 0).astype(float)
    w, b = np.zeros(train.shape[1]), 0.0
    for _ in range(steps):
        p = 1 / (1 + np.exp(-(train @ w + b)))
        w -= rate * train.T @ (p - y01) / len(y01)
        b -= rate * float(np.mean(p - y01))
    return np.where(test @ w + b >= 0, 1, -1)


def wilson_interval(correct: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Approximate 95 % confidence interval of an accuracy ``correct / n`` (Wilson score) - small test sets are uncertain."""
    p = correct / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


# ------------------------------------------------------------------------------------------------------------------
# plots
# ------------------------------------------------------------------------------------------------------------------
def plot_dataset(X_train, y_train, X_test=None, y_test=None, title: str = "The data (raw units)", *, show: bool = True):
    """Scatter plot: training points as circles, test points as triangles; colour = label."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.2, 3.8))
    for label, colour in ((1, viz.PALETTE[1]), (-1, viz.PALETTE[0])):
        m = np.asarray(y_train) == label
        ax.scatter(np.asarray(X_train)[m, 0], np.asarray(X_train)[m, 1], c=colour, s=28, edgecolor="white", label=f"train, label {label:+d}")
        if X_test is not None:
            t = np.asarray(y_test) == label
            ax.scatter(np.asarray(X_test)[t, 0], np.asarray(X_test)[t, 1], c=colour, s=40, marker="^", edgecolor="k", linewidth=0.5,
                       label=f"test, label {label:+d}")
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")
    ax.set_title(title, fontweight="bold")
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_decision_regions(output_fn, feature_min, feature_max, X_train, y_train, X_test=None, y_test=None, resolution: int = 30,
                          title: str = "Decision regions of the trained circuit", *, show: bool = True):
    """Colour map of ``output_fn(x_scaled)`` (YOUR trained model, a function of ONE scaled sample) over the raw feature plane.

    ``feature_min`` / ``feature_max`` are the training statistics used for scaling; points are scaled with them (no refitting).
    """
    import matplotlib.pyplot as plt

    X_train = np.asarray(X_train, float)
    lo, hi = np.asarray(feature_min, float), np.asarray(feature_max, float)
    pad = 0.12 * (X_train.max(axis=0) - X_train.min(axis=0))
    gx = np.linspace(X_train[:, 0].min() - pad[0], X_train[:, 0].max() + pad[0], resolution)
    gy = np.linspace(X_train[:, 1].min() - pad[1], X_train[:, 1].max() + pad[1], resolution)
    scale = lambda p: (p - lo) / (hi - lo) * math.pi
    field = np.array([[output_fn(scale(np.array([a, b]))) for a in gx] for b in gy])
    fig, ax = plt.subplots(figsize=(5.6, 4.0))
    im = ax.contourf(gx, gy, field, levels=np.linspace(-1, 1, 21), cmap="RdBu_r", alpha=0.85)
    ax.contour(gx, gy, field, levels=[0.0], colors="k", linewidths=1.2)
    fig.colorbar(im, ax=ax).set_label("model output <Z0>")
    for label, colour in ((1, viz.PALETTE[1]), (-1, viz.PALETTE[0])):
        m = np.asarray(y_train) == label
        ax.scatter(X_train[m, 0], X_train[m, 1], c=colour, s=26, edgecolor="white")
        if X_test is not None:
            t = np.asarray(y_test) == label
            ax.scatter(np.asarray(X_test)[t, 0], np.asarray(X_test)[t, 1], c=colour, s=40, marker="^", edgecolor="k", linewidth=0.6)
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_loss_history(history, title: str = "Training loss (every evaluation of the objective)", *, show: bool = True):
    """Loss against the number of objective evaluations."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.plot(history, color=viz.PALETTE[0], lw=1.6)
    ax.set_xlabel("objective evaluation")
    ax.set_ylabel("mean squared error")
    ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    return viz._finish(fig, show)


def plot_accuracy_comparison(results: dict, n_test: int, title: str = "Held-out accuracy with 95 % confidence intervals", *, show: bool = True):
    """Bar chart of ``{name: accuracy}`` with Wilson intervals: with ~60 test points the bars overlap more than people expect."""
    import matplotlib.pyplot as plt

    names = list(results)
    acc = np.array([results[k] for k in names])
    intervals = np.array([wilson_interval(round(a * n_test), n_test) for a in acc])
    fig, ax = plt.subplots(figsize=(6, 3.4))
    ax.bar(names, acc, color=viz.PALETTE[: len(names)], edgecolor="white")
    below = np.clip(acc - intervals[:, 0], 0, None)   # the Wilson interval is not symmetric around the accuracy; at 100 % its
    above = np.clip(intervals[:, 1] - acc, 0, None)   # upper end can land a rounding error below it - Matplotlib rejects negative bars
    ax.errorbar(range(len(names)), acc, yerr=[below, above], fmt="none", ecolor="k", capsize=5)
    ax.axhline(0.5, color="0.4", ls="--", lw=1)
    ax.text(len(names) - 0.55, 0.51, "chance", fontsize=8, color="0.3", ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("test accuracy")
    ax.set_title(title, fontweight="bold")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return viz._finish(fig, show)
