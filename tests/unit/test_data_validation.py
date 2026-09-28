"""Unit tests for Phase 1 dataset acquisition, integrity, and schema validation."""

import csv
from pathlib import Path

from src.config import RAW_DATASET_FILE, RAW_DATASET_SHA256, TARGET_COLUMN
from src.data.load import load_raw_header, stream_raw_records
from src.data.validate import (
    EXPECTED_LEGITIMATE_COUNT,
    EXPECTED_PHISHING_COUNT,
    EXPECTED_RAW_COLUMNS,
    EXPECTED_ROW_COUNT,
    compute_sha256,
    validate_raw_dataset,
)


def test_raw_dataset_file_exists() -> None:
    """Verify that the raw CSV file is present and non-empty."""
    assert RAW_DATASET_FILE.exists(), f"Raw file missing at: {RAW_DATASET_FILE}"
    assert RAW_DATASET_FILE.is_file()
    assert RAW_DATASET_FILE.stat().st_size > 50_000_000  # Expected ~56.8 MB


def test_raw_dataset_sha256_checksum() -> None:
    """Verify that the raw dataset SHA-256 hash matches the documented reference."""
    computed_hash = compute_sha256(RAW_DATASET_FILE)
    assert computed_hash == RAW_DATASET_SHA256


def test_validate_raw_dataset_full_integrity() -> None:
    """Run full validation on the raw dataset and assert perfect compliance with UCI specification."""
    report = validate_raw_dataset(RAW_DATASET_FILE, verify_checksum=True)

    assert report.is_valid is True, f"Validation failed with errors: {report.errors}"
    assert report.sha256_matched is True
    assert report.total_rows == EXPECTED_ROW_COUNT
    assert report.total_columns == len(EXPECTED_RAW_COLUMNS)
    assert report.target_column_present is True
    assert report.missing_values_count == 0

    # Verify class distribution
    assert report.class_counts.get("1") == EXPECTED_LEGITIMATE_COUNT
    assert report.class_counts.get("0") == EXPECTED_PHISHING_COUNT
    assert len(report.errors) == 0


def test_load_raw_header() -> None:
    """Verify load_raw_header returns clean column names with BOM stripped."""
    header = load_raw_header()
    assert len(header) == 56
    assert header[0] == "FILENAME"  # BOM stripped
    assert header[-1] == TARGET_COLUMN
    assert tuple(header) == EXPECTED_RAW_COLUMNS


def test_stream_raw_records_limit() -> None:
    """Verify stream_raw_records yields dicts with proper keys and respects limits."""
    records = list(stream_raw_records(limit=5))
    assert len(records) == 5
    for record in records:
        assert isinstance(record, dict)
        assert "FILENAME" in record
        assert "URL" in record
        assert "label" in record
        assert record["label"] in {"0", "1"}


def test_validator_detects_missing_file(tmp_path: Path) -> None:
    """Verify validator fails gracefully when target file does not exist."""
    fake_path = tmp_path / "nonexistent.csv"
    report = validate_raw_dataset(fake_path, verify_checksum=False)
    assert report.is_valid is False
    assert any("not found" in err.lower() for err in report.errors)


def test_validator_detects_corrupted_header(tmp_path: Path) -> None:
    """Verify validator flags missing expected columns."""
    corrupted_csv = tmp_path / "corrupted.csv"
    with open(corrupted_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["col1", "col2", "col3"])  # Missing expected columns & target
        writer.writerow(["val1", "val2", "val3"])

    report = validate_raw_dataset(corrupted_csv, verify_checksum=False)
    assert report.is_valid is False
    assert report.target_column_present is False
    assert any("missing expected columns" in err.lower() for err in report.errors)


def test_validator_detects_invalid_labels(tmp_path: Path) -> None:
    """Verify validator flags invalid label values in rows."""
    bad_labels_csv = tmp_path / "bad_labels.csv"
    with open(bad_labels_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(EXPECTED_RAW_COLUMNS)
        # Create a row with label '2' instead of '0' or '1'
        bad_row = ["test"] * (len(EXPECTED_RAW_COLUMNS) - 1) + ["2"]
        writer.writerow(bad_row)

    report = validate_raw_dataset(bad_labels_csv, verify_checksum=False)
    assert report.is_valid is False
    assert any("unexpected target label '2'" in err for err in report.errors)
