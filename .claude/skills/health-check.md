---
name: health-check
description: Check the health status of all Digital Banking microservices. Tests each service directly and through the API Gateway, then shows a summary table.
---

# Health Check — All Services

Verifies that all running microservices are healthy and responding correctly.

## What It Tests

1. **Docker status** — all containers running + marked healthy
2. **Direct service health** — hits each service's /health endpoint
3. **API Gateway routing** — sends request through port 8000 to confirm proxy works
4. **Database connectivity** — PostgreSQL health via docker
5. **RabbitMQ** — management API reachable

## Commands

```bash
# Docker health overview
docker-compose ps

# Direct health checks
echo "--- Auth Service ---"
curl -s http://localhost:8001/api/v1/auth/health

echo "--- Account Service ---"
curl -s http://localhost:8002/api/v1/accounts/health

echo "--- Transaction Service ---"
curl -s http://localhost:8003/api/v1/transactions/health

echo "--- Ledger Service ---"
curl -s http://localhost:8004/api/v1/ledger/health

echo "--- Customer Service (Phase 2) ---"
curl -s http://localhost:8005/api/v1/customers/health 2>/dev/null || echo "not deployed yet"

echo "--- Notification Service ---"
curl -s http://localhost:8006/health

echo "--- Analytics Service (Phase 2) ---"
curl -s http://localhost:8007/api/v1/analytics/health 2>/dev/null || echo "not deployed yet"

echo "--- Angular UI ---"
curl -s -o /dev/null -w "%{http_code}" http://localhost:4200/

echo "--- RabbitMQ ---"
curl -s -u guest:guest http://localhost:15672/api/overview | grep -o '"product":"RabbitMQ"'

# API Gateway routing test (end-to-end)
echo "--- API Gateway → Auth ---"
curl -s http://localhost:8000/api/v1/auth/health
```

## Expected Output

Every health endpoint should return `"success":true`.  
Angular UI should return HTTP 200.  
Docker status should show `(healthy)` for all services.

## Common Issues

| Issue | Fix |
|-------|-----|
| Service shows `(unhealthy)` | `docker-compose logs -f <service>` |
| Connection refused | Service not started — `docker-compose up -d <service>` |
| API Gateway 500 | Rebuild: `docker-compose up -d --build api-gateway` |
| RabbitMQ not reachable | Wait 15-20s after startup |
