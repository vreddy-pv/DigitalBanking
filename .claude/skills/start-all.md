---
name: start-all
description: Start all Digital Banking microservices via Docker Compose. Waits for every service to become healthy and shows final status. All 3 phases (13 services + Prometheus + Grafana).
---

# Start All Digital Banking Services

Start all services (API Gateway, Auth, Account, Transaction, Ledger, Customer, Notification, Analytics, Compliance, Audit, Prometheus, Grafana, PostgreSQL, RabbitMQ, Angular UI) using Docker Compose.

## Steps

1. Verify Docker is running
2. Run `docker-compose up -d --build` from the project root
3. Wait for each service to become healthy (health checks)
4. Show final service status table
5. Print URLs for each service

## Commands

```bash
# Navigate to project
cd C:/Veera/AI/agents/DigitalBanking

# Build and start all services
docker-compose up -d --build

# Wait for all services to be healthy
until docker-compose ps | grep -v "healthy\|postgres\|rabbitmq" | grep -q "(health"; do sleep 5; done

# Show final status
docker-compose ps
```

## Service URLs After Start

| Service | URL | Notes |
|---------|-----|-------|
| Angular UI | http://localhost:4200 | Web frontend |
| API Gateway | http://localhost:8000 | All user requests |
| Auth Service | http://localhost:8001 | Direct only |
| Account Service | http://localhost:8002 | Direct only |
| Transaction Service | http://localhost:8003 | Direct only |
| Ledger Service | http://localhost:8004 | Direct only |
| Customer Service | http://localhost:8005 | Phase 2 |
| Notification Service | http://localhost:8006 | Phase 2, direct only |
| Analytics Service | http://localhost:8007 | Phase 2, direct only |
| Compliance Service | http://localhost:8008 | Phase 3, direct only |
| Audit Service | http://localhost:8009 | Phase 3, direct only |
| Prometheus | http://localhost:9090 | Phase 3 |
| Grafana | http://localhost:3000 | Phase 3, admin/admin |
| RabbitMQ Management | http://localhost:15672 | guest/guest |
| PostgreSQL | localhost:5432 | postgres/password |

## Expected Startup Time

- PostgreSQL & RabbitMQ: ~15s
- Java services (cold build): 3-5 minutes each
- Java services (cached): ~60s each
- Python services (cold build): 2-3 minutes
- Python services (cached): ~30s
- Angular UI: ~45s

## Troubleshooting

If a service stays unhealthy:
```bash
docker-compose logs -f <service-name>
```
