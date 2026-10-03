"""Unit tests for Phase 3 Data Quality and Cleaning Pipeline."""

import csv

from pathlib import Path

import pytest

from src.config import (
    DISQUALIFIED_RAW_COLUMNS,
)

from src.data.clean import (
    REQUIRED_CLEANING_COLUMNS,
    clean_dataset,
    clean_records,
)

from src.data.validate import EXPECTED_RAW_COLUMNS

def write_mock_dataset(path: Path, rows: list[dict[str, str]]) -> None:

    """Write test records using the complete expected raw dataset schema."""

    with open(path, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=EXPECTED_RAW_COLUMNS)

        writer.writeheader()

        writer.writerows(rows)

@pytest.fixture

def sample_records() -> list[dict[str, str]]:

    """Fixture providing mock records with duplicates and disqualified columns."""

    return [

        {

            "FILENAME": "1.txt",
            "URL": "https://example.com/login",
            "Domain": "example.com",
            "URLLength": "26",
            "LineOfCode": "500",
            "URLSimilarityIndex": "100.0",
            "label": "1",
        },
        {

            "FILENAME": "2.txt",
            "URL": "http://phish-site.org/update",
            "Domain": "phish-site.org",
            "URLLength": "30",
            "LineOfCode": "120",
            "URLSimilarityIndex": "45.0",
            "label": "0",
        },
        # Duplicate of record 2 with same label

        {

            "FILENAME": "3.txt",
            "URL": "http://phish-site.org/update",
            "Domain": "phish-site.org",
            "URLLength": "30",
            "LineOfCode": "125",
            "URLSimilarityIndex": "45.0",
            "label": "0",
        },
        # Another duplicate of record 2 with same label

        {

            "FILENAME": "4.txt",
            "URL": "http://phish-site.org/update",
            "Domain": "phish-site.org",
            "URLLength": "30",
            "LineOfCode": "130",
            "URLSimilarityIndex": "45.0",
            "label": "0",
        },
        {

            "FILENAME": "5.txt",
            "URL": "https://bank.com/portal",
            "Domain": "bank.com",
            "URLLength": "24",
            "LineOfCode": "850",
            "URLSimilarityIndex": "95.0",
            "label": "1",
        },
    ]

def test_exact_duplicate_handling(sample_records: list[dict[str, str]]) -> None:

    """Verify that exact duplicate URLs are removed and first occurrence is retained."""

    cleaned, report = clean_records(sample_records)

    assert report.raw_rows_count == 5

    assert report.cleaned_rows_count == 3

    assert report.duplicates_removed == 2

    assert len(cleaned) == 3

    # Check preserved URLs

    cleaned_urls = [rec["URL"] for rec in cleaned]

    assert cleaned_urls == [

        "https://example.com/login",
        "http://phish-site.org/update",
        "https://bank.com/portal",
    ]

    # Check target class distribution after deduplication

    assert report.label_distribution == {"1": 2, "0": 1}

def test_conflicting_labels_raises_error() -> None:

    """Verify that duplicate URLs with conflicting labels raise a ValueError."""

    conflicting_records = [

        {

            "URL": "https://suspicious.com/page",
            "Domain": "suspicious.com",
            "label": "1",
        },
        {

            "URL": "https://suspicious.com/page",
            "Domain": "suspicious.com",
            "label": "0",
        },
    ]

    with pytest.raises(ValueError, match="Conflicting label detected"):

        clean_records(conflicting_records)

def test_excluded_column_removal(sample_records: list[dict[str, str]]) -> None:

    """Verify that all disqualified columns are purged from output records."""

    cleaned, report = clean_records(sample_records)

    for record in cleaned:

        for disq_col in DISQUALIFIED_RAW_COLUMNS:

            assert disq_col not in record

        # Explicitly verify key categories

        assert "FILENAME" not in record

        assert "LineOfCode" not in record

        assert "URLSimilarityIndex" not in record

    assert report.excluded_columns_count == 3

    assert set(report.excluded_columns) == {
    "FILENAME",
    "LineOfCode",
    "URLSimilarityIndex",
}

    assert report.retained_columns_count == 4  # URL, Domain, URLLength, label in sample

def test_required_column_preservation(sample_records: list[dict[str, str]]) -> None:

    """Verify that required columns (URL, Domain, label) and retained attributes are kept."""

    cleaned, _ = clean_records(sample_records)

    for record in cleaned:

        for required_col in REQUIRED_CLEANING_COLUMNS:

            assert required_col in record

        # Retained lexical attribute from sample

        assert "URLLength" in record

def test_empty_input() -> None:

    """Verify clean_records handles empty input gracefully."""

    cleaned, report = clean_records([])

    assert cleaned == []

    assert report.raw_rows_count == 0

    assert report.cleaned_rows_count == 0

    assert report.duplicates_removed == 0

def test_malformed_input_non_dict() -> None:

    """Verify clean_records raises TypeError on non-dictionary records."""

    with pytest.raises(TypeError, match="must be a dictionary"):

        clean_records(["not-a-dict"])  # type: ignore[arg-type]

def test_malformed_input_missing_required_column() -> None:

    """Verify clean_records raises ValueError if a required column is missing."""

    invalid_record = [

        {"URL": "https://example.com", "label": "1"}  # Missing 'Domain'

    ]

    with pytest.raises(ValueError, match="missing required columns"):

        clean_records(invalid_record)

def test_malformed_input_non_string_url() -> None:

    """Verify clean_records raises TypeError if URL is not a string."""

    invalid_record = [

        {"URL": 12345, "Domain": "example.com", "label": "1"}

    ]

    with pytest.raises(TypeError, match="must be a string"):

        clean_records(invalid_record)

def test_clean_records_rejects_invalid_label(
    sample_records: list[dict[str, str]],
) -> None:

    """Verify that labels outside 0 and 1 are rejected."""

    records = [record.copy() for record in sample_records]

    records[0]["label"] = "2"

    with pytest.raises(ValueError, match="Invalid target label"):

        clean_records(records)

def test_deterministic_output(sample_records: list[dict[str, str]]) -> None:

    """Verify clean_records produces identical ordered results across runs."""

    cleaned1, report1 = clean_records(sample_records)

    cleaned2, report2 = clean_records(sample_records)

    assert cleaned1 == cleaned2

    assert report1.model_dump() == report2.model_dump()

def test_values_are_not_mutated() -> None:

    """Verify that string values, casing, and parameters are not silently altered."""

    records = [

        {

            "URL": "HTTPS://Example.COM/Path/To/Page?Query=1&Foo=Bar#Section",
            "Domain": "Example.COM",
            "label": "1",
        }

    ]

    cleaned, _ = clean_records(records)

    assert len(cleaned) == 1

    # Check exact casing and characters preserved

    assert cleaned[0]["URL"] == "HTTPS://Example.COM/Path/To/Page?Query=1&Foo=Bar#Section"

    assert cleaned[0]["Domain"] == "Example.COM"

    assert cleaned[0]["label"] == "1"

def test_clean_dataset_streaming_csv(tmp_path: Path) -> None:

    """Verify clean_dataset streaming execution on a mock CSV file."""

    mock_input = tmp_path / "mock_raw.csv"

    mock_output = tmp_path / "mock_cleaned.csv"

    rows = [

    {

        "FILENAME": "1.txt",
        "URL": "https://site1.com",
        "Domain": "site1.com",
        "LineOfCode": "100",
        "URLSimilarityIndex": "50.0",
        "label": "1",
    },
    {

        "FILENAME": "2.txt",
        "URL": "https://site2.com",
        "Domain": "site2.com",
        "LineOfCode": "200",
        "URLSimilarityIndex": "60.0",
        "label": "0",
    },
    {

        "FILENAME": "3.txt",
        "URL": "https://site2.com",
        "Domain": "site2.com",
        "LineOfCode": "200",
        "URLSimilarityIndex": "60.0",
        "label": "0",
    },
    {

        "FILENAME": "4.txt",
        "URL": "https://site3.com",
        "Domain": "site3.com",
        "LineOfCode": "300",
        "URLSimilarityIndex": "70.0",
        "label": "1",
    },
    ]

    write_mock_dataset(mock_input, rows)

    report = clean_dataset(
        input_file=mock_input,
        output_file=mock_output,
        disqualified_columns=DISQUALIFIED_RAW_COLUMNS,
    )

    assert report.raw_rows_count == 4

    assert report.cleaned_rows_count == 3

    assert report.duplicates_removed == 1

    assert report.label_distribution == {"1": 2, "0": 1}

    # Verify output file

    assert mock_output.exists()

    with open(mock_output, encoding="utf-8") as f:

        reader = csv.reader(f)

        out_header = next(reader)

        out_rows = list(reader)

    # Disqualified columns dropped

    assert "FILENAME" not in out_header

    assert "LineOfCode" not in out_header

    assert "URLSimilarityIndex" not in out_header

    # Retained columns present

    assert "URL" in out_header

    assert "Domain" in out_header

    assert "label" in out_header

    assert len(out_header) == 23

    assert len(out_rows) == 3

def test_clean_dataset_rejects_invalid_label(tmp_path: Path) -> None:

    """Verify that streaming cleaning rejects invalid target labels."""

    mock_input = tmp_path / "invalid_label.csv"

    mock_output = tmp_path / "cleaned.csv"

    rows = [

        {

            "URL": "https://example.com",
            "Domain": "example.com",
            "label": "2",
        }

    ]

    write_mock_dataset(mock_input, rows)

    with pytest.raises(ValueError, match="Invalid target label"):

        clean_dataset(
            input_file=mock_input,
            output_file=mock_output,
        )

    assert not mock_output.exists()

def test_clean_dataset_rejects_empty_file(tmp_path: Path) -> None:

    """Verify that an empty CSV raises a clear ValueError."""

    mock_input = tmp_path / "empty.csv"

    mock_output = tmp_path / "cleaned.csv"

    mock_input.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Input dataset is empty"):

        clean_dataset(
            input_file=mock_input,
            output_file=mock_output,
        )

    assert not mock_output.exists()

def test_clean_dataset_rejects_invalid_utf8(tmp_path: Path) -> None:

    """Verify malformed UTF-8 input is rejected without replacing output."""

    mock_input = tmp_path / "invalid_encoding.csv"

    mock_output = tmp_path / "cleaned.csv"

    mock_input.write_bytes(b"\xff\xfe\xfa")

    original_output = "previous valid output\n"

    mock_output.write_text(original_output, encoding="utf-8")

    with pytest.raises(UnicodeDecodeError):

        clean_dataset(
            input_file=mock_input,
            output_file=mock_output,
        )

    assert mock_output.read_text(encoding="utf-8") == original_output

def test_clean_dataset_conflict_raises_error(tmp_path: Path) -> None:

    """Verify failed cleaning preserves any previously existing output."""

    mock_input = tmp_path / "mock_conflict.csv"

    mock_output = tmp_path / "mock_output.csv"

    rows = [

    {

        "URL": "https://valid.com",
        "Domain": "valid.com",
        "label": "1",
    },
    {

        "URL": "https://conflict.com",
        "Domain": "conflict.com",
        "label": "1",
    },
    {

        "URL": "https://conflict.com",
        "Domain": "conflict.com",
        "label": "0",
    },
    ]

    write_mock_dataset(mock_input, rows)

    original_output = "previous valid output\n"

    mock_output.write_text(original_output, encoding="utf-8")

    with pytest.raises(ValueError, match="Conflicting label detected"):

        clean_dataset(input_file=mock_input, output_file=mock_output)

    assert mock_output.read_text(encoding="utf-8") == original_output

def test_clean_dataset_rejects_same_input_and_output_path(
    tmp_path: Path,
) -> None:

    """Verify cleaning cannot overwrite its source dataset."""

    mock_input = tmp_path / "raw.csv"

    with open(mock_input, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["URL", "Domain", "label"])

        writer.writerow(["https://example.com", "example.com", "1"])

    original_content = mock_input.read_bytes()

    with pytest.raises(ValueError, match="must differ"):

        clean_dataset(
            input_file=mock_input,
            output_file=mock_input,
        )

    assert mock_input.read_bytes() == original_content

def test_clean_dataset_rejects_incomplete_header(tmp_path: Path) -> None:

    """Verify cleaning rejects a CSV that does not match the expected schema."""

    mock_input = tmp_path / "incomplete.csv"

    mock_output = tmp_path / "cleaned.csv"

    with open(mock_input, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow(["URL", "Domain", "label"])

        writer.writerow(["https://example.com", "example.com", "1"])

    with pytest.raises(ValueError, match="header"):

        clean_dataset(
            input_file=mock_input,
            output_file=mock_output,
        )

    assert not mock_output.exists()
