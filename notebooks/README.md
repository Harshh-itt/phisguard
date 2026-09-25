# PhishGuard Jupyter Notebooks

This directory contains research and exploration notebooks corresponding to sequential project phases.

## Planned Notebooks:
1. `01_data_audit.ipynb` (Phase 1): Data provenance, integrity check, checksum validation.
2. `02_eda.ipynb` (Phase 2): Exploratory data analysis, distributions, correlations, leakage checks.
3. `03_feature_engineering.ipynb` (Phase 4): URL lexical feature extraction and preprocessing experiments.
4. `04_decision_tree.ipynb` (Phases 6–7): Decision Tree baseline, validation, hyperparameter tuning.
5. `05_ann.ipynb` (Phases 8–9): Artificial Neural Network architecture, training, and regularization.
6. `06_model_comparison.ipynb` (Phase 10): Sealed holdout test evaluation and side-by-side comparison.

## Operating Rule:
Notebooks are reserved for scientific exploration and generating visual evidence. All reusable, production-critical logic (such as feature extractors, transformers, and model inference runners) must reside in `src/`. Never copy-paste notebook-only logic directly into the production API.
