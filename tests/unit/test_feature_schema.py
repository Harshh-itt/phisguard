
import pytest

from src.features.extract import extract_features
from src.features.schema import (
    FEATURE_NAMES,
    FEATURE_SCHEMA_VERSION,
    features_to_vector,
    validate_features,
)


def test_schema_version():
    assert FEATURE_SCHEMA_VERSION == "1.0.0"


def test_feature_count():
    assert len(FEATURE_NAMES) == 9


def test_vector_uses_canonical_order():
    features = extract_features("https://example.com/login")

    vector = features_to_vector(features)

    expected = [features[name] for name in FEATURE_NAMES]

    assert vector == expected
    assert len(vector) == 9


def test_missing_feature_is_rejected():
    features = extract_features("https://example.com")
    features.pop("url_length")

    with pytest.raises(ValueError, match="Missing features"):
        validate_features(features)


def test_unexpected_feature_is_rejected():
    features = extract_features("https://example.com")
    features["unknown_feature"] = 1

    with pytest.raises(ValueError, match="Unexpected features"):
        validate_features(features)


def test_negative_feature_is_rejected():
    features = extract_features("https://example.com")
    features["url_length"] = -1

    with pytest.raises(ValueError, match="cannot be negative"):
        validate_features(features)


def test_non_integer_feature_is_rejected():
    features = extract_features("https://example.com")
    features["url_length"] = 12.5

    with pytest.raises(TypeError, match="must be an integer"):
        validate_features(features)


def test_binary_feature_validation():
    features = extract_features("https://example.com")
    features["is_https"] = 2

    with pytest.raises(ValueError, match="must be 0 or 1"):
        validate_features(features)
