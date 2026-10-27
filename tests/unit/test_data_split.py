"""Unit tests for Phase 5 domain-grouped stratified train/test split."""

import csv
from pathlib import Path
from typing import Any

import pytest

from src.config import (
    EXPECTED_TEST_DOMAIN_COUNT,
    EXPECTED_TEST_ROW_COUNT,
    EXPECTED_TRAIN_DOMAIN_COUNT,
    EXPECTED_TRAIN_ROW_COUNT,
    SPLIT_GROUP_COLUMN,
    SPLIT_N_SPLITS,
    SPLIT_TEST_SIZE,
    TEST_DATASET_FILE,
    TRAIN_DATASET_FILE,
)
from src.data.split import (
    SplitReport,
    split_dataset,
    split_records,
    validate_split,
)


@pytest.fixture
def mock_domain_records() -> list[dict[str, Any]]:
    """Create a diverse mock dataset with repeated domains, mixed labels, and multiple groups."""
    records: list[dict[str, Any]] = []
    # 20 distinct domains, 2 URLs each = 40 rows
    # 10 phishing domains (20 rows), 10 legitimate domains (20 rows)
    for i in range(10):
        records.append({
            "URL": f"https://legit-domain-{i}.com/page1",
            "Domain": f"legit-domain-{i}.com",
            "label": "1",
        })
        records.append({
            "URL": f"https://legit-domain-{i}.com/page2",
            "Domain": f"legit-domain-{i}.com",
            "label": "1",
        })
    for i in range(10):
        records.append({
            "URL": f"http://phish-domain-{i}.org/login",
            "Domain": f"phish-domain-{i}.org",
            "label": "0",
        })
        records.append({
            "URL": f"http://phish-domain-{i}.org/update",
            "Domain": f"phish-domain-{i}.org",
            "label": "0",
        })
    return records


def test_split_constants_configured() -> None:
    """Verify Phase 5 configuration constants."""
    assert SPLIT_TEST_SIZE == 0.20
    assert SPLIT_N_SPLITS == 5
    assert SPLIT_GROUP_COLUMN == "Domain"
    assert TRAIN_DATASET_FILE.name == "train.csv"
    assert TEST_DATASET_FILE.name == "test.csv"
    assert EXPECTED_TRAIN_ROW_COUNT == 188296
    assert EXPECTED_TEST_ROW_COUNT == 47074
    assert EXPECTED_TRAIN_DOMAIN_COUNT == 176072
    assert EXPECTED_TEST_DOMAIN_COUNT == 44014
    assert EXPECTED_TRAIN_ROW_COUNT + EXPECTED_TEST_ROW_COUNT == 235370
    assert EXPECTED_TRAIN_DOMAIN_COUNT + EXPECTED_TEST_DOMAIN_COUNT == 220086


def test_domain_isolation_guarantee(mock_domain_records: list[dict[str, Any]]) -> None:
    """Verify that no domain appears in both train and test partitions."""
    train_records, test_records, report = split_records(
        mock_domain_records,
        group_column="Domain",
        label_column="label",
        n_splits=5,
        random_seed=42,
    )

    train_domains = {r["Domain"].lower() for r in train_records}
    test_domains = {r["Domain"].lower() for r in test_records}

    overlap = train_domains & test_domains
    assert len(overlap) == 0, f"Overlapping domains detected: {overlap}"
    assert report.domain_overlap_count == 0
    assert report.train_domains_count == len(train_domains)
    assert report.test_domains_count == len(test_domains)
    assert report.total_domains == len(train_domains) + len(test_domains)


def test_both_classes_present_in_both_partitions(
    mock_domain_records: list[dict[str, Any]],
) -> None:
    """Verify that both phishing (0) and legitimate (1) exist in train and test."""
    train_records, test_records, report = split_records(
        mock_domain_records,
        random_seed=42,
    )

    train_labels = {str(r["label"]) for r in train_records}
    test_labels = {str(r["label"]) for r in test_records}

    assert train_labels == {"0", "1"}
    assert test_labels == {"0", "1"}
    assert report.train_class_distribution["0"] > 0
    assert report.train_class_distribution["1"] > 0
    assert report.test_class_distribution["0"] > 0
    assert report.test_class_distribution["1"] > 0


def test_reproducibility_with_fixed_seed(
    mock_domain_records: list[dict[str, Any]],
) -> None:
    """Verify identical outputs across multiple runs with the same random seed."""
    train1, test1, rep1 = split_records(mock_domain_records, random_seed=42)
    train2, test2, rep2 = split_records(mock_domain_records, random_seed=42)

    assert train1 == train2
    assert test1 == test2
    assert rep1.model_dump() == rep2.model_dump()


def test_conflicting_label_domain_stays_in_single_partition() -> None:
    """Verify multi-tenant domains with both 0 and 1 labels stay strictly isolated."""
    records = [
        {"URL": "https://shared.com/benign", "Domain": "shared.com", "label": "1"},
        {"URL": "https://shared.com/phish", "Domain": "shared.com", "label": "0"},
    ]
    # Add 5 distinct domains for class 1 and 5 distinct domains for class 0
    for i in range(5):
        records.append({"URL": f"https://legit{i}.com", "Domain": f"legit{i}.com", "label": "1"})
        records.append({"URL": f"https://phish{i}.org", "Domain": f"phish{i}.org", "label": "0"})

    train_records, test_records, _ = split_records(records, n_splits=5, random_seed=42)

    shared_in_train = any(r["Domain"] == "shared.com" for r in train_records)
    shared_in_test = any(r["Domain"] == "shared.com" for r in test_records)

    # Must be in one partition or the other, NEVER both
    assert shared_in_train != shared_in_test
    # Check total count of shared.com records is preserved
    count = sum(1 for r in train_records if r["Domain"] == "shared.com") + sum(
        1 for r in test_records if r["Domain"] == "shared.com"
    )
    assert count == 2


def test_validate_split_detects_domain_overlap() -> None:
    """Verify validate_split raises ValueError when domain overlap exists."""
    train = [{"URL": "https://a.com/1", "Domain": "a.com", "label": "1"},
             {"URL": "https://b.com/1", "Domain": "b.com", "label": "0"}]
    test = [{"URL": "https://a.com/2", "Domain": "a.com", "label": "1"},
            {"URL": "https://c.com/1", "Domain": "c.com", "label": "0"}]

    with pytest.raises(ValueError, match="Domain isolation violated"):
        validate_split(train, test)


def test_validate_split_detects_missing_class() -> None:
    """Verify validate_split raises ValueError when a partition lacks a class."""
    train = [{"URL": "https://a.com/1", "Domain": "a.com", "label": "1"},
             {"URL": "https://b.com/1", "Domain": "b.com", "label": "1"}]
    test = [{"URL": "https://c.com/1", "Domain": "c.com", "label": "0"},
            {"URL": "https://d.com/1", "Domain": "d.com", "label": "1"}]

    with pytest.raises(ValueError, match="Training partition must contain both classes"):
        validate_split(train, test)


def test_split_records_input_validations() -> None:
    """Verify input validation errors in split_records."""
    # Empty records
    with pytest.raises(ValueError, match="cannot be empty"):
        split_records([])

    # Non-dict record
    with pytest.raises(TypeError, match="must be a dictionary"):
        split_records(["not a dict"])  # type: ignore

    # Missing group column
    with pytest.raises(ValueError, match="missing required column"):
        split_records([{"label": "1"}])

    # Empty domain value
    with pytest.raises(ValueError, match="empty domain"):
        split_records([{"Domain": "  ", "label": "1"}])

    # Invalid label
    with pytest.raises(ValueError, match="Invalid label"):
        split_records([{"Domain": "x.com", "label": "2"}])

    # Fewer unique domains than n_splits
    with pytest.raises(ValueError, match="must be >= n_splits"):
        split_records([
            {"Domain": "d1.com", "label": "1"},
            {"Domain": "d2.com", "label": "0"},
        ], n_splits=5)

    # Single class dataset
    with pytest.raises(ValueError, match="at least two target classes"):
        split_records([
            {"Domain": f"d{i}.com", "label": "1"} for i in range(6)
        ], n_splits=5)

    # Class with fewer members than n_splits
    with pytest.raises(ValueError, match="which is fewer than n_splits"):
        records = [{"Domain": f"d{i}.com", "label": "1"} for i in range(6)]
        records.append({"Domain": "phish.com", "label": "0"})
        split_records(records, n_splits=5)


def test_split_dataset_file_io(tmp_path: Path) -> None:
    """Verify CSV reading, atomic output generation, and report fidelity."""
    in_file = tmp_path / "cleaned.csv"
    train_file = tmp_path / "train.csv"
    test_file = tmp_path / "test.csv"

    # Write a test interim CSV
    header = ["URL", "Domain", "label", "extra_col"]
    rows = []
    for i in range(15):
        rows.append([f"https://dom{i}.com/p", f"dom{i}.com", "1" if i % 2 == 0 else "0", "val"])
    with open(in_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    report = split_dataset(
        input_file=in_file,
        train_output_file=train_file,
        test_output_file=test_file,
        n_splits=5,
        random_seed=42,
    )

    assert isinstance(report, SplitReport)
    assert train_file.exists()
    assert test_file.exists()
    assert report.total_rows == 15
    assert report.train_rows + report.test_rows == 15
    assert report.domain_overlap_count == 0

    # Verify headers and data in generated files
    with open(train_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        train_header = next(reader)
        assert train_header == header
        train_rows = list(reader)
        assert len(train_rows) == report.train_rows

    with open(test_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        test_header = next(reader)
        assert test_header == header
        test_rows = list(reader)
        assert len(test_rows) == report.test_rows


def test_split_dataset_path_validation(tmp_path: Path) -> None:
    """Verify file path error handling."""
    missing_file = tmp_path / "nonexistent.csv"
    train_file = tmp_path / "train.csv"
    test_file = tmp_path / "test.csv"

    with pytest.raises(FileNotFoundError, match="not found"):
        split_dataset(
            input_file=missing_file,
            train_output_file=train_file,
            test_output_file=test_file,
        )

    existing_file = tmp_path / "existing.csv"
    existing_file.write_text("URL,Domain,label\nhttps://a.com,a.com,1\n", encoding="utf-8")

    # Same input and output
    with pytest.raises(ValueError, match="Input and output dataset paths must differ"):
        split_dataset(
            input_file=existing_file,
            train_output_file=existing_file,
            test_output_file=test_file,
        )

    # Same train and test output
    with pytest.raises(ValueError, match="Train and test output paths must differ"):
        split_dataset(
            input_file=existing_file,
            train_output_file=train_file,
            test_output_file=train_file,
        )
