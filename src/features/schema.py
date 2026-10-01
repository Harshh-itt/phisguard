
FEATURE_SCHEMA_VERSION = "1.0.0"

FEATURE_NAMES = (
    "url_length",
    "hostname_length",
    "is_https",
    "is_ip_address",
    "digit_count",
    "dot_count",
    "hyphen_count",
    "path_length",
    "query_length",
)


def validate_features(features: dict) -> None:
    """Validate extracted features against the schema."""

    if not isinstance(features, dict):
        raise TypeError("Features must be provided as a dictionary.")

    expected = set(FEATURE_NAMES)
    received = set(features)

    missing = expected - received
    extra = received - expected

    if missing:
        raise ValueError(f"Missing features: {sorted(missing)}")

    if extra:
        raise ValueError(f"Unexpected features: {sorted(extra)}")

    for name in FEATURE_NAMES:
        value = features[name]

        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"Feature '{name}' must be an integer.")

        if value < 0:
            raise ValueError(f"Feature '{name}' cannot be negative.")

    for name in ("is_https", "is_ip_address"):
        if features[name] not in (0, 1):
            raise ValueError(f"Feature '{name}' must be 0 or 1.")


def features_to_vector(features: dict) -> list[int]:
    """Convert validated features into the canonical model input order."""

    validate_features(features)

    return [features[name] for name in FEATURE_NAMES]
