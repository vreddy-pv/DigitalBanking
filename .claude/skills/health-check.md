---
name: health-check
description: Check the health status of all Digital Banking microservices. Tests each service directly and through the API Gateway, then shows a summary. Phase 1 + Phase 2 complete (11 services).
---

# Health Check — All Services

Verifies that all 11 running microservices are healthy and responding correctly.

## What It Tests

1. **Docker status** — all containers running + marked healthy
2. **Direct service health** — hits each service's /health endpoint
3. **API Gateway routing** — sends request through port 8000 to confirm proxy works
4. **Database connectivity** — PostgreSQL health via docker
5. **RabbitMQ** — management API reachable
6. **Phase 2 services** — customer-service, notification-service, analytics-service

## Commands

```bash
cd C:/Veera/AI/agents/DigitalBanking

# Docker health overview (all should show "healthy")
docker-compose ps

# ---- Direct health checks ----

echo "--- Auth Service ---"
curl -s http://localhost:8001/api/v1/auth/health

echo "--- Account Service ---"
curl -s http://localhost:8002/api/v1/accounts/health

echo "--- Transaction Service ---"
curl -s http://localhost:8003/api/v1/transactions/health

echo "--- Ledger Service ---"
curl -s http://localhost:8004/api/v1/ledger/health

echo "--- Customer Service (Phase 2) ---"
curl -s http://localhost:8005/api/v1/customers/health

echo "--- Notification Service (Phase 2) ---"
curl -s http://localhost:8006/health

echo "--- Analytics Service (Phase 2) ---"
curl -s http://localhost:8007/api/v1/analytics/health

echo "--- Angular UI ---"
curl -s -o /dev/null -w "%{http_code}" http://localhost:4200/

echo "--- RabbitMQ ---"
curl -s -u guest:guest http://localhost:15672/api/overview | grep -o '"product":"RabbitMQ"'

# ---- API Gateway routing tests ----

echo "--- API Gateway → Auth ---"
curl -s http://localhost:8000/api/v1/auth/health

echo "--- API Gateway → Account ---"
curl -s http://localhost:8000/api/v1/accounts/health

echo "--- API Gateway → Customer (Phase 2) ---"
curl -s http://localhost:8000/api/v1/customers/health

# ---- Notification stats ----

echo "--- Notification Stats ---"
curl -s http://localhost:8006/api/v1/notifications/stats

# ---- Analytics platform summary ----

echo "--- Analytics Platform Summary ---"
curl -s http://localhost:8007/api/v1/analytics/summary
```

## Expected Output

| Endpoint | Expected |
|----------|----------|
| All Java services `/health` | `"success":true` |
| Customer service `/health` | `"success":true,"data":"UP"` |
| Notification `/health` | `{"status":"healthy"}` |
| Analytics `/health` | `{"status":"healthy","service":"analytics-service"}` |
| Angular UI | HTTP 200 |
| RabbitMQ | `"product":"RabbitMQ"` |
| Notification stats | `{"total_sent":...,"total_pending":...}` |
| Analytics summary | `{"total_transactions":...,"total_volume":...}` |

Docker: all services should show `(healthy)`.

## Common Issues

| Issue | Fix |
|-------|-----|
| Service shows `(unhealthy)` | `docker-compose logs -f <service>` |
| Connection refused | Service not started — `docker-compose up -d <service>` |
| API Gateway 500 | `docker-compose up -d --build api-gateway` |
| RabbitMQ not reachable | Wait 15-20s after startup |
| Customer service 404 | Use `/api/v1/customers/health` NOT `/health` |
| Analytics 404 | Use `/api/v1/analytics/health` NOT `/health` |
| Notifications empty | Normal — SMTP not configured in dev; check `/api/v1/notifications/stats` instead |
