# Machine Learning Pipeline Architecture

## 1. Overview
The PhishGuard machine learning pipeline enforces strict separation between offline model training and online inference. It guarantees end-to-end reproducibility, eliminates data leakage, and conducts a scientific comparison between two headline models.

## 2. Headline Model Families
1. **Decision Tree (Baseline)**:
   - Implementation: `sklearn.tree.DecisionTreeClassifier`
   - Role: Fast, inspectable, rule-based baseline.
   - Evaluation: Feature importance, branch depth analysis, confusion matrix.
2. **Artificial Neural Network (Advanced)**:
   - Implementation: `tensorflow.keras.models.Sequential`
   - Architecture: Multilayer Perceptron (MLP) with Dense layers, ReLU activations, Dropout, and Sigmoid binary output.
   - Role: Non-linear tabular feature synthesis.

## 3. Data Flow & Leakage Controls
- **Identifier Exclusion**: Non-predictive metadata (e.g. `FILENAME`, database indices) are purged before training.
- **Stratified Partitioning**: Deterministic splitting (Train / Validation / Test) ensuring balanced class ratios.
- **Holdout Test Set Sealing**: The holdout test set is sealed until Phase 10; all hyperparameter tuning is conducted solely on training/validation folds.
- **Transformation Fitting**: All scalers and transformers are fit strictly on the training partition and persisted to `artifacts/preprocessors/`.
