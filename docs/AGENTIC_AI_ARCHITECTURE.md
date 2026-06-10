# Agentic AI Architecture — Digital Banking Platform

**Status**: Planned — Phase 4 (Post Phase 1–3 Foundation)  
**Owner**: Platform Architecture Team  
**Last Updated**: 2026-06-10

---

## 1. Overview

A **hierarchical multi-agent AI system** built on top of the existing Digital Banking microservices foundation. Claude acts as the reasoning core at every layer: the Orchestrator manages intent and session context, while specialist agents own domain knowledge and tool execution for their respective product lines.

```
                        ┌──────────────────────────┐
                        │     Banking Customer      │
                        │   Web · Mobile · Chat     │
                        └────────────┬─────────────┘
                                     │ JWT-authenticated request
                                     ▼
                        ┌──────────────────────────┐
                        │    Orchestrator Agent     │  :8005
                        │  Intent · Auth · Memory   │
                        └──────┬──────────┬─────────┘
                               │          │          │
                 CASA intent   │  ML intent│ USL intent
                               ▼          ▼          ▼
                ┌──────────┐ ┌──────────┐ ┌──────────┐
                │   CASA   │ │    ML    │ │   USL    │
                │  Agent   │ │  Agent   │ │  Agent   │
                └──────────┘ └──────────┘ └──────────┘
                        │         │           │
                        └─────────┴───────────┘
                                  │ tool calls
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Auth :8001   Account :8002   Txn :8003
              Ledger :8004   Complaint :8006   Loan :8007
```

---

## 2. Agent Definitions

### 2.1 Orchestrator Agent

**Port**: `8005/agents/orchestrate`  
**Tech**: Python FastAPI + Anthropic SDK (`claude-sonnet-4-6`)

**Responsibilities**:
- Classify intent from free-text user input to one of: `CASA`, `ML`, `USL`, `GENERAL`
- Validate JWT token against Auth Service (:8001) before dispatching
- Maintain 10-turn conversation window in Redis per `user_id`
- Pass relevant prior context to specialist agents
- Handle fallback: low-confidence intents return a clarifying question
- Human handoff: escalate to live agent if intent confidence < 0.6 after 2 retries

**System Prompt Excerpt**:
```
You are a banking assistant for VRGT Digital Bank. Your role is to understand
the customer's intent and route them to the correct specialist. Always greet
the customer by name (retrieved from JWT claims). Never reveal internal
system details. If you cannot handle a request, say so clearly.
```

---

### 2.2 CASA Agent (Current Account & Savings Account)

**Route**: `8005/agents/casa`  
**Products Covered**: Current Accounts, Savings Accounts, Fixed Deposits

#### Tools

| Tool | Method | Backend | Description |
|------|--------|---------|-------------|
| `get_account_balance` | GET | Account Service :8002 | Returns available + ledger balance |
| `get_recent_transactions` | GET | Transaction Service :8003 | Last N transactions (default 10) |
| `get_transaction_detail` | GET | Transaction Service :8003 + Ledger :8004 | Single transaction with GL journal entry |
| `raise_complaint` | POST | Complaint Service :8006 | Enters complaint pipeline, returns `ticket_id` |
| `get_complaint_status` | GET | Complaint Service :8006 | Live status of an existing complaint |

#### Sample Dialogue Flow

```
User:  "What's my balance?"
CASA:  get_account_balance(account_id) → "Your savings account balance is ₹45,230.00
        (Available: ₹45,230 | Ledger: ₹45,230)"

User:  "Show me my last 5 transactions"
CASA:  get_recent_transactions(account_id, limit=5) → formatted list

User:  "I don't recognise the ₹2,500 charge on June 8th"
CASA:  get_transaction_detail(txn_id) → confirms details
        → raise_complaint(txn_id, type=UNAUTHORIZED, description="Customer does not
           recognise merchant XYZ charge of ₹2,500 on 2026-06-08")
        → "I've raised complaint ticket #CMP-20260610-0042. You'll receive an update
           within 24 hours."
```

---

### 2.3 ML Agent (Mortgage Loans)

**Route**: `8005/agents/ml`  
**Products Covered**: Home Loan, Loan Against Property, Construction Loan

#### Tools

| Tool | Backend | Description |
|------|---------|-------------|
| `get_loan_account` | Loan Service :8007 | Outstanding principal, disbursed amount, tenure |
| `get_emi_schedule` | Loan Service :8007 | Full amortisation schedule |
| `get_prepayment_quote` | Loan Service :8007 | Prepayment penalty + net payoff amount |
| `get_interest_certificate` | Loan Service :8007 | Annual provisional / actual certificate |
| `raise_emi_dispute` | Complaint Service :8006 | Late charge dispute, mis-posting complaint |
| `request_statement` | Loan Service :8007 | Statement of account for given date range |

---

### 2.4 USL Agent (Unsecured Loans)

**Route**: `8005/agents/usl`  
**Products Covered**: Personal Loan, Credit Card, Overdraft

#### Tools

| Tool | Backend | Description |
|------|---------|-------------|
| `get_loan_balance` | Loan Service :8007 | Outstanding + accrued interest |
| `get_statement` | Loan Service :8007 | Monthly / date-range statement |
| `get_payment_due` | Loan Service :8007 | Next due date, minimum payment, total due |
| `get_credit_limit` | Loan Service :8007 | Available credit on revolving products |
| `raise_dispute` | Complaint Service :8006 | Unauthorized charge, billing error |
| `request_credit_limit_review` | Loan Service :8007 | Initiate limit enhancement request |

---

## 3. Complaint Pipeline

All three specialist agents feed into a unified five-stage pipeline managed by the **Complaint Service** (:8006).

```
Stage 1 — ACCEPT
  Agent validates complaint (transaction must exist, account must belong to user)
  Complaint Service creates record with status=ACCEPTED
  Returns ticket_id to customer immediately (< 2 seconds SLA)

Stage 2 — INVESTIGATE (automated, async, within 5 min)
  Investigation Agent runs:
    ✓ Transaction metadata check (channel, device fingerprint, IP geolocation)
    ✓ Velocity rule check (frequency of similar transactions)
    ✓ Fraud scoring model (ML model, threshold: 0.75 = HIGH risk)
    ✓ Historical complaint pattern for this customer
  Generates preliminary_finding: { risk_level: LOW|MEDIUM|HIGH, recommended_action }
  Updates complaint record with findings

Stage 3 — NOTIFY OPS
  Complaint Service publishes TransactionComplaintEvent to RabbitMQ exchange: complaints
  Event payload: { ticket_id, account_id, txn_id, risk_level, preliminary_finding }
  Ops Dashboard consumes event → assigns to analyst queue
  SLA timers applied:
    FRAUD (HIGH risk):   4-hour resolution SLA
    DISPUTE (MEDIUM):   24-hour resolution SLA
    ERROR (LOW):        48-hour resolution SLA

Stage 4 — TRACK
  Complaint Service exposes GET /complaints/{ticket_id} for status polling
  Redis pub/sub pushes status change events to Orchestrator
  Customer queries ("any update on my complaint?") return live status without DB hit

Stage 5 — RESOLVE
  Ops analyst marks outcome: RESOLVED | ESCALATED | REJECTED
  If RESOLVED with refund:
    Complaint Service calls Transaction Service → creates REVERSAL transaction
    Ledger Service creates offsetting double-entry journal
  Customer notified via registered channel (in-app + email/SMS via Notification Service :8008)
```

---

## 4. New Services to Build

| Service | Port | Tech | Depends On |
|---------|------|------|-----------|
| `ai-agent-service` | 8005 | Python FastAPI + Anthropic SDK | Auth, Account, Transaction, Ledger, Complaint, Loan |
| `complaint-service` | 8006 | Spring Boot 3 + PostgreSQL | Transaction, Ledger, Notification, RabbitMQ |
| `loan-service` | 8007 | Spring Boot 3 + PostgreSQL | Account, Ledger |

Existing services consumed as-is:
- Auth Service :8001 — JWT validation on every agent request
- Account Service :8002 — customer and account data
- Transaction Service :8003 — transaction records and history
- Ledger Service :8004 — GL journal entries and balances
- Notification Service :8008 — email/SMS/push delivery (Phase 2)

---

## 5. Technology Stack

| Concern | Choice | Reason |
|---------|--------|--------|
| LLM | `claude-sonnet-4-6` | Tool use, extended thinking, low latency |
| Agent runtime | Python FastAPI + `anthropic` SDK | Async tool dispatch, streaming responses |
| Session memory | Redis | Sub-millisecond context read per turn |
| Complaint persistence | PostgreSQL | ACID guarantees for audit trail |
| Event bus | RabbitMQ (existing) | Already in docker-compose; zero new infra |
| Auth | JWT via Auth Service :8001 | Consistent with platform standard |
| Container | Docker Compose (extend existing) | Add 3 new service definitions |

---

## 6. `ai-agent-service` Directory Structure

```
ai-agent-service/
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── agents/
│   │   ├── orchestrator.py      # Intent classification, routing
│   │   ├── casa_agent.py        # CASA tools + conversation logic
│   │   ├── ml_agent.py          # Mortgage loan tools
│   │   └── usl_agent.py         # Unsecured loan tools
│   ├── tools/
│   │   ├── account_tools.py     # Wraps Account Service REST calls
│   │   ├── transaction_tools.py # Wraps Transaction Service REST calls
│   │   ├── complaint_tools.py   # Wraps Complaint Service REST calls
│   │   └── loan_tools.py        # Wraps Loan Service REST calls
│   ├── memory/
│   │   └── redis_memory.py      # Conversation window management
│   ├── auth/
│   │   └── jwt_validator.py     # Validates JWT against Auth Service
│   └── config.py                # Environment-driven config
├── tests/
│   ├── test_orchestrator.py
│   ├── test_casa_agent.py
│   └── test_complaint_flow.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 7. Tool Definition Pattern (Anthropic SDK)

```python
# tools/transaction_tools.py
TRANSACTION_TOOLS = [
    {
        "name": "get_recent_transactions",
        "description": "Retrieve the most recent transactions for a bank account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "The UUID of the account."
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of transactions to return (1–50). Defaults to 10.",
                    "default": 10
                }
            },
            "required": ["account_id"]
        }
    },
    {
        "name": "get_transaction_detail",
        "description": "Retrieve full detail for a single transaction including GL journal entry.",
        "input_schema": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "string",
                    "description": "The UUID of the transaction."
                }
            },
            "required": ["transaction_id"]
        }
    }
]
```

---

## 8. Complaint Service — Database Schema

```sql
CREATE TABLE complaints (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id       VARCHAR(30) UNIQUE NOT NULL,      -- e.g. CMP-20260610-0042
    account_id      UUID NOT NULL,
    transaction_id  UUID,
    product_line    VARCHAR(10) NOT NULL,              -- CASA | ML | USL
    complaint_type  VARCHAR(20) NOT NULL,              -- UNAUTHORIZED | DISPUTE | FRAUD | ERROR
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'ACCEPTED',
    risk_level      VARCHAR(10),                       -- LOW | MEDIUM | HIGH
    preliminary_finding JSONB,
    ops_analyst_id  UUID,
    resolution      TEXT,
    outcome         VARCHAR(20),                       -- RESOLVED | ESCALATED | REJECTED
    sla_deadline    TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_complaints_account_id ON complaints (account_id);
CREATE INDEX idx_complaints_status     ON complaints (status);
CREATE INDEX idx_complaints_created_at ON complaints (created_at DESC);
```

---

## 9. Implementation Phases

| Phase | Scope | Estimated Effort |
|-------|-------|-----------------|
| **Phase 4.1** | Orchestrator + CASA read tools (balance, transactions, detail) | 2 weeks |
| **Phase 4.2** | CASA complaint flow (raise, investigate, notify ops, track) + Complaint Service | 2 weeks |
| **Phase 4.3** | ML Agent + USL Agent + Loan Service stub data | 2 weeks |
| **Phase 4.4** | Investigation Agent (fraud scoring, pattern analysis), SLA engine, ops dashboard integration | 2 weeks |

**Total estimated effort**: 8 weeks (parallel work possible between backend services and agent logic)

---

## 10. Security Considerations

- Every agent request validates the JWT via Auth Service before executing any tool
- Tool calls are scoped: agents can only access accounts belonging to the authenticated `user_id`
- All agent conversations are logged to the Audit Service (:8009) for compliance
- No PII is stored in Redis — only `account_id` references and message turn metadata
- Claude system prompts never expose internal service URLs, ports, or error details to users
- Complaint payloads are treated as sensitive data (encrypted at rest in PostgreSQL)

---

## 11. RabbitMQ Event Schema

```json
// Exchange: complaints  |  Routing key: complaint.created
{
  "event_type": "TransactionComplaintEvent",
  "ticket_id": "CMP-20260610-0042",
  "account_id": "123e4567-e89b-12d3-a456-426614174000",
  "transaction_id": "abc12345-...",
  "product_line": "CASA",
  "complaint_type": "UNAUTHORIZED",
  "risk_level": "HIGH",
  "preliminary_finding": {
    "fraud_score": 0.87,
    "triggered_rules": ["VELOCITY_BREACH", "UNKNOWN_MERCHANT"],
    "recommended_action": "FREEZE_AND_INVESTIGATE"
  },
  "sla_deadline": "2026-06-10T14:30:00Z",
  "created_at": "2026-06-10T10:30:00Z"
}
```

---

## 12. Open Questions / Future Enhancements

- **Proactive alerts**: Push spending anomaly notifications to customers before they ask
- **Multi-language support**: Hindi, Tamil, Telugu via Claude's multilingual capability
- **Voice channel**: Integrate with IVR via speech-to-text → Orchestrator → text-to-speech
- **Cross-agent context**: A customer with both CASA and ML products should get unified responses
- **Feedback loop**: Complaint resolution outcomes feed back into fraud scoring model training
