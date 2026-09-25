# PhishGuard Artifacts

This directory stores versioned, reproducible machine learning assets, preprocessors, metadata records, and evaluation reports.

## Subdirectories:
- `models/`: Serialized models (e.g. `decision_tree.joblib`, `ann_model.keras`).
- `preprocessors/`: Serialized preprocessing pipelines and scalers.
- `metadata/`: JSON metadata capturing model versions, training timestamps, git commit hashes, hyperparameters, and feature schemas.
- `reports/`: Evaluation summaries, confusion matrices, ROC curves, and performance plots.

Binary model weights and large artifact binaries are excluded from git via `.gitignore`.
