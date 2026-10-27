"""Unit tests for classification evaluation metrics."""

import pytest

from src.evaluation.metrics import (
    ClassificationMetrics,
    compute_classification_metrics,
    format_classification_report,
)


def test_perfect_predictions() -> None:
    """Verify metrics for 100% correct predictions."""
    y_true = [0, 1, 0, 1, 1, 0]
    y_pred = [0, 1, 0, 1, 1, 0]

    metrics = compute_classification_metrics(y_true, y_pred)

    assert isinstance(metrics, ClassificationMetrics)
    assert metrics.accuracy == 1.0
    assert metrics.precision_macro == 1.0
    assert metrics.recall_macro == 1.0
    assert metrics.f1_macro == 1.0
    assert metrics.confusion_matrix == [[3, 0], [0, 3]]
    assert metrics.per_class["phishing"].precision == 1.0
    assert metrics.per_class["phishing"].recall == 1.0
    assert metrics.per_class["legitimate"].precision == 1.0
    assert metrics.per_class["legitimate"].recall == 1.0
    assert metrics.total_samples == 6


def test_imperfect_predictions() -> None:
    """Verify metrics with mixed true/false positives and negatives."""
    # Class 0: 2 instances (1 correct, 1 misclassified as 1)
    # Class 1: 2 instances (1 correct, 1 misclassified as 0)
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 0, 1]

    metrics = compute_classification_metrics(y_true, y_pred)

    assert metrics.accuracy == 0.5
    assert metrics.precision_macro == 0.5
    assert metrics.recall_macro == 0.5
    assert metrics.f1_macro == 0.5
    assert metrics.confusion_matrix == [[1, 1], [1, 1]]
    assert metrics.total_samples == 4


def test_input_validation_empty_inputs() -> None:
    """Verify ValueError is raised on empty input arrays."""
    with pytest.raises(ValueError, match="cannot be empty"):
        compute_classification_metrics([], [])


def test_input_validation_length_mismatch() -> None:
    """Verify ValueError is raised when lengths do not match."""
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_classification_metrics([0, 1], [0])


def test_input_validation_unexpected_labels() -> None:
    """Verify ValueError is raised when labels outside configured set appear."""
    with pytest.raises(ValueError, match="unexpected labels"):
        compute_classification_metrics([0, 2], [0, 1])

    with pytest.raises(ValueError, match="unexpected labels"):
        compute_classification_metrics([0, 1], [0, 3])


def test_format_classification_report() -> None:
    """Verify text report generation formatting."""
    y_true = [0, 1, 0, 1]
    y_pred = [0, 1, 0, 1]

    metrics = compute_classification_metrics(y_true, y_pred)
    report = format_classification_report(metrics)

    assert "Classification Report:" in report
    assert "Accuracy:      1.0000" in report
    assert "Phishing" in report
    assert "Legitimate" in report
    assert "Confusion Matrix" in report
