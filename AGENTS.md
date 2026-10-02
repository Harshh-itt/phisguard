# PhishGuard Agent Rules and Operating Invariants

## Mission
Build **PhishGuard**, an explainable, defensive phishing URL classification system that compares a Decision Tree baseline with an Artificial Neural Network (ANN) and exposes the trained model through a secure inference API and modern web interface.

---

## IMPORTANT PERMANENT CONSTRAINTS (NON-NEGOTIABLES)

1. **Defensive Purpose Only**: PhishGuard is strictly a defensive phishing URL detection system. Never create credential-harvesting pages, phishing simulation kits, stealth mechanisms, evasion modules, or credential interception tools.
2. **Static URL Analysis Only**: The system must perform static URL and domain feature extraction without visiting, crawling, or interacting with the target web property.
3. **NEVER Fetch, Crawl, Visit, Render, or Download Submitted URLs**:
   - Server-side URL fetching introduces SSRF (Server-Side Request Forgery), remote exploitation, malware risks, and severe privacy hazards.
   - All URL features must be computed deterministically and statically from the URL string itself.
4. **NEVER Collect Credentials, Passwords, Cookies, Tokens, or Authentication Data**:
   - Treat all user-submitted URLs as untrusted strings.
   - Do not log, store, or transmit sensitive headers, credentials, or session tokens.
5. **EXACTLY TWO Headline Predictive Algorithms**:
   - **Decision Tree**: Basic classical ML baseline.
   - **Artificial Neural Network (ANN)**: Advanced deep learning model (feedforward multilayer perceptron for tabular feature classification).
   - Do not introduce additional predictive ML algorithms (e.g., Random Forest, XGBoost, LightGBM, SVM, CatBoost, Naive Bayes, CNN, RNN/LSTM) unless the project scope is formally amended.
6. **No Preconceived Winner or Invented Claims**:
   - Do not decide in advance that the ANN will outperform the Decision Tree.
   - Do not invent datasets, metrics, accuracy, precision, recall, F1, ROC-AUC, latency, or deployment claims.
   - Report only empirically measured results from controlled experiments.
7. **Strict Phase Boundaries**:
   - Do not implement future phases early. Follow the phase-by-phase build sequence.
   - Phase 0: Project Foundation
   - Phase 1: Dataset Acquisition & Provenance
   - Phase 2: Data Understanding & EDA
   - Phase 3: Data Quality & Leakage Controls
   - Phase 4: Preprocessing & Feature Engineering
   - Phase 5: Train/Validation/Test Strategy (Lock experiment protocol)
   - Phase 6: Decision Tree Baseline
   - Phase 7: Decision Tree Tuning
   - Phase 8: ANN Design & Training
   - Phase 9: ANN Tuning & Regularization
   - Phase 10: Rigorous Model Comparison
   - Phase 11: Explainability
   - Phase 12: Production Inference Pipeline
   - Phase 13: FastAPI Backend
   - Phase 14: React Frontend
   - Phase 15: Testing & QA
   - Phase 16: Docker & Local Production Simulation
   - Phase 17: Cloud Deployment
   - Phase 18: Monitoring & Observability
   - Phase 19: CI/CD & Git Workflow
   - Phase 20: Documentation, Report & Presentation
   - Phase 21: Resume & Interview Preparation
8. **Strict Separation of Training and Inference**:
   - Reusable production feature extraction and inference logic must reside in `src/`.
   - Never copy-paste notebook-only logic directly into serving layers.
   - The inference service must only depend on lightweight runtime dependencies and versioned preprocessor/model artifacts.
   - Raw datasets and heavy training scripts must never be packaged into the production Docker image.
9. **Maintain Reproducibility and Versioned Feature Schemas**:
   - Fix random seeds across data splitting, tree training, and neural network weight initialization.
   - Persist machine-readable metadata with every artifact (`model_version`, `dataset_fingerprint`, `feature_schema_version`, `preprocessing_version`, `metrics`, `timestamp`).
   - Training and inference pipelines must share the exact same feature schema, ordering, and data transformations.
10. **Data Immutability (Never Modify `data/raw`)**:
    - The raw dataset (`data/raw/`) must never be edited, normalized, or mutated in-place by any training or cleaning script.
    - All cleaning and preprocessing must produce versioned outputs in `data/interim/` or `data/processed/`.
11. **Run Tests After Meaningful Changes**:
    - Validate each modification with unit, integration, or contract tests before proceeding.
12. **Inspect Git Diff Before Declaring Phase Complete**:
    - Always review `git status` and `git diff` before concluding any phase. Ensure no secrets, raw data, or unexpected files are staged.

---

## Operating Workflow for Agents
1. **Inspect Repository**: Check current state, existing files, and virtual environment.
2. **Review KI & Rules**: Check AGENTS.md, guidelines, and project specifications.
3. **Formulate a Minimal, Coherent Plan**: Break tasks into precise atomic steps adhering strictly to the current phase.
4. **Implement**: Write clean, modular, production-grade code with appropriate typing and docstrings.
5. **Run Tests / Lint Checks**: Ensure all tests pass.
6. **Inspect Diff**: Verify that only relevant, expected files were created or modified.
7. **Report**: Summarize files changed, commands run, test results, and next phase readiness.

---

## Additional Repository Protection and Approval Rules

### 1. Preserve Existing Work
- Never overwrite, delete, rename, or restructure existing files without explicit user approval.
- Before modifying an existing source file, explain the proposed change and its necessity.
- Prefer creating new documentation files when the task is documentation-only.
- Never perform unrelated refactoring or cleanup.

### 2. Git Safety
- Never execute `git reset --hard`, force-push, or destructive Git operations.
- Never commit or push without explicit user approval.
- Inspect existing Git status before beginning work.
- Do not discard existing user changes.
- Report all staged and unstaged changes accurately.

### 3. Evidence-Based Documentation
- Distinguish verified facts, assumptions, and unresolved questions.
- Never invent feature formulas, dataset statistics, experimental results, or model metrics.
- Cite the available dataset documentation or repository evidence for technical claims.
- Do not claim a feature is reproducible unless its calculation can be established.

### 4. Approval Checkpoints
- Work in small, reviewable tasks.
- Before implementing a phase, present a concise plan and identify affected files.
- Stop after the requested task and report the outcome.
- Wait for user approval before proceeding to the next phase.
- Do not interpret permission to inspect or document as permission to modify source code or train models.

### 5. Beginner-Friendly Communication
- Explain technical decisions in clear language.
- Provide actual commands and their purpose.
- Report actual test and lint results.
- Never claim an operation succeeded without verifying its result.

### 6. Current Authorized Scope
The current authorized work is limited to:

1. Feature provenance audit.
2. Data leakage and validation risk investigation.
3. Final feature selection documentation.

Model training, source-code refactoring, backend/frontend implementation, and deployment are outside this authorization.

---