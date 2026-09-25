# PhishGuard FastAPI Backend

This directory houses the REST API serving layer for PhishGuard, scheduled for full implementation in **Phase 13**.

## Planned Endpoints:
- `GET /health`: Health-check and model artifact status check.
- `GET /model-info`: Supported models (`decision_tree`, `ann`), default selection, and schema versions.
- `POST /predict`: Submit URL string for static classification, confidence score, and risk indicators.

## Architecture & Safety Rules:
- Never visit, fetch, crawl, or render submitted URLs.
- Input validation enforced via Pydantic schemas.
- Structured JSON logging with request IDs.
- CORS restricted to configured frontend origins.
- Inference services utilize pre-loaded, cached model artifacts.
