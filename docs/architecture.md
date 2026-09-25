# PhishGuard Architecture Specification

## 1. System Vision
PhishGuard is a high-assurance, defensive machine learning system for phishing URL detection. It relies strictly on **static URL feature analysis**, comparing a white-box classical baseline (Decision Tree) with an advanced deep learning architecture (Artificial Neural Network).

## 2. Tiered System Architecture

```
┌────────────────────────────────────────────────────────┐
│                      Client Layer                      │
│     React + Vite Single-Page Application (Tailwind CSS)│
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS (JSON)
┌───────────────────────────▼────────────────────────────┐
│                    API Gateway / Serving               │
│              FastAPI Application (Uvicorn ASGI)         │
│  - Request ID Injection                                │
│  - CORS Middleware (Restricted Origins)                │
│  - Pydantic Request/Response Validation                │
│  - Structured JSON Logging                             │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      Inference Core                    │
│                 src.inference.predictor               │
│  - URL Normalization & Syntax Validation               │
│  - Static URL Feature Extraction (Deterministic)       │
│  - Preprocessor Pipeline (StandardScaler / Encoders)   │
│  - Model Execution (Decision Tree / ANN)               │
│  - Risk Indicators & Explanation Generation            │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                   Model & Artifact Store               │
│  - Decision Tree: artifacts/models/decision_tree.joblib│
│  - ANN Model: artifacts/models/ann_model.keras         │
│  - Preprocessor: artifacts/preprocessors/pipe.joblib   │
│  - Schema & Metadata: artifacts/metadata/*.json        │
└────────────────────────────────────────────────────────┘
```

## 3. Separation of Concerns
- **Training Pipeline**: Runs offline in `src/` and `notebooks/`. It ingests immutable raw datasets, applies deterministic cross-split controls, tunes models, and exports versioned artifacts.
- **Inference Runtime**: Ships only runtime dependencies and serialized model artifacts. It has zero knowledge of training code or raw CSV datasets.
- **Client Application**: Consumes the FastAPI REST interface. It contains no predictive weights, feature extractors, or secrets.
