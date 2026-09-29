"""Dataset validation module for PhishGuard.

Validates the integrity, schema, row counts, target distribution, and checksum
of the raw UCI PhiUSIIL Phishing URL Dataset without altering the data.
"""

import csv
import hashlib
import sys
from pathlib import Path
from typing import Final

from pydantic import BaseModel, Field

from src.config import (
    LABEL_MAPPING,
    RAW_DATASET_FILE,
    RAW_DATASET_SHA256,
    TARGET_COLUMN,
)

# Documented UCI dataset facts
EXPECTED_ROW_COUNT: Final[int] = 235795
EXPECTED_LEGITIMATE_COUNT: Final[int] = 134850
EXPECTED_PHISHING_COUNT: Final[int] = 100945

# Canonical 56 columns from the raw CSV header (note UTF-8 BOM on first column in source)
EXPECTED_RAW_COLUMNS: Final[tuple[str, ...]] = (
    "FILENAME",
    "URL",
    "URLLength",
    "Domain",
    "DomainLength",
    "IsDomainIP",
    "TLD",
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
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
    "label",
)


class ValidationReport(BaseModel):
    """Structured report returned by the dataset validation pipeline."""

    is_valid: bool = Field(description="True if all validation checks passed")
    file_path: str = Field(description="Path to validated dataset file")
    file_size_bytes: int = Field(default=0, description="Size of file in bytes")
    sha256_computed: str = Field(default="", description="Computed SHA-256 hash")
    sha256_matched: bool = Field(default=False, description="Whether SHA-256 matched reference")
    total_rows: int = Field(default=0, description="Total data rows parsed")
    total_columns: int = Field(default=0, description="Total columns in header")
    target_column_present: bool = Field(default=False, description="Whether target column exists")
    class_counts: dict[str, int] = Field(default_factory=dict, description="Target label counts")
    missing_values_count: int = Field(default=0, description="Count of empty or null cells")
    errors: list[str] = Field(default_factory=list, description="List of validation errors found")


def compute_sha256(file_path: Path) -> str:
    """Compute the SHA-256 hex digest of a file in chunks."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def normalize_header(header: list[str]) -> list[str]:
    """Strip UTF-8 BOM if present on the first header column."""
    cleaned = list(header)
    if cleaned and cleaned[0].startswith("\ufeff"):
        cleaned[0] = cleaned[0].lstrip("\ufeff")
    return cleaned


def validate_raw_dataset(
    file_path: Path | str | None = None,
    verify_checksum: bool = True,
    expected_sha256: str | None = None,
) -> ValidationReport:
    """Validate the raw UCI PhiUSIIL dataset file.

    Parameters
    ----------
    file_path : Path | str | None, optional
        Path to the raw CSV file. Defaults to `src.config.RAW_DATASET_FILE`.
    verify_checksum : bool, default True
        Whether to compute and verify the SHA-256 hash.
    expected_sha256 : str | None, optional
        Reference SHA-256 hash. Defaults to `src.config.RAW_DATASET_SHA256`.

    Returns
    -------
    ValidationReport
        Structured report detailing the validation results and any errors.
    """
    path = Path(file_path) if file_path else RAW_DATASET_FILE
    expected_hash = expected_sha256 or RAW_DATASET_SHA256
    errors: list[str] = []

    # 1. Existence and type check
    if not path.exists():
        errors.append(f"Raw dataset file not found at: {path}")
        return ValidationReport(is_valid=False, file_path=str(path), errors=errors)

    if not path.is_file():
        errors.append(f"Target path is not a file: {path}")
        return ValidationReport(is_valid=False, file_path=str(path), errors=errors)

    file_size = path.stat().st_size
    if file_size == 0:
        errors.append(f"Raw dataset file is empty (0 bytes): {path}")
        return ValidationReport(
            is_valid=False, file_path=str(path), file_size_bytes=0, errors=errors
        )

    # 2. Checksum verification
    computed_hash = ""
    checksum_matched = False
    if verify_checksum:
        computed_hash = compute_sha256(path)
        checksum_matched = computed_hash == expected_hash
        if not checksum_matched:
            errors.append(
                f"SHA-256 checksum mismatch: expected {expected_hash}, got {computed_hash}"
            )

    # 3. CSV parsing and schema verification
    total_rows = 0
    total_columns = 0
    target_present = False
    class_counts: dict[str, int] = {}
    missing_values = 0

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            try:
                raw_header = next(reader)
            except StopIteration:
                errors.append("File contains no header row.")
                return ValidationReport(
                    is_valid=False,
                    file_path=str(path),
                    file_size_bytes=file_size,
                    sha256_computed=computed_hash,
                    sha256_matched=checksum_matched,
                    errors=errors,
                )

            header = normalize_header(raw_header)
            total_columns = len(header)

            # Check column count
            expected_col_count = len(EXPECTED_RAW_COLUMNS)
            if total_columns != expected_col_count:
                errors.append(
                    f"Column count mismatch: expected {expected_col_count}, got {total_columns}"
                )

            # Check expected columns
            missing_cols = set(EXPECTED_RAW_COLUMNS) - set(header)
            if missing_cols:
                errors.append(f"Missing expected columns: {sorted(missing_cols)}")

            # Check target column
            target_present = TARGET_COLUMN in header
            if not target_present:
                errors.append(f"Target column '{TARGET_COLUMN}' not found in header.")
                label_idx = -1
            else:
                label_idx = header.index(TARGET_COLUMN)

            # 4. Row-level scanning: row count, column consistency, null values, target distribution
            valid_target_values = {str(k) for k in LABEL_MAPPING.keys()}

            for row_num, row in enumerate(reader, start=1):
                total_rows += 1

                # Check row width
                if len(row) != total_columns:
                    errors.append(
                        f"Row {row_num} width mismatch: expected {total_columns}, got {len(row)}"
                    )

                # Check missing / null cells
                for _col_idx, val in enumerate(row):
                    if val == "" or val is None:
                        missing_values += 1

                # Check label value
                if label_idx >= 0 and label_idx < len(row):
                    lbl = row[label_idx]
                    if lbl not in valid_target_values:
                        errors.append(
                            f"Row {row_num} has unexpected target label '{lbl}'"
                        )
                    class_counts[lbl] = class_counts.get(lbl, 0) + 1

    except Exception as exc:
        errors.append(f"Failed to read or parse CSV: {exc}")
        return ValidationReport(
            is_valid=False,
            file_path=str(path),
            file_size_bytes=file_size,
            sha256_computed=computed_hash,
            sha256_matched=checksum_matched,
            errors=errors,
        )

    # 5. Row count verification
    if total_rows != EXPECTED_ROW_COUNT:
        errors.append(
            f"Row count mismatch: expected {EXPECTED_ROW_COUNT}, got {total_rows}"
        )

    # 6. Target distribution verification
    legitimate_count = class_counts.get("1", 0)
    phishing_count = class_counts.get("0", 0)

    if legitimate_count != EXPECTED_LEGITIMATE_COUNT:
       errors.append(
        f"Legitimate count mismatch: expected {EXPECTED_LEGITIMATE_COUNT}, "
        f"got {legitimate_count}"
        )

    if phishing_count != EXPECTED_PHISHING_COUNT:
        errors.append(
            f"Phishing count mismatch: expected {EXPECTED_PHISHING_COUNT}, got {phishing_count}"
        )

    # 7. Missing values verification (UCI dataset explicitly has 0 missing values)
    if missing_values > 0:
        errors.append(
            f"Dataset contains {missing_values} missing/empty values; expected 0."
        )

    is_valid = len(errors) == 0

    return ValidationReport(
        is_valid=is_valid,
        file_path=str(path),
        file_size_bytes=file_size,
        sha256_computed=computed_hash,
        sha256_matched=checksum_matched,
        total_rows=total_rows,
        total_columns=total_columns,
        target_column_present=target_present,
        class_counts=class_counts,
        missing_values_count=missing_values,
        errors=errors,
    )


def main() -> int:
    """CLI execution entrypoint for dataset validation."""
    print("=" * 70)
    print("PhishGuard Dataset Validation (Phase 1 — Provenance & Integrity)")
    print("=" * 70)
    print(f"Target raw file: {RAW_DATASET_FILE}")
    print("Scanning dataset and computing SHA-256...")

    report = validate_raw_dataset()

    print(f"File Size:          {report.file_size_bytes:,} bytes")
    print(f"SHA-256 Computed:   {report.sha256_computed}")
    print(f"SHA-256 Matched:    {report.sha256_matched}")
    print(f"Total Data Rows:    {report.total_rows:,} (Expected: {EXPECTED_ROW_COUNT:,})")
    print(f"Total Columns:      {report.total_columns} (Expected: {len(EXPECTED_RAW_COLUMNS)})")
    print(f"Target Present:     {report.target_column_present} ('{TARGET_COLUMN}')")
    print(f"Class Distribution: {report.class_counts}")
    print(
        f"  - Legitimate (1): {report.class_counts.get('1', 0):,} "
        f"(Expected: {EXPECTED_LEGITIMATE_COUNT:,})"
)
    print(
        f"  - Phishing (0):   {report.class_counts.get('0', 0):,} "
        f"(Expected: {EXPECTED_PHISHING_COUNT:,})"
)
    print(f"Missing Values:     {report.missing_values_count} (Expected: 0)")
    print("-" * 70)

    if report.is_valid:
        print("RESULT: [PASS] Raw dataset is pristine, valid, and matches UCI specification.")
        print("=" * 70)
        return 0
    else:
        print("RESULT: [FAIL] Validation errors detected:")
        for err in report.errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
