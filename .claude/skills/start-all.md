---
name: start-all
description: Start all Digital Banking microservices via Docker Compose. Waits for every service to become healthy and shows final status.
---

# Start All Digital Banking Services

Start all 8 services (API Gateway, Auth, Account, Transaction, Ledger, Notification, PostgreSQL, RabbitMQ, Angular UI) using Docker Compose.

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

| Service | URL |
|---------|-----|
| Angular UI | http://localhost:4200 |
| API Gateway | http://localhost:8000 |
| Auth Service | http://localhost:8001 |
| Account Service | http://localhost:8002 |
| Transaction Service | http://localhost:8003 |
| Ledger Service | http://localhost:8004 |
| Notification Service | http://localhost:8006 |
| RabbitMQ Management | http://localhost:15672 (guest/guest) |
| PostgreSQL | localhost:5432 (postgres/password) |

## Expected Startup Time

- PostgreSQL & RabbitMQ: ~15s
- Java services (cold build): 3-5 minutes
- Java services (cached): ~60s
- Angular UI: ~45s

## Troubleshooting

If a service stays unhealthy:
```bash
docker-compose logs -f <service-name>
```
