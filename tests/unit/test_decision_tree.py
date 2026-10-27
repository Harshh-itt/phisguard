"""Unit tests for Phase 6 Decision Tree baseline model."""

from pathlib import Path
from typing import Any

import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

from src.features.schema import FEATURE_NAMES, FEATURE_SCHEMA_VERSION
from src.models.decision_tree import (
    DecisionTreeMetadata,
    cross_validate_decision_tree,
    extract_feature_importances,
    load_decision_tree_artifacts,
    prepare_features_and_targets,
    run_decision_tree_training_pipeline,
    train_baseline_decision_tree,
)


@pytest.fixture
def mock_training_records() -> list[dict[str, Any]]:
    """Generate mock training records with valid URLs, domains, and binary labels."""
    records: list[dict[str, Any]] = []
    # 10 distinct domains, 2 records each = 20 rows
    for i in range(5):
        records.append({
            "URL": f"https://legit-site-{i}.com/home",
            "Domain": f"legit-site-{i}.com",
            "label": "1",
        })
        records.append({
            "URL": f"https://legit-site-{i}.com/about",
            "Domain": f"legit-site-{i}.com",
            "label": "1",
        })
    for i in range(5):
        records.append({
            "URL": f"http://phish-login-{i}.org/signin?token=123",
            "Domain": f"phish-login-{i}.org",
            "label": "0",
        })
        records.append({
            "URL": f"http://phish-login-{i}.org/verify",
            "Domain": f"phish-login-{i}.org",
            "label": "0",
        })
    return records


def test_prepare_features_and_targets(mock_training_records: list[dict[str, Any]]) -> None:
    """Verify feature extraction and canonical array shapes."""
    X, y, groups = prepare_features_and_targets(mock_training_records)

    assert X.shape == (20, len(FEATURE_NAMES))
    assert y.shape == (20,)
    assert groups.shape == (20,)
    assert set(y) == {0, 1}
    assert len(set(groups)) == 10


def test_prepare_features_and_targets_validations() -> None:
    """Verify input validation on malformed records."""
    with pytest.raises(ValueError, match="cannot be empty"):
        prepare_features_and_targets([])

    with pytest.raises(ValueError, match="missing required column"):
        prepare_features_and_targets([{"URL": "https://a.com", "Domain": "a.com"}])

    with pytest.raises(ValueError, match="empty domain"):
        prepare_features_and_targets([{"URL": "https://a.com", "Domain": " ", "label": "1"}])

    with pytest.raises(ValueError, match="invalid target label"):
        prepare_features_and_targets([{"URL": "https://a.com", "Domain": "a.com", "label": "2"}])


def test_train_baseline_decision_tree() -> None:
    """Verify fitting of baseline Decision Tree classifier."""
    X = np.array([
        [20, 10, 1, 0, 0, 1, 0, 5, 0],
        [22, 11, 1, 0, 0, 1, 0, 6, 0],
        [60, 25, 0, 1, 8, 3, 2, 20, 15],
        [65, 26, 0, 1, 9, 3, 2, 22, 18],
    ])
    y = np.array([1, 1, 0, 0])

    model = train_baseline_decision_tree(X, y, random_seed=42)

    assert isinstance(model, DecisionTreeClassifier)
    assert model.n_features_in_ == len(FEATURE_NAMES)
    preds = model.predict(X)
    assert np.array_equal(preds, y)


def test_cross_validate_decision_tree() -> None:
    """Verify domain-grouped cross-validation execution."""
    X = np.random.RandomState(42).randint(0, 100, size=(20, len(FEATURE_NAMES)))
    y = np.array([1] * 10 + [0] * 10)
    groups = np.array([f"dom{i // 2}.com" for i in range(20)])

    metrics = cross_validate_decision_tree(X, y, groups, n_splits=5, random_seed=42)

    assert 0.0 <= metrics.accuracy <= 1.0
    assert metrics.total_samples == 20
    assert "phishing" in metrics.per_class
    assert "legitimate" in metrics.per_class


def test_extract_feature_importances() -> None:
    """Verify feature importances are extracted with matching schema names."""
    X = np.random.RandomState(42).rand(20, len(FEATURE_NAMES))
    y = np.array([1] * 10 + [0] * 10)
    model = DecisionTreeClassifier(random_state=42).fit(X, y)

    importances = extract_feature_importances(model)

    assert len(importances) == len(FEATURE_NAMES)
    assert list(importances.keys()) == list(FEATURE_NAMES)
    assert round(sum(importances.values()), 2) == 1.0


def test_save_and_load_decision_tree_artifacts(tmp_path: Path) -> None:
    """Verify model persistence, metadata structure, and reloading."""
    X = np.random.RandomState(42).rand(20, len(FEATURE_NAMES))
    y = np.array([1] * 10 + [0] * 10)

    records = [
        {"URL": f"https://dom{i}.com/p", "Domain": f"dom{i}.com", "label": str(y[i])}
        for i in range(20)
    ]

    model, meta = run_decision_tree_training_pipeline(
        records,
        random_seed=42,
        n_cv_splits=5,
        save_artifacts=True,
        models_dir=tmp_path / "models",
        metadata_dir=tmp_path / "metadata",
    )

    assert isinstance(meta, DecisionTreeMetadata)
    assert meta.feature_schema_version == FEATURE_SCHEMA_VERSION
    assert meta.train_samples_count == 20
    assert meta.train_domains_count == 20

    loaded_model, loaded_meta = load_decision_tree_artifacts(
        models_dir=tmp_path / "models",
        metadata_dir=tmp_path / "metadata",
    )

    assert isinstance(loaded_model, DecisionTreeClassifier)
    assert loaded_meta.model_family == "decision_tree"
    assert loaded_meta.feature_names == list(FEATURE_NAMES)
    assert np.array_equal(loaded_model.predict(X), model.predict(X))
