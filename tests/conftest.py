"""Global pytest fixtures and test configuration for PhishGuard."""

from pathlib import Path

import pytest

from src.config import ARTIFACTS_DIR, DATA_DIR, PROJECT_ROOT


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_dir() -> Path:
    """Return the absolute path to the data directory."""
    return DATA_DIR


@pytest.fixture(scope="session")
def artifacts_dir() -> Path:
    """Return the absolute path to the artifacts directory."""
    return ARTIFACTS_DIR


@pytest.fixture
def sample_test_urls() -> dict[str, str]:
    """Provide synthetic URL samples for testing without network calls."""
    return {
        "legitimate_sample": "https://www.example.com/safe/path",
        "phishing_sample": "http://192.168.1.1/secure-login/verification.html",
    }
