# Digital Banking Platform - Architecture & Design Decisions

## 🏛️ System Architecture

### Phase 1: Foundation MVP (Weeks 1-4)

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (8000)                          │
│                  Spring Cloud Gateway                            │
│  Routes: /auth/* → 8001, /accounts/* → 8002, /transactions* → 8003│
└──────┬──────────────────┬──────────────────┬────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
   ┌────────────┐   ┌─────────────┐   ┌──────────────┐
   │Auth Service│   │Account Svc  │   │Transaction   │
   │(8001)      │   │(8002)       │   │Service(8003) │
   │            │   │             │   │              │
   │- JWT Auth  │   │- Customers  │   │- Deposits    │
   │- User Mgmt │   │- Accounts   │   │- Withdrawals │
   │- Tokens    │   │- KYC Fields │   │- Transfers   │
   └────────┬───┘   └──────┬──────┘   └────────┬─────┘
            │               │                   │
            │               │    Events         │
            │               │    (Spring App    │
            │               │    EventPublisher)│
            │               │                   │
            └───────────────┼───────────────────┘
                            │
                            ▼
                  ┌──────────────────────┐
                  │ Ledger Service(8004) │
                  │                      │
                  │- Double-Entry Books. │
                  │- GL Accounts         │
                  │- Journal Entries     │
                  │- Trial Balance       │
                  └──────┬───────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
    ┌────────────────┐      ┌─────────────────┐
    │PostgreSQL      │      │PostgreSQL       │
    │(Shared)        │      │(Ledger DB)      │
    │                │      │                 │
    │auth_db         │      │ledger_db        │
    │account_db      │      │gl_accounts      │
    │transaction_db  │      │journal_entries  │
    └────────────────┘      └─────────────────┘
```

## 🔄 Event-Driven Architecture

### Transaction Lifecycle Flow

```
1. Client Request
   POST /api/v1/transactions/deposit
   {toAccountId, amount, description, requestId}

2. Transaction Service
   ├─ Check idempotency (findByRequestId)
   ├─ Create Transaction entity (PENDING status)
   ├─ Save to database
   └─ Publish TransactionCreatedEvent

3. Event Bus (Spring ApplicationEventPublisher)
   └─ Synchronous event delivery to listeners

4. Ledger Service (Event Listener)
   ├─ Receive TransactionCreatedEvent
   ├─ Validate transaction data
   ├─ Create double-entry journal entries
   │  ├─ For DEPOSIT: DEBIT Assets, CREDIT Liabilities
   │  ├─ For WITHDRAWAL: DEBIT Liabilities, CREDIT Assets
   │  └─ For TRANSFER: DEBIT from account, CREDIT to account
   ├─ Update GL account balances
   └─ Publish TransactionSettledEvent (Phase 2)

5. Transaction Service (Updates status)
   └─ Set status to COMPLETED

6. Response to Client
   {transactionId, status: COMPLETED, ...}
```

### Event Classes

**TransactionCreatedEvent** (Common Module)
```
├─ transactionId: UUID
├─ fromAccountId: UUID (nullable for deposits)
├─ toAccountId: UUID (nullable for withdrawals)
├─ type: String (DEPOSIT, WITHDRAWAL, TRANSFER)
├─ amount: BigDecimal
├─ description: String
└─ timestamp: long
```

## 💾 Database Design Philosophy

### Key Principles

1. **Immutability**: Transactions never modified/deleted (append-only)
2. **Auditability**: All changes logged with timestamp and reason
3. **Consistency**: Database constraints enforce business rules
4. **Idempotency**: requestId unique constraint prevents duplicate transactions

### Database Per Service Pattern

Each microservice owns its database:
- **Auth Service** → `auth_db` (users, user_roles)
- **Account Service** → `account_db` (customers, accounts)
- **Transaction Service** → `transaction_db` (transactions, transaction_audit)
- **Ledger Service** → `ledger_db` (gl_accounts, journal_entries, snapshots)

**Rationale**: 
- Database-level constraints ensure data consistency within service boundaries
- Independent scaling and maintenance
- Clear ownership and responsibility
- Schema evolution without coordinating other services

### Double-Entry Bookkeeping

Every transaction creates exactly 2 journal entries:

```
DEPOSIT: Amount $100
├─ DEBIT:  Asset Account (Customer Deposits) $100
└─ CREDIT: Liability Account (Bank Obligation) $100
   (Net: 0, balanced)

WITHDRAWAL: Amount $100
├─ DEBIT:  Liability Account (Bank Obligation) $100
└─ CREDIT: Asset Account (Customer Deposits) $100
   (Net: 0, balanced)

TRANSFER: From Account A to Account B, Amount $100
├─ DEBIT:  Account A (Customer A balance down) $100
└─ CREDIT: Account B (Customer B balance up) $100
   (Net: 0, balanced)
```

**Validation**: Trial Balance Report
```sql
SELECT SUM(debit) as total_debits, SUM(credit) as total_credits
FROM journal_entries;
-- Always: total_debits = total_credits
```

## 🔐 Security Architecture

### Authentication & Authorization

```
User Request
    │
    ▼
┌─────────────────────────┐
│ API Gateway (8000)      │
│ - Extract Authorization │
│   header (Bearer token) │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ JWT Token Validation                │
│ - Signature: HS512 (secret key)     │
│ - Claims: sub (email), iat, exp     │
│ - Cache: Valid tokens in memory     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Authorization (Spring Security)     │
│ - Load UserDetails from database    │
│ - Extract roles (CUSTOMER, ADMIN)   │
│ - Check @PreAuthorize annotations   │
└────────────┬────────────────────────┘
             │
             ▼
     Request Proceeds
```

### Token Structure

**JWT (HS512 Signature)**
```
Header: {alg: "HS512", typ: "JWT"}

Payload: {
  sub: "user@example.com",
  userId: "123e4567-e89b-12d3-a456-426614174000",
  roles: ["CUSTOMER"],
  iat: 1715169600,
  exp: 1715170500  // 15 minutes from iat
}

Signature: HMACSHA512(
  base64(header) + "." + base64(payload),
  secret-key-min-256-bits
)
```

**Token Lifecycle**
- **Access Token**: 15 minutes (short-lived)
- **Refresh Token**: 7 days (long-lived, stored server-side in Phase 2)
- **Rotation**: Client exchanges refresh token for new access token

### Password Security

- **Hashing**: BCrypt with work factor 12 (100-200ms per hash)
- **Validation**: Minimum 8 characters, mixed case, numbers/symbols (Phase 2)
- **Storage**: Only password_hash stored, never plaintext

### Input Validation

```
User Request
    │
    ▼
┌──────────────────────────────────────┐
│ Bean Validation (javax.validation)   │
│ - @NotNull, @Email, @Size, etc.     │
│ - MethodArgumentNotValidException    │
│   mapped to 400 Bad Request          │
└──────────────────────────────────────┘
    │
    ▼
Sanitization (Spring Security)
    │
    ▼
Business Logic Validation
    │
    ▼
Database Constraints
```

## 📊 Data Consistency Strategy

### Eventual Consistency Model

**Scenario**: Transfer $100 from Account A to Account B

```
T0: Client sends transfer request
T1: Transaction Service creates transaction (PENDING)
T2: Event published
T3: Ledger Service processes event (may take milliseconds)
T4: Transaction status updated to COMPLETED

Between T1-T3: Temporary inconsistency
- Transaction created but not yet settled
- Account balances not yet updated
- Client waits for response (blocking)
```

**Safety Guarantees**:
1. **Idempotency**: Same requestId → same result (database constraint)
2. **Atomicity**: Transaction saved OR not (database ACID)
3. **Durability**: Event persisted before response sent
4. **Consistency**: Ledger validates double-entry bookkeeping

### Handling Failures

**Case 1: Ledger Service Unavailable**
```
1. Transaction Service publishes event
2. Ledger Service cannot receive event
3. Status remains PENDING
4. Retry mechanism: Event replay (Phase 2)
5. Manual recovery: Ledger team reconciles
```

**Case 2: Database Transaction Fails**
```
1. Catch exception
2. Create audit entry (reason: database error)
3. Set transaction status to FAILED
4. Return 500 Internal Server Error to client
5. Client retries with same requestId (idempotent)
```

**Case 3: Concurrent Requests**
```
1. Two clients submit same requestId
2. Database UNIQUE constraint on requestId
3. First succeeds, second gets duplicate key error
4. Transaction Service catches error, returns existing result
5. Both clients receive same response
```

## 🏗️ Architectural Patterns Used

### 1. Microservices Pattern
- Independent services with separate databases
- Clear responsibility boundaries
- Async communication via events
- Horizontal scalability

### 2. Event Sourcing (Phase 2)
- Audit trail of all state changes
- Complete transaction history
- Replay capability for disaster recovery

### 3. CQRS - Command Query Responsibility Segregation (Phase 2)
- Write: Transaction Service (commands)
- Read: Ledger/Analytics Service (queries)
- Separate scaling for reads vs. writes

### 4. Saga Pattern (Phase 3)
- Distributed transactions across services
- Compensation logic for failures
- Manual workflow for complex operations

### 5. Circuit Breaker (Phase 3)
- Detect failures early
- Fast-fail when downstream unavailable
- Graceful degradation

## 🔄 Service Communication

### Synchronous (Request-Response)
Used for: User data retrieval, validation
```
Account Service → Auth Service
GET /api/v1/auth/validate?token=...
(Validate user JWT before processing account request)
```

### Asynchronous (Event-Driven)
Used for: Cross-service side effects
```
Transaction Service --publishes--> TransactionCreatedEvent
Ledger Service --listens--> TransactionCreatedEvent
```

**Why Events?**
- Decoupling: Services don't know about each other
- Scalability: Ledger can lag without blocking transactions
- Reliability: Event replay if service restarts
- Extensibility: New listeners added without changing Transaction Service

## 🗂️ Project Organization

### Module Hierarchy

```
pom.xml (root)
├── <dependencyManagement>
│   └─ Spring Boot 3.3.0, Spring Cloud, JWT, PostgreSQL
├── <properties>
│   └─ java.version: 17, project.build.sourceEncoding: UTF-8
│
├── common/ (Library module)
│   ├─ pom.xml (skip repackage)
│   └─ Shared classes: ApiResponse, AppException, TransactionCreatedEvent
│
├── auth-service/ (Spring Boot App)
│   ├─ pom.xml (depends on common)
│   ├─ Main: AuthServiceApplication.java
│   ├─ Layer structure:
│   │   ├─ entity/ → JPA entities
│   │   ├─ dto/ → Request/Response DTOs
│   │   ├─ repository/ → Spring Data JPA repositories
│   │   ├─ service/ → Business logic
│   │   ├─ controller/ → REST endpoints
│   │   ├─ security/ → JWT, SecurityConfig
│   │   └─ exception/ → GlobalExceptionHandler
│   ├─ resources/
│   │   ├─ application.yml
│   │   └─ db/changelog/ → Liquibase migrations
│   ├─ test/ → Unit + Integration tests
│   └─ Dockerfile (multi-stage)
│
├── account-service/ (Similar structure)
├── transaction-service/ (Similar structure)
├── ledger-service/ (Similar structure)
└── api-gateway/ (Spring Cloud Gateway)
```

## 📈 Scalability Considerations

### Horizontal Scaling
- **Stateless services**: Session data in database
- **Connection pooling**: HikariCP (default in Spring Boot)
- **Database indices**: ON frequently queried columns
- **Load balancing**: Nginx/HAProxy (Phase 3)

### Vertical Scaling
- **Thread pool**: Configurable per service
- **Memory**: JVM heap settings
- **Database**: Connection limits, query optimization

### Future Optimizations (Phase 3)
- **Caching**: Redis for token validation, account balances
- **Database replication**: Master-slave PostgreSQL
- **Async processing**: Message queue (RabbitMQ) instead of in-memory events
- **Batch processing**: Nightly reconciliation jobs

## 🔍 Monitoring & Observability (Phase 3)

```
Services
    │
    ├─ Logs → ELK Stack (Elasticsearch, Logstash, Kibana)
    ├─ Metrics → Prometheus + Grafana
    ├─ Traces → Jaeger (distributed tracing)
    └─ Alerts → PagerDuty
```

### Key Metrics
- Request latency (P50, P95, P99)
- Error rate (4xx, 5xx)
- Transaction throughput (TPS)
- Database connection pool utilization
- JWT token cache hit rate

## ⚠️ Known Limitations (Phase 1)

1. **In-Memory Events**: No event persistence; restart loses pending events
2. **Synchronous Processing**: Ledger waits for completion (blocking)
3. **No Caching**: Every request hits database
4. **Single Region**: No multi-region deployment
5. **Manual Reconciliation**: No automatic failure recovery
6. **No Audit Trail**: Limited logging of who did what when

## 📚 Design Decision Rationale

### Why Spring Boot 3.x + Java 17?
- LTS Java version (support until 2029)
- Virtual threads readiness (Project Loom) for Phase 3
- Spring Boot 3 drops Java 8/11 support, uses latest libraries
- Excellent community support and documentation

### Why PostgreSQL not MongoDB?
- ACID compliance required for banking
- Relational schema enforcement
- Strong data integrity (foreign keys, constraints)
- Transaction support (critical for ledger)

### Why JWT not OAuth 2.0?
- Simpler implementation for MVP (OAuth is enterprise-scale)
- Self-contained tokens (no session storage needed)
- Stateless architecture (horizontal scalability)
- OAuth deferred to Phase 3 (multi-tenant SaaS)

### Why Event-Driven not RPC?
- Decoupling (services independent)
- Failure isolation (Ledger failure ≠ transaction failure)
- Natural for eventual consistency
- Foundation for event sourcing (Phase 2)

## 🔄 Deployment Architecture

### Development
```
docker-compose.yml
├─ PostgreSQL (container)
├─ Auth Service (container)
├─ Account Service (container)
├─ Transaction Service (container)
└─ Ledger Service (container)
```

### Production (Phase 3)
```
Kubernetes Cluster
├─ Services (multiple replicas)
├─ PostgreSQL (managed AWS RDS)
├─ Message Queue (AWS SQS/SNS)
├─ Load Balancer (AWS ALB)
└─ Monitoring (CloudWatch/Prometheus)
```

---

**Next Phase**: Implement Phase 2 services (Notification, Analytics, Compliance)
