"""Read-only dataset loader for PhishGuard.

Provides safe, streaming access to the raw UCI PhiUSIIL Phishing URL Dataset
under strict read-only guarantees. Never mutates data/raw.
"""

import csv
from collections.abc import Iterator
from pathlib import Path

from src.config import RAW_DATASET_FILE
from src.data.validate import normalize_header


def get_raw_dataset_path(file_path: Path | str | None = None) -> Path:
    """Resolve and verify existence of the raw dataset file."""
    path = Path(file_path) if file_path else RAW_DATASET_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Raw dataset file not found at: {path}. "
            "Please ensure dataset is downloaded under data/raw/."
        )
    return path


def load_raw_header(file_path: Path | str | None = None) -> list[str]:
    """Load the column names from the raw dataset header.

    Parameters
    ----------
    file_path : Path | str | None, optional
        Path to the raw CSV file. Defaults to `RAW_DATASET_FILE`.

    Returns
    -------
    list[str]
        List of cleaned column names (with BOM stripped if present).
    """
    path = get_raw_dataset_path(file_path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        raw_header = next(reader)
        return normalize_header(raw_header)


def stream_raw_records(
    file_path: Path | str | None = None,
    limit: int | None = None,
) -> Iterator[dict[str, str]]:
    """Stream raw records from the dataset as dictionaries in read-only mode.

    Parameters
    ----------
    file_path : Path | str | None, optional
        Path to the raw CSV file. Defaults to `RAW_DATASET_FILE`.
    limit : int | None, optional
        Maximum number of records to yield. If None, yields all records.

    Yields
    ------
    dict[str, str]
        Dictionary mapping column names to string values for each record.
    """
    path = get_raw_dataset_path(file_path)
    header = load_raw_header(path)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row

        for idx, row in enumerate(reader):
            if limit is not None and idx >= limit:
                break
            if len(row) == len(header):
                yield dict(zip(header, row, strict=False))
            else:
                # Handle potential width mismatch gracefully
                padded = row + [""] * (len(header) - len(row))
                yield dict(zip(header, padded[: len(header)], strict=False))
