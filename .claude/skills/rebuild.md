---
name: rebuild
description: Rebuild one or more Digital Banking Docker services from source. Useful after code changes. Usage: /rebuild api-gateway OR /rebuild all
---

# Rebuild Services

Force a fresh Docker build for specific services after code changes, without restarting unaffected services.

## Usage

```
/rebuild api-gateway         # Rebuild and restart API Gateway only
/rebuild auth-service        # Rebuild Auth Service
/rebuild account-service     # Rebuild Account Service
/rebuild transaction-service # Rebuild Transaction Service
/rebuild ledger-service      # Rebuild Ledger Service
/rebuild notification-service # Rebuild Notification Service (Python)
/rebuild digital-banking-ui  # Rebuild Angular frontend
/rebuild all                 # Rebuild everything
```

## Commands

### Single Service
```bash
cd C:/Veera/AI/agents/DigitalBanking
SERVICE=api-gateway   # change this

docker-compose stop $SERVICE
docker-compose rm -f $SERVICE
docker-compose up -d --build $SERVICE

# Wait for health
until docker-compose ps | grep "$SERVICE" | grep "healthy"; do
  sleep 5
  echo "Waiting for $SERVICE..."
done
echo "$SERVICE is healthy!"
```

### All Services (full rebuild)
```bash
cd C:/Veera/AI/agents/DigitalBanking
docker-compose down
docker-compose up -d --build
```

### Force No-Cache Rebuild
```bash
docker-compose build --no-cache api-gateway
docker-compose up -d api-gateway
```

## When to Use

| Changed File | Service to Rebuild |
|-------------|-------------------|
| `api-gateway/src/**` | api-gateway |
| `api-gateway/src/main/java/…/GatewayConfig.java` | api-gateway |
| `auth-service/src/**` | auth-service |
| `account-service/src/**` | account-service |
| `transaction-service/src/**` | transaction-service |
| `ledger-service/src/**` | ledger-service |
| `notification-service/app/**` | notification-service |
| `digital-banking-ui/src/**` | digital-banking-ui |
| `init-db.sql` | all + `docker-compose down -v` first |

## Estimated Build Times

| Service | First Build | Cached |
|---------|------------|--------|
| Java services | 3-5 min | 45-90s |
| Notification (Python) | 2-3 min | 30s |
| Angular UI | 3-4 min | 60s |

## Verify After Rebuild

```bash
docker-compose ps | grep api-gateway
curl -s http://localhost:8000/api/v1/auth/health
```
