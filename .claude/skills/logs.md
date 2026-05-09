---
name: logs
description: Stream live logs from Digital Banking services. Usage: /logs api-gateway OR /logs all OR /logs errors
---

# View Service Logs

Stream or inspect logs from Docker Compose services.

## Usage

```
/logs api-gateway         # Tail API Gateway logs
/logs auth-service        # Tail Auth Service logs
/logs transaction-service # Tail Transaction logs
/logs notification-service# Tail Notification Service logs
/logs all                 # Tail all services
/logs errors              # Show only ERROR lines from all services
```

## Commands

### Single Service (live tail)
```bash
cd C:/Veera/AI/agents/DigitalBanking
docker-compose logs -f api-gateway
```

### All Services (live tail)
```bash
docker-compose logs -f
```

### Show Last 100 Lines
```bash
docker-compose logs --tail=100 api-gateway
```

### Filter Errors Only
```bash
docker-compose logs --tail=500 | grep -i "error\|exception\|failed\|refused"
```

### Filter Specific Service Errors
```bash
docker-compose logs api-gateway 2>&1 | grep -i "ERROR\|500\|connection refused" | tail -30
```

### Java Stack Trace (full exception)
```bash
docker-compose logs auth-service 2>&1 | grep -A 20 "Exception\|ERROR"
```

## Log Files by Service

All logs are in Docker container stdout. For persistent logs, redirect:
```bash
docker-compose logs api-gateway > /tmp/gateway.log 2>&1
```

## Useful Patterns

### Watch for Successful Route Match
```bash
docker-compose logs -f api-gateway | grep -i "route\|matched\|forward"
```

### Watch RabbitMQ Events
```bash
docker-compose logs -f notification-service | grep -i "received\|processing\|sent\|queue"
```

### Watch Auth Failures
```bash
docker-compose logs -f auth-service | grep -i "invalid\|failed\|unauthorized\|401"
```

### Watch Transaction Processing
```bash
docker-compose logs -f transaction-service ledger-service | grep -i "created\|processed\|event"
```
