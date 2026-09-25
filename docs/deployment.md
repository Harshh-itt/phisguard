# PhishGuard Deployment Specification

## Production Target
- **Compute Platform**: Google Cloud Run (Fully managed serverless container runtime)
- **Container Registry**: Google Artifact Registry
- **Packaging**: Multi-stage Docker image based on `python:3.12-slim`

## Container Architecture
- **Non-Root Execution**: Runs under the dedicated unprivileged user `phishguard`.
- **Minimal Image Footprint**: Excludes training datasets, exploratory notebooks, and compiler toolchains from the final image stage.
- **Healthcheck**: Configured against `GET /health` with 30s intervals and 5s timeout.

## Environment Variable Schema
| Variable | Description | Default |
|---|---|---|
| `ENVIRONMENT` | Target deployment tier (`development`, `staging`, `production`) | `production` |
| `MODEL_DEFAULT` | Default model used if unspecified in request | `ann` |
| `MODEL_ARTIFACT_DIR` | Absolute or relative path to model weights | `/app/artifacts/models` |
| `PREPROCESSOR_ARTIFACT_DIR` | Path to fitted preprocessor pipeline | `/app/artifacts/preprocessors` |
| `ALLOWED_ORIGINS` | Permitted frontend origins for CORS | Required in prod |
| `LOG_LEVEL` | Log filtering level (`INFO`, `WARNING`, `ERROR`) | `INFO` |

## Secret Management
No credentials or private keys are embedded within Docker images or git repositories. All cloud credentials rely on GCP Workload Identity / default service accounts.
