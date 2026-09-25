"""Unit tests for Phase 0 foundation, environment, and architectural constraints."""

import importlib

import src
from src.config import (
    ALLOW_CREDENTIAL_COLLECTION,
    ALLOW_URL_FETCH,
    ARTIFACTS_DIR,
    DATA_DIR,
    HEADLINE_MODELS,
    INTERIM_DATA_DIR,
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
