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
| Customer Service | 8005 | Java 17 / Spring Boot 3 | KYC docs, beneficiaries, preferences *(Phase 2)* |
| Notification Service | 8006 | Python 3.11 / FastAPI | Email/SMS via RabbitMQ events |
| Analytics Service | 8007 | Python 3.11 / FastAPI | CQRS read model, reports *(Phase 2)* |
| PostgreSQL | 5432 | postgres:15-alpine | All service databases |
| RabbitMQ | 5672 / 15672 | rabbitmq:3.12-management | Async event bus |
| Angular UI | 4200 | Angular 17 / Node 18 | Web frontend |

> **Java version**: All Java services compile and run on **Java 17** (set in root `pom.xml`).
> The parent POM sets `java.version=17`, `maven.compiler.source=17`, `maven.compiler.target=17`.
> All Dockerfiles use `eclipse-temurin:17-alpine` (builder) + `eclipse-temurin:17-jre-alpine` (runtime).

### Routing through API Gateway
```
/api/v1/auth/**          → auth-service:8001
/api/v1/accounts/**      → account-service:8002
/api/v1/transactions/**  → transaction-service:8003
/api/v1/ledger/**        → ledger-service:8004
/api/v1/customers/**     → customer-service:8005  (Phase 2)
/api/v1/analytics/**     → analytics-service:8007 (Phase 2)
```
**Note:** Customer Service (8005) is routed through the gateway (`/api/v1/customers/**`).
Notification Service (8006) and Analytics Service (8007) are **not** routed through the gateway — they are consumed by events (Notification) or queried directly (Analytics).

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
```

### Check Health
```bash
docker-compose ps                             # All service states
curl http://localhost:8000/api/v1/auth/health # API Gateway → Auth
curl http://localhost:8001/api/v1/auth/health # Auth direct
curl http://localhost:8002/api/v1/accounts/health
curl http://localhost:8003/api/v1/transactions/health
curl http://localhost:8004/api/v1/ledger/health
curl http://localhost:8005/api/v1/customers/health  # Customer Service (Phase 2)
curl http://localhost:8006/health                   # Notification Service
curl http://localhost:8007/api/v1/analytics/health  # Analytics Service (Phase 2)
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

| Service | Database |
|---------|---------|
| auth-service | auth_db |
| account-service | account_db |
| transaction-service | transaction_db |
| ledger-service | ledger_db |
| customer-service | customer_db |
| notification-service | notification_db |
| analytics-service | read-only access to transaction_db + ledger_db (no own DB) |

Schema initialized by `init-db.sql` (runs on first container start).

---

## Event-Driven Architecture

```
Transaction Service → publishes TransactionCreatedEvent → RabbitMQ queue: transaction_events
Ledger Service      ← consumes events and creates journal entries
Notification Service← consumes events and sends email/SMS notifications
```

RabbitMQ Management UI: http://localhost:15672 (guest / guest)

---

## Phase Status

- [x] **Phase 1** — Auth, Account, Transaction, Ledger, API Gateway, UI (complete)
- [x] **Phase 2 Week 5** — Notification Service with RabbitMQ (complete)
- [x] **Phase 2 remaining** — Customer Service (8005, KYC/beneficiaries), KYC enrichment in Transaction Service, Analytics Service (8007, CQRS read model) ✅ **complete & verified 2026-05-09**
- [ ] **Phase 3** — Compliance (AML/KYC, Port 8008), Audit Service (Port 8009), K8s, Prometheus/Grafana

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
