# PhishGuard API Contract Specification

## Endpoints Overview

The FastAPI service exposes three primary endpoints:

### 1. GET `/health`
Returns application health, loaded model status, and feature schema version.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "model_version": "ann-v1",
  "feature_schema_version": "features-v1"
}
```

### 2. GET `/model-info`
Provides details on available models and defaults.

**Response (200 OK):**
```json
{
  "available_models": ["decision_tree", "ann"],
  "default_model": "ann",
  "feature_schema_version": "features-v1"
}
```

### 3. POST `/predict`
Analyzes a submitted URL string using static analysis and returns the classification verdict, model probability, and human-readable risk indicators.

**Request Body:**
```json
{
  "url": "https://example.com/login",
  "model": "ann"
}
```

**Response (200 OK):**
```json
{
  "prediction": "legitimate",
  "probability": 0.96,
  "model": {
    "name": "ann",
    "version": "ann-v1"
  },
  "feature_schema_version": "features-v1",
  "explanation": {
    "risk_level": "low",
    "indicators": [
      {
        "feature": "url_length",
        "direction": "low",
        "message": "URL length is within the learned normal range."
      }
    ]
  },
  "request_id": "req-98745c1a"
}
```
