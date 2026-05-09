# ---- builder ----
FROM python:3.11-slim AS builder

WORKDIR /build
COPY compliance-service/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim

WORKDIR /app

# libpq5 for psycopg2, curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY compliance-service/app/ app/

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8008

HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=20s \
  CMD curl -f http://127.0.0.1:8008/health || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]
