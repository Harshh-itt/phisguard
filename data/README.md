# PhishGuard Data Directory Structure

This directory manages the lifecycle of datasets used in the PhishGuard project, strictly observing data immutability and provenance tracking.

## Subdirectories:

- **`raw/`**: Contains raw, pristine dataset downloads (specifically the UCI PhiUSIIL Phishing URL Dataset).
  - **IMMUTABLE RULE**: Files placed in `raw/` must NEVER be modified, formatted, cleaned, or overwritten by any code or human operator.
  - Excluded from version control via `.gitignore`.
- **`interim/`**: Contains intermediate transformed data subsets, feature-selected matrices, or cached data generated during leakage audits and pipeline stages.
- **`processed/`**: Contains final modeling partitions (e.g. train, validation, and sealed test splits) generated strictly by deterministic scripts.

## Data Provenance
- Source: UCI Machine Learning Repository — PhiUSIIL Phishing URL (Website) Dataset
- Instances: 235,795
- Features: 54
- Target: `label` (1 = legitimate, 0 = phishing)
- Raw dataset acquisition is formally conducted in **Phase 1**.
