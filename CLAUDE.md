# CLAUDE.md — Digital Banking Platform

This file provides guidance to Claude Code when working in this repository.

## Project Overview

Production-quality digital banking microservices platform built in 3 phases.
All services run via Docker Compose. No local JDK/Node install required for running — only Docker.

**Repository:** https://github.com/vreddy-pv/DigitalBanking  
**Architecture doc:** `ARCHITECTURE.md`  
**Deployment doc:** `DEPLOYMENT_SUMMARY.md`

---

## Architecture

| Service | Port | Language | Purpose |
|---------|------|----------|---------|
| API Gateway | 8000 | Java 17 / Spring Cloud Gateway | Request routing, CORS |
| Auth Service | 8001 | Java 17 / Spring Boot 3 | JWT auth, user management |
| Account Service | 8002 | Java 17 / Spring Boot 3 | Customer & account lifecycle |
| Transaction Service | 8003 | Java 17 / Spring Boot 3 | Deposits, withdrawals, transfers |
| Ledger Service | 8004 | Java 17 / Spring Boot 3 | Double-entry bookkeeping |
| Customer Service | 8005 | Java 17 / Spring Boot 3 | KYC docs, beneficiaries, preferences |
| Notification Service | 8006 | Python 3.11 / FastAPI | Email/SMS via RabbitMQ events |
| Analytics Service | 8007 | Python 3.11 / FastAPI | CQRS read model, reports |
| **Compliance Service** | **8008** | **Python 3.11 / FastAPI** | **AML/KYC rule engine, risk scoring** *(Phase 3)* |
| **Audit Service** | **8009** | **Python 3.11 / FastAPI** | **Immutable append-only audit trail** *(Phase 3)* |
| PostgreSQL | 5432 | postgres:15-alpine | All service databases |
| RabbitMQ | 5672 / 15672 | rabbitmq:3.12-management | Async event bus |
| Angular UI | 4200 | Angular 17 / Node 18 | Web frontend |
| **Prometheus** | **9090** | **prom/prometheus:v2.47.0** | **Metrics scraping** *(Phase 3)* |
| **Grafana** | **3000** | **grafana/grafana:10.1.0** | **Dashboards & visualization** *(Phase 3)* |

> **Java version**: All Java services compile and run on **Java 17** (set in root `pom.xml`).
> The parent POM sets `java.version=17`, `maven.compiler.source=17`, `maven.compiler.target=17`.
> All Dockerfiles use `eclipse-temurin:17-alpine` (builder) + `eclipse-temurin:17-jre-alpine` (runtime).

### Routing through API Gateway
```
/api/v1/auth/**          → auth-service:8001
/api/v1/accounts/**      → account-service:8002
/api/v1/transactions/**  → transaction-service:8003
/api/v1/ledger/**        → ledger-service:8004
/api/v1/customers/**     → customer-service:8005
/api/v1/analytics/**     → analytics-service:8007
```
**Note:** Notification (8006), Compliance (8008), and Audit (8009) are **not** routed through the gateway — they consume RabbitMQ events or are queried directly.
Analytics (8007) is queried directly (CQRS read model).

---

## Commands

### Start Everything
```bash
docker-compose up -d --build        # Full rebuild + start
docker-compose up -d                # Start (use cached images)
```

### Stop Everything
```bash
docker-compose down                 # Stop, keep volumes
docker-compose down -v              # Stop + wipe all data
```

### Rebuild a Single Service
```bash
docker-compose up -d --build api-gateway
docker-compose up -d --build auth-service
docker-compose up -d --build account-service
docker-compose up -d --build transaction-service
docker-compose up -d --build ledger-service
docker-compose up -d --build customer-service
docker-compose up -d --build notification-service
docker-compose up -d --build analytics-service
docker-compose up -d --build digital-banking-ui
docker-compose up -d --build compliance-service
docker-compose up -d --build audit-service
```

### Check Health
```bash
docker-compose ps                             # All service states
curl http://localhost:8000/api/v1/auth/health # API Gateway → Auth
curl http://localhost:8001/api/v1/auth/health # Auth direct
curl http://localhost:8002/api/v1/accounts/health
curl http://localhost:8003/api/v1/transactions/health
curl http://localhost:8004/api/v1/ledger/health
curl http://localhost:8005/api/v1/customers/health  # Customer Service
curl http://localhost:8006/health                   # Notification Service
curl http://localhost:8007/api/v1/analytics/health  # Analytics Service
curl http://localhost:8008/health                   # Compliance Service (Phase 3)
curl http://localhost:8009/health                   # Audit Service (Phase 3)
curl http://localhost:9090/-/healthy                # Prometheus (Phase 3)
curl http://localhost:3000/api/health               # Grafana (Phase 3)
```

### View Logs
```bash
docker-compose logs -f api-gateway
docker-compose logs -f auth-service
docker-compose logs -f transaction-service
docker-compose logs -f notification-service
```

---

## Key API Flows

### Register + Login
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@bank.com","password":"Pass123!","fullName":"Jane Doe"}'

# Login → get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@bank.com","password":"Pass123!"}'
```

### Create Account (needs Bearer token)
```bash
curl -X POST http://localhost:8000/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"userId":"<USER_ID>","name":"Jane Doe","email":"user@bank.com",
       "phone":"9876543210","dob":"1990-01-15","address":"123 Main St",
       "city":"NYC","state":"NY","zipCode":"10001",
       "pan":"ABCDE1234F","aadhar":"123456789012","accountType":"SAVINGS"}'
```

### Deposit / Withdraw / Transfer
```bash
# Deposit
curl -X POST http://localhost:8000/api/v1/transactions/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"toAccountId":"<ACCOUNT_ID>","amount":1000,"requestId":"req-unique-id","description":"Deposit"}'

# Withdraw
curl -X POST http://localhost:8000/api/v1/transactions/withdraw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"fromAccountId":"<ACCOUNT_ID>","amount":500,"requestId":"req-unique-id","description":"ATM"}'

# Transfer
curl -X POST http://localhost:8000/api/v1/transactions/transfer \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"fromAccountId":"<FROM_ID>","toAccountId":"<TO_ID>","amount":200,"requestId":"req-unique-id","description":"Transfer"}'
```

### Customer Service — KYC & Beneficiaries (Phase 2)
> Routes through API Gateway: `http://localhost:8000/api/v1/customers/...`  
> Direct: `http://localhost:8005/api/v1/customers/...`

```bash
CUSTOMER_ID="<CUSTOMER_ID_FROM_ACCOUNT_REGISTER>"

# Submit KYC document
# documentType: PASSPORT | NATIONAL_ID | DRIVING_LICENSE | PAN_CARD | UTILITY_BILL
curl -X POST http://localhost:8000/api/v1/customers/$CUSTOMER_ID/kyc/documents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"documentType":"PAN_CARD","documentReference":"ABCDE1234F"}'

# Get KYC status summary
curl http://localhost:8000/api/v1/customers/$CUSTOMER_ID/kyc/status \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# List all KYC documents
curl http://localhost:8000/api/v1/customers/$CUSTOMER_ID/kyc/documents \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Add beneficiary
curl -X POST http://localhost:8000/api/v1/customers/$CUSTOMER_ID/beneficiaries \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"beneficiaryAccountId":"<TARGET_ACCOUNT_UUID>","nickname":"Friend"}'

# List beneficiaries
curl http://localhost:8000/api/v1/customers/$CUSTOMER_ID/beneficiaries \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Update preferences
curl -X PUT http://localhost:8000/api/v1/customers/$CUSTOMER_ID/preferences \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"emailNotifications":true,"smsNotifications":false,"currency":"INR","language":"en"}'
```

> **Note:** `CUSTOMER_ID` is the `id` returned from `POST /api/v1/accounts/register` (it's the customer record id, NOT the account id or user id).

### Analytics Service — CQRS Reports (Phase 2)
> Direct only (not through gateway): `http://localhost:8007/api/v1/analytics/...`

```bash
ACCOUNT_ID="<ACCOUNT_UUID>"

# Paginated transaction statement
curl "http://localhost:8007/api/v1/analytics/accounts/$ACCOUNT_ID/statement?page=1&page_size=20"

# Monthly credit/debit summary (default: current month)
curl "http://localhost:8007/api/v1/analytics/accounts/$ACCOUNT_ID/summary?month=2026-05"

# Spending breakdown by transaction type
curl "http://localhost:8007/api/v1/analytics/accounts/$ACCOUNT_ID/spending"

# Ledger trial balance (all GL accounts)
curl "http://localhost:8007/api/v1/analytics/ledger/trial-balance"

# Journal entries for a specific transaction
curl "http://localhost:8007/api/v1/analytics/ledger/journal/<TRANSACTION_ID>"

# Platform-wide statistics
curl "http://localhost:8007/api/v1/analytics/summary"
```

### Notifications (Phase 2)
> Direct only: `http://localhost:8006/api/v1/notifications/...`

```bash
# Query notifications (filter by status, transaction_id, limit)
curl "http://localhost:8006/api/v1/notifications?status=SENT&limit=10"

# Notification stats
curl "http://localhost:8006/api/v1/notifications/stats"

# Get single notification
curl "http://localhost:8006/api/v1/notifications/<NOTIFICATION_ID>"
```

### Compliance Service — AML Alerts & Risk (Phase 3)
> Direct only: `http://localhost:8008/api/v1/compliance/...`
> **Automatically triggers** for any transaction over 50,000 (HIGH_VALUE) or matching AML rules.

```bash
ACCOUNT_ID="<ACCOUNT_UUID>"

# List AML alerts (filter by account, severity, status)
curl "http://localhost:8008/api/v1/compliance/alerts?account_id=$ACCOUNT_ID"
curl "http://localhost:8008/api/v1/compliance/alerts?severity=HIGH&status=PENDING"

# Get single alert
curl "http://localhost:8008/api/v1/compliance/alerts/<ALERT_ID>"

# Review an alert (REVIEWED | CLEARED | ESCALATED)
curl -X PUT "http://localhost:8008/api/v1/compliance/alerts/<ALERT_ID>/review" \
  -H "Content-Type: application/json" \
  -d '{"status":"CLEARED","reviewed_by":"officer@bank.com","review_notes":"False positive"}'

# Customer risk profile (score 0-100, level LOW/MEDIUM/HIGH/CRITICAL)
curl "http://localhost:8008/api/v1/compliance/customers/$ACCOUNT_ID/risk"

# Compliance stats
curl "http://localhost:8008/api/v1/compliance/stats"

# Manual AML check (without waiting for event)
curl -X POST "http://localhost:8008/api/v1/compliance/check" \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"<TXN_ID>","account_id":"<ACCOUNT_ID>","amount":75000,"transaction_type":"DEPOSIT"}'
```

**AML Rules triggered automatically:**
| Rule | Threshold |
|------|-----------|
| HIGH_VALUE_TRANSACTION | amount > 50,000 |
| LARGE_WITHDRAWAL | withdrawal > 25,000 |
| ROUND_AMOUNT | amount is round (multiples of 10,000+) |
| FREQUENT_TRANSACTIONS | 5+ txns in 60 min window |
| RAPID_SUCCESSION | 3+ txns in 10 min window |
| STRUCTURING | 3+ txns between 40,000–49,999 |

### Audit Service — Immutable Audit Trail (Phase 3)
> Direct only: `http://localhost:8009/api/v1/audit/...`
> **Automatically records** every transaction event from RabbitMQ.

```bash
# List audit events (filters: event_type, actor, resource_type, resource_id, start_date, end_date)
curl "http://localhost:8009/api/v1/audit/events?limit=20"
curl "http://localhost:8009/api/v1/audit/events?resource_type=TRANSACTION&limit=10"
curl "http://localhost:8009/api/v1/audit/events?event_type=TRANSACTION_CREATED"

# Get single audit event
curl "http://localhost:8009/api/v1/audit/events/<EVENT_UUID>"

# Get all audit events for a specific resource
curl "http://localhost:8009/api/v1/audit/events/resource/TRANSACTION/<TXN_ID>"

# Audit statistics
curl "http://localhost:8009/api/v1/audit/events/stats"

# Manually create an audit event (admin use)
curl -X POST "http://localhost:8009/api/v1/audit/events" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "ADMIN_ACTION",
    "actor": "admin@bank.com",
    "resource_type": "ACCOUNT",
    "resource_id": "<ACCOUNT_ID>",
    "action": "FREEZE",
    "description": "Account frozen for AML review",
    "source_service": "compliance-service"
  }'
```

**Audit event types:** `TRANSACTION_CREATED`, `USER_REGISTERED`, `ACCOUNT_CREATED`,
`KYC_DOCUMENT_SUBMITTED`, `COMPLIANCE_ALERT_RAISED`, `ADMIN_ACTION`

### Monitoring (Phase 3)
```bash
# Prometheus
open http://localhost:9090                          # Query UI
open http://localhost:9090/targets                  # Scrape targets status

# Grafana (admin/admin)
open http://localhost:3000                          # Dashboard
```

---

## Test Credentials (current Docker session)

```
Email:      testuser@digitalbanking.com
Password:   TestPassword123!
```

> Re-register after `docker-compose down -v` since volumes are wiped.

---

## Docker Build Architecture

All services use **multi-stage Dockerfiles**:

- **Java services** (api-gateway, auth, account, transaction, ledger, customer):
  - Stage 1 (`builder`): `eclipse-temurin:17-alpine` — runs `mvn clean package -DskipTests`
  - Stage 2 (runtime): `eclipse-temurin:17-jre-alpine` — runs `java -jar app.jar`

- **Notification Service**:
  - Stage 1 (`builder`): `python:3.11-slim` — installs dependencies
  - Stage 2 (runtime): `python:3.11-slim` — runs `uvicorn`

- **UI**:
  - Stage 1 (`builder`): `node:18-alpine` — runs `ng build`
  - Stage 2 (runtime): `node:18-alpine` + `serve` — serves from `dist/digital-banking-ui/`

---

## Gateway Configuration

Routes are defined **programmatically** via `GatewayConfig.java` (NOT YAML-only):

```
api-gateway/src/main/java/com/digitalbanking/gateway/config/GatewayConfig.java
```

CORS is configured in `application.yml` for origins `localhost:4200` and `localhost:4201`.

> **Important:** Always use `GatewayConfig.java` for route changes — YAML routes alone are unreliable with environment variable overrides.

---

## Database Databases

Each service has its own PostgreSQL database (single Postgres container):

| Service | Database | User |
|---------|---------|------|
| auth-service | auth_db | postgres |
| account-service | account_db | postgres |
| transaction-service | transaction_db | postgres |
| ledger-service | ledger_db | postgres |
| customer-service | customer_db | customer_user |
| notification-service | notification_db | notification_user |
| analytics-service | read-only: transaction_db + ledger_db | analytics_user (SELECT only) |
| **compliance-service** | **compliance_db** | **compliance_user** |
| **audit-service** | **audit_db** | **audit_user** |

Schema initialized by `init-db.sql` (runs on first container start).
**Important:** If `audit_db`/`compliance_db` don't exist (postgres container already running), create them manually:
```bash
docker exec digital-banking-postgres psql -U postgres -c "CREATE USER audit_user WITH ENCRYPTED PASSWORD 'password';"
docker exec digital-banking-postgres psql -U postgres -c "CREATE DATABASE audit_db;"
docker exec digital-banking-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE audit_db TO audit_user;"
docker exec digital-banking-postgres psql -U postgres -d audit_db -c "GRANT ALL PRIVILEGES ON SCHEMA public TO audit_user;"
```

---

## Event-Driven Architecture

```
Transaction Service → banking.events exchange (routing key: transaction.created)
    ↓ transaction_events queue    → Ledger Service (journal entries)
    ↓ transaction_events queue    → Notification Service (email/SMS)
    ↓ compliance_events queue     → Compliance Service (AML checks)  ← Phase 3
    ↓ audit_events queue          → Audit Service (immutable trail)  ← Phase 3
```

**Each Python service has its OWN dedicated queue** bound to the `banking.events` exchange,
so every service receives every message (fan-out pattern via dedicated queues, not shared queue).

RabbitMQ Management UI: http://localhost:15672 (guest / guest)

---

## Phase Status

- [x] **Phase 1** — Auth, Account, Transaction, Ledger, API Gateway, UI (complete)
- [x] **Phase 2 Week 5** — Notification Service with RabbitMQ (complete)
- [x] **Phase 2 remaining** — Customer Service (8005, KYC/beneficiaries), KYC enrichment in Transaction Service, Analytics Service (8007, CQRS read model) ✅ **complete & verified 2026-05-09**
- [x] **Phase 3** — Compliance Service (8008, AML/risk scoring), Audit Service (8009, immutable trail), Prometheus (9090), Grafana (3000) ✅ **complete & verified 2026-05-09**

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| API Gateway 500 "Connection refused" | Rebuild gateway: `docker-compose up -d --build api-gateway` |
| UI shows directory listing | Check dist path in UI Dockerfile — must be `dist/digital-banking-ui/` |
| Auth returns 401 on valid token | Verify JWT_SECRET env var matches across services |
| CSRF error on POST | SecurityConfig.java must have `.csrf(csrf -> csrf.disable())` |
| Service unhealthy | Check `docker-compose logs -f <service>` |
| DB schema errors | Run `docker-compose down -v && docker-compose up -d --build` |
| RabbitMQ connection refused | Wait for `digital-banking-rabbitmq` to become healthy first |
| Customer-service 404 on KYC endpoints | Paths are `/kyc/documents` and `/kyc/status` — NOT `/kyc-documents` or `/kyc-status` |
| Transaction-service 403 fetching account | account-service SecurityConfig must allow GET `/api/v1/accounts/*` without auth |
| Analytics trial balance empty | Expected if ledger-service `@EventListener` hasn't processed events (in-process only in Phase 1) |
| Notification `recipient` is empty | Means AccountServiceClient got 403 — check account-service SecurityConfig permitAll |
| Python service healthcheck fails (exit 127) | `wget` not in python:3.11-slim — use `curl -f http://127.0.0.1:<port>/<path> \|\| exit 1` |
| Compliance/audit not receiving events | All services shared one queue — each needs own queue bound to exchange via `queue_bind()` |
| audit-service fails with `password auth failed` | `audit_user` not in running Postgres — create manually (init-db.sql only runs first start) |
| `metadata` field causes SQLAlchemy error | Reserved attribute name — use `event_metadata` column alias in ORM model |
| Compliance `timestamp` validation error | Java sends Unix ms int — use `Optional[Any]` for timestamp field in Pydantic schema |
| Audit `/api/v1/audit/stats` 404 | Correct path is `/api/v1/audit/events/stats` |

---

## Architecture Notes — Phase 2 Decisions

### KYC Enrichment Flow
`POST /transactions/deposit` (or withdraw/transfer):
1. Transaction created in `transaction_db`
2. `AccountServiceClient` calls `account-service GET /api/v1/accounts/{id}` (no auth required — internal network)
3. Gets `accountNumber` + `customerId` → calls `GET /api/v1/accounts/customer/{customerId}`
4. Gets `email` + `name` → stored in `TransactionCreatedEvent.recipientEmail` / `customerName`
5. Event published to RabbitMQ → notification-service receives enriched event with real email

### Account-Service Internal Auth Bypass
`SecurityConfig.java` permits `GET /api/v1/accounts/*` and `GET /api/v1/accounts/customer/*` without JWT.
These are read-only lookups on the internal Docker network (port 8002 is internal only in production).

### Analytics Service — CQRS Read Model
- Reads `transaction_db` via `analytics_user` (SELECT only)
- Reads `ledger_db` via `analytics_user` (SELECT only)
- **Never writes** — pure read model
- Uses two separate SQLAlchemy engines
- The `analytics_user` is created in `init-db.sql` with SELECT grants

### Customer Service — `CUSTOMER_ID` vs `ACCOUNT_ID` vs `USER_ID`
- `USER_ID` — returned by `/auth/register` — identifies the auth user
- `CUSTOMER_ID` — returned by `/accounts/register` (the `id` field) — the customer profile id
- `ACCOUNT_ID` — the actual bank account UUID — found in account_db.accounts table
- Customer-service endpoints use `CUSTOMER_ID`, not `ACCOUNT_ID`

---

## Architecture Notes — Phase 3 Decisions

### RabbitMQ Fan-Out via Dedicated Queues
Each Python consumer service has its own dedicated queue bound to `banking.events` exchange:
- `notification_events` — notification-service
- `compliance_events` — compliance-service
- `audit_events` — audit-service

Each listener calls `channel.queue_bind(queue, exchange, routing_key)` so every service gets every event independently. Without dedicated queues, messages round-robin between consumers of the same queue.

### Compliance Service — AML Rule Engine
- 6 configurable rules: HIGH_VALUE, LARGE_WITHDRAWAL, ROUND_AMOUNT, FREQUENT_TX, RAPID_SUCCESSION, STRUCTURING
- Risk score 0–100 calculated from alert history: CRITICAL=30pts, HIGH=20pts, MEDIUM=10pts, LOW=3pts (capped per severity)
- Risk levels: LOW (0-20), MEDIUM (21-50), HIGH (51-80), CRITICAL (81-100)
- All thresholds configurable via environment variables in docker-compose.yml
- Alerts have lifecycle: PENDING → REVIEWED / CLEARED / ESCALATED

### Audit Service — Append-Only Design
- `audit_events` table is strictly append-only — NO UPDATE or DELETE at application level
- ORM column renamed from `metadata` to `event_metadata` (alias="metadata") to avoid SQLAlchemy reserved attribute conflict
- Response schema uses `serialization_alias="metadata"` so JSON output still shows `metadata`
- Event types: TRANSACTION_CREATED, USER_REGISTERED, ACCOUNT_CREATED, KYC_DOCUMENT_SUBMITTED, COMPLIANCE_ALERT_RAISED, ADMIN_ACTION

### Prometheus & Grafana Monitoring
- Java services expose metrics at `/actuator/prometheus` (Spring Boot Actuator)
- Python services expose metrics at `/metrics` (prometheus_client)
- Prometheus config: `monitoring/prometheus.yml` — scrapes all 10+ services
- Grafana auto-provisioned via `monitoring/grafana/datasources/` and `monitoring/grafana/dashboards/`
- Default credentials: admin/admin (Grafana), guest/guest (RabbitMQ)
