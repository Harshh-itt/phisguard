"""Unit tests for Phase 0 foundation, environment, and architectural constraints."""

import importlib

import src
from src.config import (
    ALLOW_CREDENTIAL_COLLECTION,
    ALLOW_URL_FETCH,
    ARTIFACTS_DIR,
    DATA_DIR,
    DISQUALIFIED_RAW_COLUMNS,
    EXCLUDED_METADATA_COLUMNS,
    EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS,
    EXCLUDED_WEBPAGE_COLUMNS,
    EXPECTED_DUPLICATE_URL_COUNT,
    EXPECTED_INTERIM_CLASS_COUNTS,
    EXPECTED_INTERIM_LEGITIMATE_COUNT,
    EXPECTED_INTERIM_PHISHING_COUNT,
    EXPECTED_INTERIM_ROW_COUNT,
    EXPECTED_RAW_ROW_COUNT,
    HEADLINE_MODELS,
    INTERIM_DATA_DIR,
    INTERIM_DATASET_FILE,
    LABEL_MAPPING,
    METADATA_DIR,
    MODELS_DIR,
    PREPROCESSORS_DIR,
    PROCESSED_DATA_DIR,
    PROJECT_ROOT,
    RAW_DATA_DIR,
    REPORTS_DIR,
    STATIC_ANALYSIS_ONLY,
    TARGET_COLUMN,
    settings,
)


def test_package_version() -> None:
    """Verify package version is defined and follows semantic versioning."""
    assert hasattr(src, "__version__")
    assert src.__version__ == "0.1.0"


def test_package_imports() -> None:
    """Verify that all core src and backend subpackages can be imported cleanly."""
    packages = [
        "src.data",
        "src.features",
        "src.preprocessing",
        "src.models",
        "src.evaluation",
        "src.inference",
        "backend",
        "backend.routes",
        "backend.services",
    ]
    for pkg in packages:
        module = importlib.import_module(pkg)
        assert module is not None, f"Failed to import {pkg}"


def test_directory_structure_existence() -> None:
    """Verify all required project directories exist on the filesystem."""
    required_directories = [
        PROJECT_ROOT,
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        ARTIFACTS_DIR,
        MODELS_DIR,
        PREPROCESSORS_DIR,
        METADATA_DIR,
        REPORTS_DIR,
        PROJECT_ROOT / "notebooks",
        PROJECT_ROOT / "docs",
        PROJECT_ROOT / "frontend",
        PROJECT_ROOT / ".github" / "workflows",
    ]
    for directory in required_directories:
        assert directory.exists(), f"Missing directory: {directory}"
        assert directory.is_dir(), f"Path is not a directory: {directory}"


def test_safety_and_architectural_invariants() -> None:
    """Verify permanent architectural and security constraints."""
    # Static URL analysis invariant
    assert STATIC_ANALYSIS_ONLY is True
    assert ALLOW_URL_FETCH is False
    assert ALLOW_CREDENTIAL_COLLECTION is False

    # Headline ML model constraint: exactly two models
    assert len(HEADLINE_MODELS) == 2
    assert "decision_tree" in HEADLINE_MODELS
    assert "ann" in HEADLINE_MODELS
    assert HEADLINE_MODELS == ("decision_tree", "ann")

    # Target label mapping invariant
    assert TARGET_COLUMN == "label"
    assert LABEL_MAPPING[0] == "phishing"
    assert LABEL_MAPPING[1] == "legitimate"


def test_settings_initialization() -> None:
    """Verify default runtime settings are valid."""
    assert settings.environment == "development"
    assert settings.default_model in HEADLINE_MODELS
    assert settings.random_seed == 42
    assert isinstance(settings.allowed_origins, list)


def test_interim_dataset_path() -> None:
    """Verify Phase 3 interim dataset path resolution."""
    assert INTERIM_DATASET_FILE.parent == INTERIM_DATA_DIR
    assert INTERIM_DATASET_FILE.name == "cleaned_phiusiil.csv"
    assert INTERIM_DATA_DIR.exists()


def test_phase3_interim_invariants() -> None:
    """Verify Phase 3 data quality and post-deduplication dimension invariants."""
    assert EXPECTED_RAW_ROW_COUNT == 235795
    assert EXPECTED_DUPLICATE_URL_COUNT == 425
    assert EXPECTED_INTERIM_ROW_COUNT == EXPECTED_RAW_ROW_COUNT - EXPECTED_DUPLICATE_URL_COUNT
    assert EXPECTED_INTERIM_ROW_COUNT == 235370

    # Class distribution invariants
    assert EXPECTED_INTERIM_LEGITIMATE_COUNT == 134850
    assert EXPECTED_INTERIM_PHISHING_COUNT == 100520
    assert (
        EXPECTED_INTERIM_LEGITIMATE_COUNT + EXPECTED_INTERIM_PHISHING_COUNT
        == EXPECTED_INTERIM_ROW_COUNT
    )
    assert EXPECTED_INTERIM_CLASS_COUNTS == {
        "1": EXPECTED_INTERIM_LEGITIMATE_COUNT,
        "0": EXPECTED_INTERIM_PHISHING_COUNT,
    }


def test_raw_column_exclusion_constants() -> None:
    """Verify Phase 2 audit provenance exclusion constants."""
    assert len(EXCLUDED_METADATA_COLUMNS) == 1
    assert "FILENAME" in EXCLUDED_METADATA_COLUMNS

    assert len(EXCLUDED_WEBPAGE_COLUMNS) == 29
    assert "LineOfCode" in EXCLUDED_WEBPAGE_COLUMNS
    assert "HasTitle" in EXCLUDED_WEBPAGE_COLUMNS
    assert "NoOfImage" in EXCLUDED_WEBPAGE_COLUMNS

    assert len(EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS) == 3
    assert "URLSimilarityIndex" in EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS
    assert "TLDLegitimateProb" in EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS
    assert "URLCharProb" in EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS

    # All 33 disqualified columns combined (1 metadata + 29 webpage/DOM + 3 heuristics)
    assert len(DISQUALIFIED_RAW_COLUMNS) == 33
    assert len(set(DISQUALIFIED_RAW_COLUMNS)) == 33  # Check uniqueness
