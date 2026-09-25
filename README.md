# PhishGuard: AI-Based Phishing URL Detection System

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Phase](https://img.shields.io/badge/Phase-0%20%7C%20Project%20Foundation-orange.svg)](#development-phases)

> **Status:** Phase 0 — Project Foundation  
> **Headline Models:** Decision Tree (Baseline) vs. Artificial Neural Network (Advanced Deep Learning)

---

## 1. Project Purpose & Overview

**PhishGuard** is an end-to-end, defensive cybersecurity machine learning system designed to detect and classify phishing URLs while providing human-readable explanations. 

Modern cyber adversaries routinely deploy deceptive URLs to compromise credentials, hijack sensitive personal records, and execute financial fraud. Traditional blocklist approaches struggle with zero-hour threats and rapid domain rotation. PhishGuard evaluates URLs using statistical and deep learning models to determine whether a given URL exhibits characteristic malicious patterns—delivering an auditable classification, model confidence/probability, and concrete risk indicators to defenders and end users.

---

## 2. Core Principle: Static URL Analysis Only

A fundamental tenet of PhishGuard's design is **Static URL Analysis**:
- **Zero Network Interaction with Target URLs**: PhishGuard evaluates URLs entirely based on lexical, syntactic, domain, and character-level properties extracted directly from the URL string.
- **Never Fetch, Crawl, Visit, or Render Target Sites**: The system **never** establishes HTTP/HTTPS connections to, crawls, downloads content from, or renders the submitted URL.
- **Security Justification**: Visiting or fetching untrusted URLs introduces catastrophic attack surfaces, including Server-Side Request Forgery (SSRF), remote code execution, exposure of internal network topologies, download of drive-by malware payloads, and exposure to honeypots or tracking pixels. Static analysis guarantees safety, high throughput, zero egress risk, and complete reproducibility.

---

## 3. High-Level Planned Architecture

The PhishGuard architecture is structured into five clean logical tiers with strict decoupling between offline model training and online production serving:

```
[ User Browser / Client ]
            │
            ▼ (HTTPS / JSON)
┌────────────────────────────────────────┐
│        React + Vite Frontend           │
│  - URL Analysis Form                   │
│  - Verdict & Calibrated Risk Display   │
│  - Human-Readable Risk Indicators      │
│  - Decision Tree vs. ANN Comparison UI │
└───────────────────┬────────────────────┘
                    │
                    ▼ (REST API)
┌────────────────────────────────────────┐
│           FastAPI Backend              │
│  - Input Validation & Normalization    │
│  - Rate Limiting Hooks & Request IDs   │
│  - /health, /model-info, /predict      │
│  - Structured JSON Logging             │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│          Inference Service             │
│  - Deterministic URL Feature Extractor │
│  - Preprocessor Pipeline (Shared V1)   │
│  - Decision Tree & ANN Model Runners   │
│  - Explainability & Risk Indicator Svc │
└───────────────────┬────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│           Model Artifacts              │
│  - decision_tree.joblib                │
│  - ann_model.keras                     │
│  - preprocessor.joblib / scaler        │
│  - feature_schema.json                 │
│  - model_metadata.json (Provenance)    │
└────────────────────────────────────────┘
```

### Decoupling Rules:
- **Offline Training**: Data auditing, exploratory data analysis (EDA), feature selection, and training occur in controlled pipelines (`src/` and `notebooks/`).
- **Production Serving**: The FastAPI inference service loads pre-compiled model artifacts once at startup and performs deterministic feature extraction. It **never** retrains models in response to user requests.
- **Artifact Immobility**: Raw datasets are never bundled into the production container image.

---

## 4. Exactly Two Planned Headline ML Algorithms

PhishGuard strictly focuses on an academic and empirical head-to-head evaluation between two model families:

1. **Decision Tree (Baseline)**:
   - *Class*: Classical, interpretable machine learning.
   - *Implementation*: `scikit-learn` `DecisionTreeClassifier`.
   - *Purpose*: Provides a fully transparent, highly inspectable white-box baseline with deterministic decision boundaries and direct feature splits.
2. **Artificial Neural Network / ANN (Advanced)**:
   - *Class*: Deep feedforward neural network / Multilayer Perceptron (MLP) tailored for tabular feature classification.
   - *Implementation*: `TensorFlow / Keras`.
   - *Purpose*: Captures high-dimensional non-linear interactions across lexical and structural URL attributes with regularization (Dropout, Early Stopping).

> **Scientific Neutrality**: No predetermined winner is assumed. Both models are trained on the exact same feature representations, verified against strict data-leakage controls, and evaluated on an identical, sealed holdout test set across accuracy, precision, recall, F1, ROC-AUC, confusion matrix, false-positive rate, model footprint, and inference latency.

---

## 5. Development Phases Roadmap

The project adheres to a 22-phase structured lifecycle:

- **Phase 0: Project Initialization & Foundation** *(Current)* — Repository layout, environment setup, safety rules, CI setup, and test scaffolding.
- **Phase 1: Dataset Acquisition & Provenance** — Acquire UCI PhiUSIIL dataset, establish SHA-256 checksums, and verify schema immutability.
- **Phase 2: Data Understanding & EDA** — Statistical inspection, distribution analysis, correlation matrices, and leakage risk auditing.
- **Phase 3: Data Quality & Leakage Controls** — Removal of training identifiers, cross-split duplicate prevention, and stratified split definition.
- **Phase 4: Preprocessing & Feature Engineering** — Canonical feature schema and deterministic URL feature extraction pipeline.
- **Phase 5: Train/Validation/Test Strategy** — Seal the holdout test set, lock seeds, and establish evaluation protocols.
- **Phase 6: Decision Tree Baseline** — Train and validate the un-tuned baseline tree.
- **Phase 7: Decision Tree Tuning** — Controlled hyperparameter search over depth, split criteria, and leaf nodes.
- **Phase 8: ANN Design & Training** — Feedforward architecture construction, binary cross-entropy loss, and validation monitoring.
- **Phase 9: ANN Tuning & Regularization** — Hyperparameter refinement, dropout tuning, and checkpoint selection.
- **Phase 10: Rigorous Model Comparison** — Unseal holdout test set; measure accuracy, recall, precision, ROC-AUC, latency, and footprint.
- **Phase 11: Explainability** — Deterministic risk indicators derived from observable URL features.
- **Phase 12: Production Inference Pipeline** — Unified runtime service consuming single URLs to structured predictions.
- **Phase 13: FastAPI Backend** — High-performance REST API with `/health`, `/model-info`, and `/predict`.
- **Phase 14: React Frontend** — Modern, responsive user interface with URL inspection and comparison dashboard.
- **Phase 15: Testing & QA** — End-to-end unit, integration, contract, and UI test suites.
- **Phase 16: Docker & Local Production Simulation** — Containerized multi-stage builds and `docker-compose` orchestration.
- **Phase 17: Cloud Deployment** — Cloud Run container deployment with production hardening.
- **Phase 18: Monitoring & Observability** — Structured logging, latency metrics, and privacy-preserving telemetry.
- **Phase 19: CI/CD & Git Workflow** — Automated GitHub Actions test and build pipelines.
- **Phase 20: Documentation & Reports** — Comprehensive architectural and empirical reports.
- **Phase 21: Resume & Evidence Synthesis** — Defensible evidence-based summaries and technical walkthroughs.

---

## 6. Safety and Security Constraints

- **No Credential Handling**: PhishGuard never collects, stores, transmits, or handles credentials, cookies, passwords, or personal identity information.
- **Untrusted Input**: All user inputs are sanitized and length-capped before processing.
- **Privacy Protection**: Server logging records request IDs, latencies, model versions, and feature metrics without logging raw submitted URLs by default.
- **Immutability of Raw Data**: Data located in `data/raw/` is read-only and preserved permanently in its pristine original format.

---

## 7. Current Status: Phase 0 — Project Foundation

Phase 0 establishes the engineering scaffolding:
- Repository directory structure initialized.
- Virtual environment and Python 3.12 compatibility configured.
- Core project metadata defined via `pyproject.toml` and `requirements.txt`.
- Agent operating rules locked in `AGENTS.md`.
- Baseline test suite initialized with `pytest`.
- Docker and container orchestration specifications prepared.
