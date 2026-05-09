---
name: stop-all
description: Stop all Digital Banking Docker services. Use --wipe to also delete all database volumes (full reset).
---

# Stop All Digital Banking Services

Gracefully stop all running containers. Optionally wipe all data volumes for a clean slate.

## Usage

```
/stop-all          # Stop containers, keep database data
/stop-all --wipe   # Stop containers AND delete all volumes (fresh restart)
```

## Commands

### Stop Only (keep data)
```bash
cd C:/Veera/AI/agents/DigitalBanking
docker-compose down
```

### Stop + Wipe All Data (full reset)
```bash
cd C:/Veera/AI/agents/DigitalBanking
docker-compose down -v
```

## What Gets Deleted with --wipe

- `postgres_data` volume — all database records
- `rabbitmq_data` volume — all queued messages

> After wipe, re-register users and recreate accounts via the API or UI.

## Verify All Stopped

```bash
docker-compose ps    # Should show no running containers
docker ps            # Double-check
```
