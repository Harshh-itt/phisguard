
import numpy as np
import pytest

from src.features.extract import extract_features
from src.features.schema import FEATURE_NAMES
from src.preprocessing.pipeline import build_feature_matrix

import json

import pytest
from sklearn.preprocessing import StandardScaler

from src.preprocessing.pipeline import (
    load_ann_scaler,
    save_ann_scaler,
)


def test_feature_matrix_shape():
    urls = [
        "https://example.com",
        "http://test.org/login",
        "https://192.168.1.1/home",
    ]

    feature_rows = [extract_features(url) for url in urls]

    matrix = build_feature_matrix(feature_rows)

    assert matrix.shape == (3, 9)


def test_feature_matrix_uses_canonical_order():
    features = extract_features("https://example.com/login")

    matrix = build_feature_matrix([features])

    expected = np.array(
        [[features[name] for name in FEATURE_NAMES]],
        dtype=np.float64,
    )

    np.testing.assert_array_equal(matrix, expected)


def test_empty_feature_rows_are_rejected():
    with pytest.raises(ValueError, match="cannot be empty"):
        build_feature_matrix([])


def test_invalid_feature_row_is_rejected():
    features = extract_features("https://example.com")
    features.pop("url_length")

    with pytest.raises(ValueError, match="Missing features"):
        build_feature_matrix([features])

from sklearn.preprocessing import StandardScaler

from src.preprocessing.pipeline import create_ann_scaler


def test_create_ann_scaler_returns_unfitted_scaler():
    scaler = create_ann_scaler()

    assert isinstance(scaler, StandardScaler)
    assert not hasattr(scaler, "mean_")


def test_ann_scaler_standardizes_features():
    scaler = create_ann_scaler()

    training_data = np.array([
        [100, 2],
        [200, 4],
        [300, 6],
    ], dtype=np.float64)

    scaled = scaler.fit_transform(training_data)

    assert scaled.shape == training_data.shape
    np.testing.assert_allclose(scaled.mean(axis=0), [0, 0], atol=1e-10)
    np.testing.assert_allclose(scaled.std(axis=0), [1, 1], atol=1e-10)

from src.features.schema import FEATURE_SCHEMA_VERSION
from src.preprocessing.pipeline import validate_schema_compatibility


def test_matching_schema_is_accepted():
    validate_schema_compatibility(
        FEATURE_SCHEMA_VERSION,
        FEATURE_NAMES,
    )


def test_schema_version_mismatch_is_rejected():
    with pytest.raises(ValueError, match="version mismatch"):
        validate_schema_compatibility(
            "2.0.0",
            FEATURE_NAMES,
        )


def test_feature_order_mismatch_is_rejected():
    incorrect_names = tuple(reversed(FEATURE_NAMES))

    with pytest.raises(ValueError, match="ordering"):
        validate_schema_compatibility(
            FEATURE_SCHEMA_VERSION,
            incorrect_names,
        )    

def test_save_and_load_ann_scaler(tmp_path):
    scaler = StandardScaler()
    scaler.fit([
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [2, 3, 4, 5, 6, 7, 8, 9, 10],
        [3, 4, 5, 6, 7, 8, 9, 10, 11],
    ])

    save_ann_scaler(scaler, tmp_path)
    loaded_scaler = load_ann_scaler(tmp_path)

    assert isinstance(loaded_scaler, StandardScaler)
    assert loaded_scaler.n_features_in_ == 9
    assert loaded_scaler.mean_.tolist() == scaler.mean_.tolist()


def test_save_rejects_unfitted_scaler(tmp_path):
    scaler = StandardScaler()

    with pytest.raises(ValueError, match="fitted"):
        save_ann_scaler(scaler, tmp_path)


def test_load_rejects_missing_artifacts(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_ann_scaler(tmp_path)


def test_load_rejects_incompatible_schema(tmp_path):
    scaler = StandardScaler()
    scaler.fit([
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [2, 3, 4, 5, 6, 7, 8, 9, 10],
    ])

    save_ann_scaler(scaler, tmp_path)

    metadata_path = tmp_path / "ann_scaler_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    metadata["feature_schema_version"] = "999.0.0"

    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="version mismatch"):
        load_ann_scaler(tmp_path)