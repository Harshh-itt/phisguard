"""Data cleaning and leakage control pipeline for PhishGuard.

Implements deterministic URL deduplication and column exclusion for the
interim dataset stage while preserving raw dataset immutability.
"""

import csv
import os
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Final

from pydantic import BaseModel, Field

from src.config import (
    DISQUALIFIED_RAW_COLUMNS,
    INTERIM_DATASET_FILE,
    RAW_DATASET_FILE,
    TARGET_COLUMN,
)
from src.data.validate import EXPECTED_RAW_COLUMNS, normalize_header

REQUIRED_CLEANING_COLUMNS: Final[tuple[str, ...]] = (
    "URL",
    "Domain",
    TARGET_COLUMN,
)

RETAINED_RAW_COLUMNS: Final[tuple[str, ...]] = tuple(
    col for col in EXPECTED_RAW_COLUMNS if col not in set(DISQUALIFIED_RAW_COLUMNS)
)


class CleaningReport(BaseModel):
    """Structured audit report produced by the data cleaning pipeline."""

    raw_rows_count: int = Field(description="Total raw records ingested")
    cleaned_rows_count: int = Field(description="Total clean records retained")
    duplicates_removed: int = Field(description="Total duplicate URL rows removed")
    excluded_columns_count: int = Field(
        description="Count of disqualified columns dropped"
    )
    retained_columns_count: int = Field(
        description="Count of columns retained in clean dataset"
    )
    excluded_columns: list[str] = Field(
        default_factory=list, description="List of dropped columns"
    )
    retained_columns: list[str] = Field(
        default_factory=list, description="List of retained columns"
    )
    label_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Target class distribution after cleaning",
    )


def clean_records(
    records: Iterable[dict[str, Any]],
    disqualified_columns: set[str] | tuple[str, ...] = DISQUALIFIED_RAW_COLUMNS,
    url_column: str = "URL",
    label_column: str = TARGET_COLUMN,
    required_columns: tuple[str, ...] = REQUIRED_CLEANING_COLUMNS,
) -> tuple[list[dict[str, Any]], CleaningReport]:
    """Clean records by deduplicating URLs and removing disqualified columns."""
    disq_set = set(disqualified_columns)
    seen_urls: dict[str, Any] = {}
    cleaned_records: list[dict[str, Any]] = []
    raw_rows_count = 0
    duplicates_removed = 0
    label_distribution: dict[str, int] = {}
    observed_columns: list[str] = []
    retained_columns: list[str] = []

    for record in records:
        raw_rows_count += 1

        if not isinstance(record, dict):
            raise TypeError(
                f"Record at index {raw_rows_count - 1} must be a dictionary, "
                f"got {type(record).__name__}."
            )

        missing_required = set(required_columns) - set(record)
        if missing_required:
            raise ValueError(
                f"Record at index {raw_rows_count - 1} is missing required "
                f"columns: {sorted(missing_required)}"
            )

        if not observed_columns:
            observed_columns = list(record.keys())
            retained_columns = [
                col for col in observed_columns if col not in disq_set
            ]

        url = record[url_column]
        if not isinstance(url, str):
            raise TypeError(
                f"URL value in record {raw_rows_count - 1} must be a string, "
                f"got {type(url).__name__}."
            )
        if not url.strip():
            raise ValueError(
                f"URL value in record {raw_rows_count - 1} must not be empty."
            )

        label = record[label_column]
        label_key = str(label)
        if label_key not in {"0", "1"}:
            raise ValueError(
                f"Invalid target label '{label}' in record "
                f"{raw_rows_count - 1}. Expected 0 or 1."
            )

        if url in seen_urls:
            previous_label = seen_urls[url]
            if str(previous_label) != label_key:
                raise ValueError(
                    f"Conflicting label detected for duplicate URL '{url}': "
                    f"previously observed label '{previous_label}', "
                    f"current record has label '{label}'."
                )
            duplicates_removed += 1
            continue

        seen_urls[url] = label
        cleaned_records.append(
            {col: record[col] for col in retained_columns}
        )
        label_distribution[label_key] = (
            label_distribution.get(label_key, 0) + 1
        )

    excluded_columns = [
        col for col in observed_columns if col in disq_set
    ]
    report = CleaningReport(
        raw_rows_count=raw_rows_count,
        cleaned_rows_count=len(cleaned_records),
        duplicates_removed=duplicates_removed,
        excluded_columns_count=len(excluded_columns),
        retained_columns_count=len(retained_columns),
        excluded_columns=excluded_columns,
        retained_columns=retained_columns,
        label_distribution=label_distribution,
    )
    return cleaned_records, report


def clean_dataset(
    input_file: Path | str | None = None,
    output_file: Path | str | None = None,
    disqualified_columns: set[str] | tuple[str, ...] = DISQUALIFIED_RAW_COLUMNS,
    url_column: str = "URL",
    label_column: str = TARGET_COLUMN,
    required_columns: tuple[str, ...] = REQUIRED_CLEANING_COLUMNS,
) -> CleaningReport:
    """Stream and clean a dataset, replacing the output only on success."""
    in_path = Path(input_file) if input_file else RAW_DATASET_FILE
    out_path = Path(output_file) if output_file else INTERIM_DATASET_FILE

    if in_path.resolve() == out_path.resolve():
        raise ValueError("Input and output paths must differ.")
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found at: {in_path}")

    disq_set = set(disqualified_columns)
    seen_urls: dict[str, str] = {}
    label_distribution: dict[str, int] = {}
    raw_rows_count = 0
    duplicates_removed = 0
    cleaned_rows_count = 0
    retained_header: list[str] = []
    excluded_columns: list[str] = []

    out_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=out_path.parent,
            prefix=f".{out_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as fout:
            temp_path = Path(fout.name)

            with open(in_path, encoding="utf-8", newline="") as fin:
                reader = csv.reader(fin)
                try:
                    raw_header = next(reader)
                except StopIteration as exc:
                    raise ValueError("Input dataset is empty.") from exc

                header = normalize_header(raw_header)
                if len(header) != len(set(header)):
                    raise ValueError(
                        "Input dataset contains duplicate column headers."
                    )
                if tuple(header) != EXPECTED_RAW_COLUMNS:
                    raise ValueError(
                        "Input dataset header does not match the expected "
                        "56-column schema."
                    )

                missing_required = set(required_columns) - set(header)
                if missing_required:
                    raise ValueError(
                        "Input dataset header is missing required columns: "
                        f"{sorted(missing_required)}"
                    )
                if url_column not in header or label_column not in header:
                    raise ValueError(
                        "Configured URL or target column is missing from header."
                    )

                url_idx = header.index(url_column)
                label_idx = header.index(label_column)
                retained_indices = [
                    idx for idx, col in enumerate(header) if col not in disq_set
                ]
                retained_header = [header[idx] for idx in retained_indices]
                excluded_columns = [
                    col for col in header if col in disq_set
                ]

                writer = csv.writer(fout)
                writer.writerow(retained_header)

                for row in reader:
                    raw_rows_count += 1
                    if len(row) != len(header):
                        raise ValueError(
                            f"Row {raw_rows_count} width mismatch: "
                            f"expected {len(header)} columns, got {len(row)}."
                        )

                    url = row[url_idx]
                    label = row[label_idx]
                    if not url.strip():
                        raise ValueError(
                            f"URL value in row {raw_rows_count} must not be empty."
                        )
                    if label not in {"0", "1"}:
                        raise ValueError(
                            f"Invalid target label '{label}' in row "
                            f"{raw_rows_count}. Expected 0 or 1."
                        )

                    if url in seen_urls:
                        previous_label = seen_urls[url]
                        if previous_label != label:
                            raise ValueError(
                                f"Conflicting label detected for duplicate "
                                f"URL '{url}': previously observed label "
                                f"'{previous_label}', current row "
                                f"{raw_rows_count} has label '{label}'."
                            )
                        duplicates_removed += 1
                        continue

                    seen_urls[url] = label
                    cleaned_rows_count += 1
                    label_distribution[label] = (
                        label_distribution.get(label, 0) + 1
                    )
                    writer.writerow([row[idx] for idx in retained_indices])

        os.replace(temp_path, out_path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return CleaningReport(
        raw_rows_count=raw_rows_count,
        cleaned_rows_count=cleaned_rows_count,
        duplicates_removed=duplicates_removed,
        excluded_columns_count=len(excluded_columns),
        retained_columns_count=len(retained_header),
        excluded_columns=excluded_columns,
        retained_columns=retained_header,
        label_distribution=label_distribution,
    )
