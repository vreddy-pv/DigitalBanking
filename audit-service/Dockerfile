# Stage 1: Builder — install Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Build deps needed to compile psycopg2 (libpq headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY audit-service/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Runtime deps: libpq5 (postgres client lib) + curl (healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application source
COPY audit-service/app/ app/

# Ensure local pip-installed binaries are on PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8009

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://127.0.0.1:8009/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8009"]
