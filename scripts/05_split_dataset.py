"""Phase 5 execution script: Reproducible domain-grouped stratified split.

Partitions the cleaned interim dataset into train.csv and test.csv under data/processed/
with zero domain leakage and preserved class balance.
"""

from src.config import INTERIM_DATASET_FILE, TEST_DATASET_FILE, TRAIN_DATASET_FILE
from src.data.split import split_dataset


def main() -> None:
    """Execute the domain-grouped stratified train/test split."""
    print(f"Splitting interim dataset from: {INTERIM_DATASET_FILE}")
    report = split_dataset()
    print("\n========== PHASE 5 SPLIT REPORT ==========")
    print(f"Total Rows:              {report.total_rows}")
    print(f"Train Rows:              {report.train_rows} ({report.train_ratio:.2%})")
    print(f"Test Rows:               {report.test_rows} ({report.test_ratio:.2%})")
    print(f"Total Unique Domains:    {report.total_domains}")
    print(f"Train Unique Domains:    {report.train_domains_count}")
    print(f"Test Unique Domains:     {report.test_domains_count}")
    print(f"Domain Overlap:          {report.domain_overlap_count} (Must be 0)")
    print(f"Train Class Dist (0/1):  {report.train_class_distribution}")
    print(f"Test Class Dist (0/1):   {report.test_class_distribution}")
    print(f"Train Legit Ratio:       {report.train_legitimate_ratio:.4f}")
    print(f"Test Legit Ratio:        {report.test_legitimate_ratio:.4f}")
    print(f"Random Seed:             {report.random_seed}")
    print("\nOutputs written atomically to:")
    print(f"  Train: {TRAIN_DATASET_FILE}")
    print(f"  Test:  {TEST_DATASET_FILE}")


if __name__ == "__main__":
    main()
