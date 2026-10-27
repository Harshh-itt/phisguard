"""Classification evaluation metrics for PhishGuard.

Provides deterministic computation of accuracy, precision, recall, F1,
confusion matrix, and structured evaluation reports.
"""

from collections.abc import Sequence

import numpy as np
from pydantic import BaseModel, Field
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from src.config import LABEL_MAPPING


class ClassMetrics(BaseModel):
    """Metrics for an individual target class."""

    precision: float = Field(description="Precision for this class")
    recall: float = Field(description="Recall for this class")
    f1_score: float = Field(description="F1-score for this class")
    support: int = Field(description="Number of true instances for this class")


class ClassificationMetrics(BaseModel):
    """Comprehensive evaluation metrics for binary classification."""

    accuracy: float = Field(description="Overall accuracy score")
    precision_macro: float = Field(description="Macro-averaged precision")
    recall_macro: float = Field(description="Macro-averaged recall")
    f1_macro: float = Field(description="Macro-averaged F1 score")
    precision_weighted: float = Field(description="Weighted-averaged precision")
    recall_weighted: float = Field(description="Weighted-averaged recall")
    f1_weighted: float = Field(description="Weighted-averaged F1 score")
    confusion_matrix: list[list[int]] = Field(
        description="2x2 confusion matrix [[TN, FP], [FN, TP]]"
    )
    per_class: dict[str, ClassMetrics] = Field(
        description="Metrics breakdown keyed by class name"
    )
    total_samples: int = Field(description="Total evaluated samples")


def compute_classification_metrics(
    y_true: Sequence[int] | np.ndarray,
    y_pred: Sequence[int] | np.ndarray,
    labels: tuple[int, ...] = (0, 1),
    label_mapping: dict[int, str] | None = None,
) -> ClassificationMetrics:
    """Compute comprehensive classification metrics.

    Parameters
    ----------
    y_true : Sequence[int] or np.ndarray
        True target labels.
    y_pred : Sequence[int] or np.ndarray
        Predicted target labels.
    labels : tuple[int, ...], default=(0, 1)
        Target label classes to evaluate.
    label_mapping : dict[int, str], optional
        Mapping from integer class to human-readable name.
        Defaults to `LABEL_MAPPING` (0: 'phishing', 1: 'legitimate').

    Returns
    -------
    ClassificationMetrics
        Structured evaluation metrics container.
    """
    mapping = label_mapping or LABEL_MAPPING

    y_t = np.asarray(y_true, dtype=np.int64)
    y_p = np.asarray(y_pred, dtype=np.int64)

    if y_t.ndim != 1 or y_p.ndim != 1:
        raise ValueError("y_true and y_pred must be 1-dimensional arrays.")
    if len(y_t) == 0 or len(y_p) == 0:
        raise ValueError("Inputs cannot be empty.")
    if len(y_t) != len(y_p):
        raise ValueError(
            f"Length mismatch: y_true has {len(y_t)} samples, y_pred has {len(y_p)}."
        )

    valid_labels = set(labels)
    invalid_true = set(y_t) - valid_labels
    invalid_pred = set(y_p) - valid_labels
    if invalid_true:
        raise ValueError(f"y_true contains unexpected labels: {sorted(invalid_true)}")
    if invalid_pred:
        raise ValueError(f"y_pred contains unexpected labels: {sorted(invalid_pred)}")

    acc = float(accuracy_score(y_t, y_p))

    # Macro and weighted averages
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
        y_t, y_p, labels=list(labels), average="macro", zero_division=0
    )
    p_wt, r_wt, f1_wt, _ = precision_recall_fscore_support(
        y_t, y_p, labels=list(labels), average="weighted", zero_division=0
    )

    # Per-class metrics
    p_per, r_per, f1_per, s_per = precision_recall_fscore_support(
        y_t, y_p, labels=list(labels), average=None, zero_division=0
    )

    per_class_dict: dict[str, ClassMetrics] = {}
    for idx, lbl in enumerate(labels):
        name = mapping.get(lbl, str(lbl))
        per_class_dict[name] = ClassMetrics(
            precision=round(float(p_per[idx]), 4),
            recall=round(float(r_per[idx]), 4),
            f1_score=round(float(f1_per[idx]), 4),
            support=int(s_per[idx]),
        )

    cm = confusion_matrix(y_t, y_p, labels=list(labels)).tolist()

    return ClassificationMetrics(
        accuracy=round(acc, 4),
        precision_macro=round(float(p_macro), 4),
        recall_macro=round(float(r_macro), 4),
        f1_macro=round(float(f1_macro), 4),
        precision_weighted=round(float(p_wt), 4),
        recall_weighted=round(float(r_wt), 4),
        f1_weighted=round(float(f1_wt), 4),
        confusion_matrix=cm,
        per_class=per_class_dict,
        total_samples=len(y_t),
    )


def format_classification_report(metrics: ClassificationMetrics) -> str:
    """Format structured metrics into a human-readable summary text report."""
    lines = [
        "Classification Report:",
        f"  Total Samples: {metrics.total_samples}",
        f"  Accuracy:      {metrics.accuracy:.4f}",
        f"  Macro F1:      {metrics.f1_macro:.4f}",
        f"  Weighted F1:   {metrics.f1_weighted:.4f}",
        "",
        "Per-Class Breakdown:",
    ]
    for class_name, cm in metrics.per_class.items():
        lines.append(
            f"  {class_name.capitalize():<12} "
            f"Precision: {cm.precision:.4f}  "
            f"Recall: {cm.recall:.4f}  "
            f"F1: {cm.f1_score:.4f}  "
            f"Support: {cm.support}"
        )
    lines.append("")
    lines.append("Confusion Matrix (rows=true, cols=pred):")
    for row in metrics.confusion_matrix:
        lines.append(f"  {row}")
    return "\n".join(lines)
