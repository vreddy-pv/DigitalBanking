---
name: rebuild
description: Rebuild one or more Digital Banking Docker services from source. Useful after code changes. Usage: /rebuild api-gateway OR /rebuild all
---

# Rebuild Services

Force a fresh Docker build for specific services after code changes, without restarting unaffected services.

## Usage

```
/rebuild api-gateway          # Rebuild and restart API Gateway only
/rebuild auth-service         # Rebuild Auth Service
/rebuild account-service      # Rebuild Account Service
/rebuild transaction-service  # Rebuild Transaction Service
/rebuild ledger-service       # Rebuild Ledger Service
/rebuild customer-service     # Rebuild Customer Service (Phase 2, Java 17)
/rebuild notification-service # Rebuild Notification Service (Phase 2, Python 3.11)
/rebuild analytics-service    # Rebuild Analytics Service (Phase 2, Python 3.11)
/rebuild compliance-service   # Rebuild Compliance Service (Phase 3, Python 3.11)
/rebuild audit-service        # Rebuild Audit Service (Phase 3, Python 3.11)
/rebuild digital-banking-ui   # Rebuild Angular frontend
/rebuild all                  # Rebuild everything
```

## Commands

### Single Service (recommended — no downtime to other services)
```bash
cd C:/Veera/AI/agents/DigitalBanking
SERVICE=api-gateway   # change this

docker-compose stop $SERVICE
docker-compose rm -f $SERVICE
docker-compose build $SERVICE
docker-compose up -d $SERVICE

# Wait for health
sleep 30
docker-compose ps $SERVICE
```

### All Services (full rebuild)
```bash
cd C:/Veera/AI/agents/DigitalBanking
docker-compose down
docker-compose up -d --build
```

### Force No-Cache Rebuild
```bash
docker-compose build --no-cache customer-service
docker-compose up -d customer-service
```

## When to Rebuild

| Changed File | Service to Rebuild |
|-------------|-------------------|
| `api-gateway/src/**` | api-gateway |
| `api-gateway/src/main/java/…/GatewayConfig.java` | api-gateway |
| `auth-service/src/**` | auth-service |
| `account-service/src/**` | account-service |
| `account-service/src/main/java/…/SecurityConfig.java` | account-service |
| `transaction-service/src/**` | transaction-service |
| `transaction-service/src/main/java/…/client/**` | transaction-service |
| `ledger-service/src/**` | ledger-service |
| `customer-service/src/**` | customer-service |
| `notification-service/app/**` | notification-service |
| `analytics-service/app/**` | analytics-service |
| `compliance-service/app/**` | compliance-service |
| `audit-service/app/**` | audit-service |
| `monitoring/prometheus.yml` | prometheus (restart only) |
| `monitoring/grafana/**` | grafana (restart only) |
| `digital-banking-ui/src/**` | digital-banking-ui |
| `common/src/**` | all Java services (common lib) |
| `init-db.sql` | all + `docker-compose down -v` first |

## Java Version

> **All Java services use `eclipse-temurin:17`** (builder + runtime).
> Set in root `pom.xml`: `java.version=17`, `maven.compiler.source=17`, `maven.compiler.target=17`.
> **Never use 21 in Dockerfiles** — it's inconsistent with the compiled bytecode target.

## Python Version

> **All Python services use `python:3.11-slim`** (Debian-based).
> **Healthchecks must use `curl`**, not `wget` — python:3.11-slim has curl but NOT wget.
> Example: `curl -f http://127.0.0.1:8006/health || exit 1`

## Estimated Build Times

| Service | First Build | Cached |
|---------|------------|--------|
| Java services (api-gateway, auth, account, transaction, ledger, customer) | 3-5 min | 45-90s |
| Notification (Python 3.11) | 2-3 min | 30s |
| Analytics (Python 3.11) | 2-3 min | 30s |
| Compliance (Python 3.11) | 2-3 min | 30s |
| Audit (Python 3.11) | 2-3 min | 30s |
| Angular UI | 3-4 min | 60s |

## Verify After Rebuild

```bash
cd C:/Veera/AI/agents/DigitalBanking

# Check status
docker-compose ps

# Check health endpoint
curl -s http://localhost:8000/api/v1/auth/health
curl -s http://localhost:8005/api/v1/customers/health
curl -s http://localhost:8007/api/v1/analytics/health
```
