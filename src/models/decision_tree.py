"""Decision Tree baseline model implementation, cross-validation, and persistence.

Implements the Phase 6 baseline classifier using scikit-learn's
DecisionTreeClassifier, trained strictly on approved static URL features.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from pydantic import BaseModel, Field
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.tree import DecisionTreeClassifier

from src.config import (
    METADATA_DIR,
    MODELS_DIR,
    RANDOM_SEED,
    TARGET_COLUMN,
)
from src.evaluation.metrics import (
    ClassificationMetrics,
    compute_classification_metrics,
)
from src.features.extract import extract_features
from src.features.schema import FEATURE_NAMES, FEATURE_SCHEMA_VERSION
from src.preprocessing.pipeline import build_feature_matrix

MODEL_FAMILY: str = "decision_tree"
MODEL_VARIANT: str = "baseline"


class DecisionTreeMetadata(BaseModel):
    """Metadata persisted alongside the trained Decision Tree model artifact."""

    model_family: str = Field(default=MODEL_FAMILY)
    model_variant: str = Field(default=MODEL_VARIANT)
    feature_schema_version: str = Field(default=FEATURE_SCHEMA_VERSION)
    feature_names: list[str] = Field(default_factory=lambda: list(FEATURE_NAMES))
    n_features: int = Field(default=len(FEATURE_NAMES))
    random_seed: int = Field(default=RANDOM_SEED)
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    tree_depth: int = Field(description="Max depth of the fitted tree")
    node_count: int = Field(description="Total node count of the fitted tree")
    feature_importances: dict[str, float] = Field(
        default_factory=dict, description="Gini feature importances"
    )
    train_metrics: ClassificationMetrics = Field(
        description="Fit metrics evaluated on full training set"
    )
    cv_metrics: ClassificationMetrics = Field(
        description="Out-of-fold domain-grouped cross-validation metrics"
    )
    train_samples_count: int = Field(description="Total training records used")
    train_domains_count: int = Field(description="Total distinct domains in training set")
    timestamp_utc: str = Field(description="ISO-8601 UTC creation timestamp")


def prepare_features_and_targets(
    records: list[dict[str, Any]],
    url_column: str = "URL",
    domain_column: str = "Domain",
    label_column: str = TARGET_COLUMN,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract approved static URL features, domains, and targets from raw records.

    Parameters
    ----------
    records : list[dict[str, Any]]
        Input records containing URL, Domain, and target label.
    url_column : str
        Column name holding the URL string.
    domain_column : str
        Column name holding the domain identifier for grouping.
    label_column : str
        Column name holding the target label.

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        X: (N, 9) feature matrix in canonical schema order.
        y: (N,) target binary labels.
        groups: (N,) domain names for group-aware partitioning.
    """
    if not records:
        raise ValueError("Input records cannot be empty.")

    feature_rows: list[dict[str, int]] = []
    labels: list[int] = []
    groups: list[str] = []

    for idx, rec in enumerate(records):
        if url_column not in rec or label_column not in rec or domain_column not in rec:
            raise ValueError(
                f"Record {idx} missing required column '{url_column}', "
                f"'{domain_column}', or '{label_column}'."
            )
        url = str(rec[url_column])
        domain = str(rec[domain_column]).strip().lower()
        if not domain:
            raise ValueError(f"Record {idx} contains empty domain.")
        lbl_str = str(rec[label_column]).strip()
        if lbl_str not in {"0", "1"}:
            raise ValueError(f"Record {idx} has invalid target label: '{lbl_str}'.")

        feats = extract_features(url)
        feature_rows.append(feats)
        labels.append(int(lbl_str))
        groups.append(domain)

    X = build_feature_matrix(feature_rows)
    y = np.asarray(labels, dtype=np.int64)
    domain_arr = np.asarray(groups)

    return X, y, domain_arr


def train_baseline_decision_tree(
    X: np.ndarray,
    y: np.ndarray,
    random_seed: int = RANDOM_SEED,
) -> DecisionTreeClassifier:
    """Fit an unpruned baseline DecisionTreeClassifier on tabular features."""
    if X.ndim != 2 or X.shape[1] != len(FEATURE_NAMES):
        raise ValueError(
            f"Feature matrix must have shape (N, {len(FEATURE_NAMES)}), got {X.shape}."
        )
    if len(X) != len(y):
        raise ValueError(f"Length mismatch between X ({len(X)}) and y ({len(y)}).")
    if len(np.unique(y)) < 2:
        raise ValueError("Target y must contain at least two classes.")

    clf = DecisionTreeClassifier(random_state=random_seed)
    clf.fit(X, y)
    return clf


def cross_validate_decision_tree(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    n_splits: int = 5,
    random_seed: int = RANDOM_SEED,
) -> ClassificationMetrics:
    """Perform domain-grouped cross-validation on the training set."""
    if len(X) != len(y) or len(X) != len(groups):
        raise ValueError("Lengths of X, y, and groups must match.")

    unique_groups = set(groups)
    if len(unique_groups) < n_splits:
        raise ValueError(f"Unique groups ({len(unique_groups)}) must be >= n_splits ({n_splits}).")

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    oof_predictions = np.zeros(len(y), dtype=np.int64)

    for train_idx, val_idx in sgkf.split(X, y, groups):
        clf = DecisionTreeClassifier(random_state=random_seed)
        clf.fit(X[train_idx], y[train_idx])
        oof_predictions[val_idx] = clf.predict(X[val_idx])

    return compute_classification_metrics(y, oof_predictions)


def extract_feature_importances(model: DecisionTreeClassifier) -> dict[str, float]:
    """Map fitted decision tree Gini importances to canonical feature names."""
    if not hasattr(model, "feature_importances_"):
        raise ValueError("Model is not fitted.")
    importances = model.feature_importances_
    return {
        name: round(float(imp), 4)
        for name, imp in zip(FEATURE_NAMES, importances, strict=True)
    }


def save_decision_tree_artifacts(
    model: DecisionTreeClassifier,
    metadata: DecisionTreeMetadata,
    models_dir: Path | str | None = None,
    metadata_dir: Path | str | None = None,
) -> tuple[Path, Path]:
    """Atomically persist fitted model and associated metadata."""
    m_dir = Path(models_dir) if models_dir else MODELS_DIR
    meta_dir = Path(metadata_dir) if metadata_dir else METADATA_DIR

    m_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    model_path = m_dir / "decision_tree_baseline.joblib"
    metadata_path = meta_dir / "decision_tree_baseline_metadata.json"

    # Save model binary
    joblib.dump(model, model_path)

    # Save metadata JSON
    metadata_path.write_text(
        json.dumps(metadata.model_dump(), indent=2),
        encoding="utf-8",
    )
    return model_path, metadata_path


def load_decision_tree_artifacts(
    models_dir: Path | str | None = None,
    metadata_dir: Path | str | None = None,
) -> tuple[DecisionTreeClassifier, DecisionTreeMetadata]:
    """Load model binary and validate against persisted metadata schema."""
    m_dir = Path(models_dir) if models_dir else MODELS_DIR
    meta_dir = Path(metadata_dir) if metadata_dir else METADATA_DIR

    model_path = m_dir / "decision_tree_baseline.joblib"
    metadata_path = meta_dir / "decision_tree_baseline_metadata.json"

    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"Artifact files missing: {model_path} or {metadata_path}"
        )

    meta_raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    meta = DecisionTreeMetadata(**meta_raw)

    if meta.feature_schema_version != FEATURE_SCHEMA_VERSION:
        raise ValueError(
            f"Feature schema mismatch: expected {FEATURE_SCHEMA_VERSION}, "
            f"got {meta.feature_schema_version}."
        )

    model = joblib.load(model_path)
    if not isinstance(model, DecisionTreeClassifier):
        raise TypeError(f"Loaded artifact is not a DecisionTreeClassifier: {type(model)}.")

    return model, meta


def run_decision_tree_training_pipeline(
    records: list[dict[str, Any]],
    random_seed: int = RANDOM_SEED,
    n_cv_splits: int = 5,
    save_artifacts: bool = False,
    models_dir: Path | str | None = None,
    metadata_dir: Path | str | None = None,
) -> tuple[DecisionTreeClassifier, DecisionTreeMetadata]:
    """Execute end-to-end Decision Tree baseline training, CV, and metadata generation."""
    X, y, groups = prepare_features_and_targets(records)

    # Cross-validation for unbiased performance estimate on training distribution
    cv_metrics = cross_validate_decision_tree(
        X, y, groups, n_splits=n_cv_splits, random_seed=random_seed
    )

    # Fit final model on full training set
    model = train_baseline_decision_tree(X, y, random_seed=random_seed)

    # Evaluate full training set fit (to measure overfit/tree complexity)
    train_preds = model.predict(X)
    train_metrics = compute_classification_metrics(y, train_preds)

    importances = extract_feature_importances(model)

    metadata = DecisionTreeMetadata(
        random_seed=random_seed,
        hyperparameters=model.get_params(),
        tree_depth=int(model.get_depth()),
        node_count=int(model.tree_.node_count),
        feature_importances=importances,
        train_metrics=train_metrics,
        cv_metrics=cv_metrics,
        train_samples_count=len(y),
        train_domains_count=len(set(groups)),
        timestamp_utc=datetime.now(UTC).isoformat(),
    )

    if save_artifacts:
        save_decision_tree_artifacts(
            model, metadata, models_dir=models_dir, metadata_dir=metadata_dir
        )

    return model, metadata
