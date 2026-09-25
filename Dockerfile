# Multi-stage Dockerfile for PhishGuard Backend Service
# Base stage: official lightweight Python 3.12 image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies if required for builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencies stage: Install Python dependencies
FROM base AS builder

COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production runtime stage
FROM base AS runner

# Create a secure non-root user and group
RUN groupadd -r phishguard && useradd -r -g phishguard -d /app -s /sbin/nologin phishguard

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code and backend service
COPY src/ /app/src/
COPY backend/ /app/backend/
COPY artifacts/ /app/artifacts/

# Set ownership to non-root user
RUN chown -R phishguard:phishguard /app

USER phishguard

EXPOSE 8000

# Health check configured against backend health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
