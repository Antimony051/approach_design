"""Image-level metrics and operating-point selection."""

from collections.abc import Sequence

import numpy as np


def _precision_recall(
    scores: Sequence[float], truth: Sequence[bool]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.asarray(scores)
    labels = np.asarray(truth, dtype=bool)
    ranking = np.argsort(-values, kind="stable")
    descending = values[ranking]
    ranked_labels = labels[ranking]
    if len(descending) == 0:
        empty = np.array([], dtype=float)
        return empty, empty, empty
    last_tied = np.flatnonzero(np.r_[descending[:-1] != descending[1:], True])
    cumulative = np.cumsum(ranked_labels)[last_tied]
    precision = cumulative / (last_tied + 1)
    recall = cumulative / max(1, int(labels.sum()))
    return descending[last_tied], precision, recall


def average_precision(scores: Sequence[float], truth: Sequence[bool]) -> float | None:
    if not any(truth):
        return None
    _, precision, recall = _precision_recall(scores, truth)
    return float(np.sum(precision * np.diff(np.r_[0.0, recall])))


def best_threshold(scores: Sequence[float], truth: Sequence[bool]) -> tuple[float, float, float]:
    """Return decision threshold, F1 and precision from validation labels."""
    thresholds, precision, recall = _precision_recall(scores, truth)
    best = (0.0, 0.0, 1.0)
    for threshold, p, r in zip(thresholds, precision, recall, strict=True):
        if threshold > 0 and p + r > 0:
            best = max(best, (float(2 * p * r / (p + r)), float(p), float(threshold)))
    f1, p, threshold = best
    return threshold, f1, p


def image_metrics(
    scores: Sequence[float], truth: Sequence[bool], threshold: float
) -> dict[str, int | float | None]:
    actual = np.asarray(truth, dtype=bool)
    detected = np.asarray(scores) >= threshold
    tp = int(np.count_nonzero(detected & actual))
    fp = int(np.count_nonzero(detected & ~actual))
    fn = int(np.count_nonzero(~detected & actual))
    tn = len(truth) - tp - fp - fn
    return {
        "known_images": len(truth),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        "average_precision": average_precision(scores, truth),
        "threshold": threshold,
    }
