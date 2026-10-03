"""Central configuration and paths for PhishGuard.

Defines project directory paths, global random seeds, model constants,
and safety invariants.
"""

from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, Field

# Base Directory Resolution
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

# Data Directories
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
INTERIM_DATA_DIR: Final[Path] = DATA_DIR / "interim"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
RAW_DATASET_FILE: Final[Path] = RAW_DATA_DIR / "PhiUSIIL_Phishing_URL_Dataset.csv"
RAW_DATASET_SHA256: Final[str] = (
    "a236549cd369cd80bd478ff8e1779cbf44c58d5c3f79f7a51a1adbed7d06d1c6"
)
INTERIM_DATASET_FILE: Final[Path] = INTERIM_DATA_DIR / "cleaned_phiusiil.csv"

# Artifact Directories
ARTIFACTS_DIR: Final[Path] = PROJECT_ROOT / "artifacts"
MODELS_DIR: Final[Path] = ARTIFACTS_DIR / "models"
PREPROCESSORS_DIR: Final[Path] = ARTIFACTS_DIR / "preprocessors"
METADATA_DIR: Final[Path] = ARTIFACTS_DIR / "metadata"
REPORTS_DIR: Final[Path] = ARTIFACTS_DIR / "reports"

# Notebooks & Docs
NOTEBOOKS_DIR: Final[Path] = PROJECT_ROOT / "notebooks"
DOCS_DIR: Final[Path] = PROJECT_ROOT / "docs"

# Core Experiment & Reproducibility Defaults
RANDOM_SEED: Final[int] = 42
TARGET_COLUMN: Final[str] = "label"

# UCI PhiUSIIL ground truth mapping: 1 = legitimate, 0 = phishing
LABEL_MAPPING: Final[dict[int, str]] = {
    0: "phishing",
    1: "legitimate",
}

# The EXACT TWO headline predictive models for this project
HEADLINE_MODELS: Final[tuple[str, str]] = ("decision_tree", "ann")
HeadlineModelType = Literal["decision_tree", "ann"]

# Phase 3 Data Quality & Leakage Invariants (Interim Dataset Specification)
EXPECTED_RAW_ROW_COUNT: Final[int] = 235795
EXPECTED_DUPLICATE_URL_COUNT: Final[int] = 425
EXPECTED_INTERIM_ROW_COUNT: Final[int] = 235370
EXPECTED_INTERIM_LEGITIMATE_COUNT: Final[int] = 134850
EXPECTED_INTERIM_PHISHING_COUNT: Final[int] = 100520
EXPECTED_INTERIM_CLASS_COUNTS: Final[dict[str, int]] = {
    "1": EXPECTED_INTERIM_LEGITIMATE_COUNT,
    "0": EXPECTED_INTERIM_PHISHING_COUNT,
}

# Raw Dataset Column Exclusion Categories (Phase 2 Provenance Audit Invariants)
EXCLUDED_METADATA_COLUMNS: Final[tuple[str, ...]] = ("FILENAME",)

EXCLUDED_WEBPAGE_COLUMNS: Final[tuple[str, ...]] = (
    "LineOfCode",
    "LargestLineLength",
    "HasTitle",
    "Title",
    "DomainTitleMatchScore",
    "URLTitleMatchScore",
    "HasFavicon",
    "Robots",
    "IsResponsive",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasDescription",
    "NoOfPopup",
    "NoOfiFrame",
    "HasExternalFormSubmit",
    "HasSocialNet",
    "HasSubmitButton",
    "HasHiddenFields",
    "HasPasswordField",
    "Bank",
    "Pay",
    "Crypto",
    "HasCopyrightInfo",
    "NoOfImage",
    "NoOfCSS",
    "NoOfJS",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef",
)

EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS: Final[tuple[str, ...]] = (
    "URLSimilarityIndex",
    "TLDLegitimateProb",
    "URLCharProb",
)

DISQUALIFIED_RAW_COLUMNS: Final[tuple[str, ...]] = (
    *EXCLUDED_METADATA_COLUMNS,
    *EXCLUDED_WEBPAGE_COLUMNS,
    *EXCLUDED_UNVERIFIED_HEURISTIC_COLUMNS,
)

# Permanent Architectural & Safety Invariants
STATIC_ANALYSIS_ONLY: Final[bool] = True
ALLOW_URL_FETCH: Final[bool] = False
ALLOW_CREDENTIAL_COLLECTION: Final[bool] = False


class ProjectSettings(BaseModel):
    """Runtime configuration settings."""

    environment: str = Field(default="development", description="App environment")
    default_model: HeadlineModelType = Field(
        default="ann", description="Default model for inference"
    )
    random_seed: int = Field(default=RANDOM_SEED, description="Seed for reproducibility")
    log_level: str = Field(default="INFO", description="Logging level")
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"],
        description="Permitted CORS origins",
    )


settings = ProjectSettings()
