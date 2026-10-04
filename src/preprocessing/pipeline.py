import numpy as np
from sklearn.preprocessing import StandardScaler
import json
from pathlib import Path

import joblib

from src.features.schema import (
    FEATURE_NAMES,
    FEATURE_SCHEMA_VERSION,
    features_to_vector,
)

def build_feature_matrix(feature_rows: list[dict]) -> np.ndarray:
    """Convert extracted feature dictionaries into a canonical matrix."""

    if not feature_rows:
        raise ValueError("Feature rows cannot be empty.")

    vectors = [
        features_to_vector(features)
        for features in feature_rows
    ]

    matrix = np.asarray(vectors, dtype=np.float64)

    if matrix.ndim != 2 or matrix.shape[1] != len(FEATURE_NAMES):
        raise ValueError("Feature matrix does not match the canonical schema.")

    return matrix

def create_ann_scaler() -> StandardScaler:
    """Create a fresh scaler for ANN numerical features."""

    return StandardScaler()    

def validate_schema_compatibility(
    saved_version: str,
    saved_feature_names: tuple[str, ...],
) -> None:
    """Validate a saved preprocessor against the current feature schema."""

    if saved_version != FEATURE_SCHEMA_VERSION:
        raise ValueError(
            f"Feature schema version mismatch: "
            f"expected {FEATURE_SCHEMA_VERSION}, received {saved_version}."
        )

    if saved_feature_names != FEATURE_NAMES:
        raise ValueError(
            "Saved feature names or ordering do not match the current schema."
        )    

def save_ann_scaler(
    scaler: StandardScaler,
    artifact_dir: str | Path,
) -> None:
    """Save a fitted ANN scaler and its feature-schema metadata."""

    if not hasattr(scaler, "mean_") or not hasattr(scaler, "scale_"):
        raise ValueError("Scaler must be fitted before saving.")

    if scaler.n_features_in_ != len(FEATURE_NAMES):
        raise ValueError("Scaler feature count does not match the current schema.")

    artifact_path = Path(artifact_dir)
    artifact_path.mkdir(parents=True, exist_ok=True)

    scaler_path = artifact_path / "ann_scaler.joblib"
    metadata_path = artifact_path / "ann_scaler_metadata.json"

    metadata = {
        "preprocessor_type": "StandardScaler",
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "feature_names": list(FEATURE_NAMES),
        "n_features": len(FEATURE_NAMES),
    }

    joblib.dump(scaler, scaler_path)

    metadata_path.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8",
    )

def load_ann_scaler(
    artifact_dir: str | Path,
) -> StandardScaler:
    """Load an ANN scaler after validating its schema metadata."""

    artifact_path = Path(artifact_dir)
    scaler_path = artifact_path / "ann_scaler.joblib"
    metadata_path = artifact_path / "ann_scaler_metadata.json"

    if not scaler_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Scaler artifact or metadata file is missing.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    if metadata.get("preprocessor_type") != "StandardScaler":
        raise ValueError("Unsupported preprocessor type.")

    saved_version = metadata.get("feature_schema_version")
    saved_names = metadata.get("feature_names")

    if not isinstance(saved_version, str):
        raise ValueError("Invalid feature schema version in metadata.")

    if not isinstance(saved_names, list) or not all(
        isinstance(name, str) for name in saved_names
    ):
        raise ValueError("Invalid feature names in metadata.")

    validate_schema_compatibility(
        saved_version,
        tuple(saved_names),
    )

    if metadata.get("n_features") != len(FEATURE_NAMES):
        raise ValueError("Metadata feature count does not match the current schema.")

    scaler = joblib.load(scaler_path)

    if not isinstance(scaler, StandardScaler):
        raise ValueError("Saved artifact is not a StandardScaler.")

    if not hasattr(scaler, "mean_") or not hasattr(scaler, "scale_"):
        raise ValueError("Saved scaler is not fitted.")

    if scaler.n_features_in_ != len(FEATURE_NAMES):
        raise ValueError("Saved scaler feature count is incompatible.")

    return scaler    
