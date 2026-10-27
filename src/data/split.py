"""Domain-grouped stratified train/test dataset splitting for PhishGuard.

Implements zero-leakage, domain-isolated, and class-stratified partitioning
using StratifiedGroupKFold on the cleaned interim dataset.
"""

import csv
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel, Field
from sklearn.model_selection import StratifiedGroupKFold

from src.config import (
    INTERIM_DATASET_FILE,
    RANDOM_SEED,
    SPLIT_GROUP_COLUMN,
    SPLIT_N_SPLITS,
    TARGET_COLUMN,
    TEST_DATASET_FILE,
    TRAIN_DATASET_FILE,
)


class SplitReport(BaseModel):
    """Structured audit report produced by the dataset split pipeline."""

    total_rows: int = Field(description="Total records in input dataset")
    train_rows: int = Field(description="Count of records in training partition")
    test_rows: int = Field(description="Count of records in test partition")
    train_ratio: float = Field(description="Proportion of records in training partition")
    test_ratio: float = Field(description="Proportion of records in test partition")
    total_domains: int = Field(description="Total distinct domains in input dataset")
    train_domains_count: int = Field(description="Distinct domains in training partition")
    test_domains_count: int = Field(description="Distinct domains in test partition")
    domain_overlap_count: int = Field(
        default=0,
        description="Number of overlapping domains between train and test (must be 0)",
    )
    train_class_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Class counts in training partition",
    )
    test_class_distribution: dict[str, int] = Field(
        default_factory=dict,
        description="Class counts in test partition",
    )
    train_legitimate_ratio: float = Field(
        description="Proportion of legitimate class in train partition"
    )
    test_legitimate_ratio: float = Field(
        description="Proportion of legitimate class in test partition"
    )
    random_seed: int = Field(description="Random seed used for reproducibility")


def validate_split(
    train_records: Sequence[dict[str, Any]],
    test_records: Sequence[dict[str, Any]],
    group_column: str = SPLIT_GROUP_COLUMN,
    label_column: str = TARGET_COLUMN,
) -> None:
    """Validate data integrity, domain isolation, and class presence across partitions.

    Raises:
        ValueError: If partitions are empty, domains overlap, required columns
            are missing, or any class is missing from either partition.
    """
    if not train_records:
        raise ValueError("Training partition cannot be empty.")
    if not test_records:
        raise ValueError("Test partition cannot be empty.")

    train_domains: set[str] = set()
    train_labels: set[str] = set()
    for idx, rec in enumerate(train_records):
        if not isinstance(rec, dict):
            raise TypeError(f"Train record at index {idx} must be a dictionary.")
        if group_column not in rec or label_column not in rec:
            raise ValueError(
                f"Train record at index {idx} missing required "
                f"column '{group_column}' or '{label_column}'."
            )
        domain = str(rec[group_column]).strip().lower()
        if not domain:
            raise ValueError(f"Train record at index {idx} has empty domain.")
        label = str(rec[label_column]).strip()
        if label not in {"0", "1"}:
            raise ValueError(f"Invalid label '{label}' in train record {idx}.")
        train_domains.add(domain)
        train_labels.add(label)

    test_domains: set[str] = set()
    test_labels: set[str] = set()
    for idx, rec in enumerate(test_records):
        if not isinstance(rec, dict):
            raise TypeError(f"Test record at index {idx} must be a dictionary.")
        if group_column not in rec or label_column not in rec:
            raise ValueError(
                f"Test record at index {idx} missing required "
                f"column '{group_column}' or '{label_column}'."
            )
        domain = str(rec[group_column]).strip().lower()
        if not domain:
            raise ValueError(f"Test record at index {idx} has empty domain.")
        label = str(rec[label_column]).strip()
        if label not in {"0", "1"}:
            raise ValueError(f"Invalid label '{label}' in test record {idx}.")
        test_domains.add(domain)
        test_labels.add(label)

    overlap = train_domains & test_domains
    if overlap:
        raise ValueError(
            f"Domain isolation violated: {len(overlap)} domain(s) appear in both "
            f"partitions: {sorted(list(overlap))[:5]}"
        )

    if train_labels != {"0", "1"}:
        raise ValueError(
            f"Training partition must contain both classes '0' and '1', found: {train_labels}"
        )
    if test_labels != {"0", "1"}:
        raise ValueError(
            f"Test partition must contain both classes '0' and '1', found: {test_labels}"
        )


def split_records(
    records: list[dict[str, Any]],
    group_column: str = SPLIT_GROUP_COLUMN,
    label_column: str = TARGET_COLUMN,
    n_splits: int = SPLIT_N_SPLITS,
    random_seed: int = RANDOM_SEED,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], SplitReport]:
    """Split in-memory records into domain-isolated, stratified train and test partitions.

    Uses StratifiedGroupKFold to group URLs by domain while maintaining class balance.
    Fold 0 is assigned as the holdout test set (~20%), with the remaining folds
    combined into the training set (~80%).
    """
    if not records:
        raise ValueError("Input records cannot be empty.")

    domains: list[str] = []
    labels: list[int] = []

    for idx, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise TypeError(f"Record at index {idx} must be a dictionary.")
        if group_column not in rec or label_column not in rec:
            raise ValueError(
                f"Record at index {idx} missing required "
                f"column '{group_column}' or '{label_column}'."
            )
        domain = str(rec[group_column]).strip().lower()
        if not domain:
            raise ValueError(f"Record at index {idx} has empty domain.")
        label_val = str(rec[label_column]).strip()
        if label_val not in {"0", "1"}:
            raise ValueError(f"Invalid label '{label_val}' at index {idx}. Expected '0' or '1'.")

        domains.append(domain)
        labels.append(int(label_val))

    unique_domains = set(domains)
    if len(unique_domains) < n_splits:
        raise ValueError(
            f"Number of unique domains ({len(unique_domains)}) must be >= n_splits ({n_splits})."
        )

    unique_classes, class_counts = np.unique(labels, return_counts=True)
    if len(unique_classes) < 2:
        raise ValueError("Dataset must contain at least two target classes (0 and 1).")
    for cls, cnt in zip(unique_classes, class_counts, strict=False):
        if cnt < n_splits:
            raise ValueError(
                f"Class '{cls}' has {cnt} member(s), which is fewer than n_splits ({n_splits})."
            )

    y = np.array(labels, dtype=np.int64)
    groups = np.array(domains)
    x_dummy = np.zeros(len(y), dtype=np.int8)

    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    train_idx, test_idx = next(sgkf.split(x_dummy, y, groups))

    train_records = [records[i] for i in train_idx]
    test_records = [records[i] for i in test_idx]

    validate_split(
        train_records,
        test_records,
        group_column=group_column,
        label_column=label_column,
    )

    train_0 = int(np.sum(y[train_idx] == 0))
    train_1 = int(np.sum(y[train_idx] == 1))
    test_0 = int(np.sum(y[test_idx] == 0))
    test_1 = int(np.sum(y[test_idx] == 1))

    total = len(records)
    report = SplitReport(
        total_rows=total,
        train_rows=len(train_records),
        test_rows=len(test_records),
        train_ratio=round(len(train_records) / total, 4),
        test_ratio=round(len(test_records) / total, 4),
        total_domains=len(unique_domains),
        train_domains_count=len(set(groups[train_idx])),
        test_domains_count=len(set(groups[test_idx])),
        domain_overlap_count=0,
        train_class_distribution={"0": train_0, "1": train_1},
        test_class_distribution={"0": test_0, "1": test_1},
        train_legitimate_ratio=round(train_1 / len(train_records), 4),
        test_legitimate_ratio=round(test_1 / len(test_records), 4),
        random_seed=random_seed,
    )
    return train_records, test_records, report


def split_dataset(
    input_file: Path | str | None = None,
    train_output_file: Path | str | None = None,
    test_output_file: Path | str | None = None,
    group_column: str = SPLIT_GROUP_COLUMN,
    label_column: str = TARGET_COLUMN,
    n_splits: int = SPLIT_N_SPLITS,
    random_seed: int = RANDOM_SEED,
) -> SplitReport:
    """Read cleaned dataset, partition into train/test, and atomically persist CSV outputs."""
    in_path = Path(input_file) if input_file else INTERIM_DATASET_FILE
    train_path = Path(train_output_file) if train_output_file else TRAIN_DATASET_FILE
    test_path = Path(test_output_file) if test_output_file else TEST_DATASET_FILE

    if not in_path.exists():
        raise FileNotFoundError(f"Input interim dataset not found at: {in_path}")
    if in_path.resolve() in {train_path.resolve(), test_path.resolve()}:
        raise ValueError("Input and output dataset paths must differ.")
    if train_path.resolve() == test_path.resolve():
        raise ValueError("Train and test output paths must differ.")

    records: list[dict[str, Any]] = []
    header: list[str] = []
    with open(in_path, encoding="utf-8", newline="") as fin:
        reader = csv.reader(fin)
        try:
            raw_header = next(reader)
        except StopIteration as exc:
            raise ValueError("Input dataset is empty.") from exc
        header = [col.strip() for col in raw_header]
        if group_column not in header or label_column not in header:
            raise ValueError(
                f"Input dataset missing required columns '{group_column}' or '{label_column}'."
            )

        for row in reader:
            if len(row) == len(header):
                records.append(dict(zip(header, row, strict=False)))

    train_records, test_records, report = split_records(
        records=records,
        group_column=group_column,
        label_column=label_column,
        n_splits=n_splits,
        random_seed=random_seed,
    )

    train_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.parent.mkdir(parents=True, exist_ok=True)

    temp_train: Path | None = None
    temp_test: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=train_path.parent,
            prefix=f".{train_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as f_train:
            temp_train = Path(f_train.name)
            writer = csv.DictWriter(f_train, fieldnames=header)
            writer.writeheader()
            writer.writerows(train_records)

        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=test_path.parent,
            prefix=f".{test_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as f_test:
            temp_test = Path(f_test.name)
            writer = csv.DictWriter(f_test, fieldnames=header)
            writer.writeheader()
            writer.writerows(test_records)

        os.replace(temp_train, train_path)
        temp_train = None
        os.replace(temp_test, test_path)
        temp_test = None
    finally:
        if temp_train is not None:
            temp_train.unlink(missing_ok=True)
        if temp_test is not None:
            temp_test.unlink(missing_ok=True)

    return report
