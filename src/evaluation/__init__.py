"""Model evaluation, metrics computation, and comparative benchmarking.

Provides functions to compute accuracy, precision, recall, F1, ROC-AUC,
confusion matrices, false positive rates, inference latency, and generate
empirical comparison reports.
"""

from src.evaluation.metrics import (
    ClassificationMetrics,
    ClassMetrics,
    compute_classification_metrics,
    format_classification_report,
)

__all__ = [
    "ClassMetrics",
    "ClassificationMetrics",
    "compute_classification_metrics",
    "format_classification_report",
]
