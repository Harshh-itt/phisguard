"""Phase 6 execution script: Train and evaluate baseline Decision Tree model.

Trains strictly on data/processed/train.csv using only approved static URL features.
The test set (data/processed/test.csv) remains sealed and untouched.
"""

import csv
import time
from pathlib import Path

from src.config import METADATA_DIR, MODELS_DIR, RANDOM_SEED, TRAIN_DATASET_FILE
from src.evaluation.metrics import format_classification_report
from src.models.decision_tree import (
    load_decision_tree_artifacts,
    run_decision_tree_training_pipeline,
)


def main() -> None:
    """Execute Decision Tree baseline model training and evaluation."""
    print("=" * 60)
    print("PHISHGUARD — PHASE 6: DECISION TREE BASELINE MODEL")
    print("=" * 60)
    print(f"Loading training partition: {TRAIN_DATASET_FILE}")
    if not TRAIN_DATASET_FILE.exists():
        raise FileNotFoundError(
            f"Training dataset not found at {TRAIN_DATASET_FILE}. "
            "Please run scripts/05_split_dataset.py first."
        )

    t0 = time.perf_counter()
    records: list[dict[str, str]] = []
    with open(TRAIN_DATASET_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "URL": row["URL"],
                "Domain": row["Domain"],
                "label": row["label"],
            })
    load_duration = time.perf_counter() - t0
    print(f"Loaded {len(records):,} records in {load_duration:.2f}s.")

    print("\nRunning 5-Fold Domain-Grouped Cross-Validation and Model Fitting...")
    t1 = time.perf_counter()
    model, metadata = run_decision_tree_training_pipeline(
        records,
        random_seed=RANDOM_SEED,
        n_cv_splits=5,
        save_artifacts=True,
        models_dir=MODELS_DIR,
        metadata_dir=METADATA_DIR,
    )
    train_duration = time.perf_counter() - t1
    print(f"Training and CV completed in {train_duration:.2f}s.")

    print("\n" + "=" * 60)
    print("MODEL ARCHITECTURE & COMPLEXITY")
    print("=" * 60)
    print(f"Model:                DecisionTreeClassifier(random_state={RANDOM_SEED})")
    print(f"Tree Max Depth:       {metadata.tree_depth}")
    print(f"Total Nodes:          {metadata.node_count:,}")
    print(f"Training Samples:     {metadata.train_samples_count:,}")
    print(f"Training Domains:     {metadata.train_domains_count:,}")

    print("\n" + "=" * 60)
    print("GINI FEATURE IMPORTANCES")
    print("=" * 60)
    sorted_importances = sorted(
        metadata.feature_importances.items(), key=lambda kv: kv[1], reverse=True
    )
    for feat, imp in sorted_importances:
        print(f"  {feat:<22} : {imp:.4f} ({imp * 100:.1f}%)")

    print("\n" + "=" * 60)
    print("OUT-OF-FOLD DOMAIN-GROUPED CROSS-VALIDATION (ZERO-DAY GENERALIZATION)")
    print("=" * 60)
    print(format_classification_report(metadata.cv_metrics))

    print("\n" + "=" * 60)
    print("FULL TRAINING FIT PERFORMANCE (OVERFITTING ASSESSMENT)")
    print("=" * 60)
    print(format_classification_report(metadata.train_metrics))

    # Verify reload integrity
    loaded_model, loaded_meta = load_decision_tree_artifacts(
        models_dir=MODELS_DIR, metadata_dir=METADATA_DIR
    )
    assert loaded_model.tree_.node_count == model.tree_.node_count

    print("\n" + "=" * 60)
    print("PERSISTED ARTIFACTS VERIFICATION")
    print("=" * 60)
    print(f"Model Binary:  {Path(MODELS_DIR) / 'decision_tree_baseline.joblib'}")
    print(f"Metadata JSON: {Path(METADATA_DIR) / 'decision_tree_baseline_metadata.json'}")
    print("Status: Verified and reloaded successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
