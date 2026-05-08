# Digital Banking Platform - Reusable Skills & Workflows

## 🛠️ Available Skills

Reusable prompts and workflows for automating common tasks in the Digital Banking project.

---

## 1. Skill: Full Build & Test Suite

**Purpose**: Execute complete build, unit tests, and integration tests

**File**: `.claude/skills/full-build-test.md`

```markdown
# Full Build & Test Suite

## Objective
Execute Maven clean build with all tests to verify code integrity.

## Steps
1. Clean previous build artifacts
2. Run unit tests (all modules)
3. Run integration tests (Testcontainers)
4. Report coverage metrics
5. Generate test report

## Commands
\`\`\`bash
cd C:\Veera\AI\agents\DigitalBanking

# Full build with all tests
mvn clean verify -DskipITs=false

# View test reports
# HTML reports at: <module>/target/surefire-reports/

# Check coverage
mvn clean install jacoco:report
# Coverage at: <module>/target/site/jacoco/index.html
\`\`\`

## Expected Output
```
BUILD SUCCESS
Total Tests: XX
Tests Passed: XX
Tests Failed: 0
Code Coverage: > 80%
```

## Troubleshooting
- If tests fail: Check logs in target/surefire-reports/
- If coverage low: Add tests for untested code paths
- If Docker needed: Ensure Docker daemon running
```

---

## 2. Skill: Docker Build & Deploy Local

**Purpose**: Build Docker images and start services locally

**File**: `.claude/skills/docker-build-deploy.md`

```markdown
# Docker Build & Deploy

## Objective
Build all Docker images and verify services start correctly.

## Steps
1. Verify Docker daemon running
2. Build each service Docker image
3. Start services with docker-compose
4. Verify health checks pass
5. Run smoke tests

## Commands
\`\`\`bash
# Navigate to project
cd C:\Veera\AI\agents\DigitalBanking

# Verify Docker running
docker ps

# Build all images
docker-compose build

# Start services
docker-compose up -d

# Wait for health checks
sleep 10

# Check service status
docker-compose ps

# Verify all services are "Up (healthy)"

# Run health check endpoints
curl http://localhost:8001/api/v1/auth/health
curl http://localhost:8002/api/v1/accounts/health
curl http://localhost:8003/api/v1/transactions/health
curl http://localhost:8004/api/v1/ledger/health

# View logs for any service
docker-compose logs -f auth-service
\`\`\`

## Expected Output
```
CONTAINER ID    IMAGE              STATUS
<id>            postgres:15-alpine  Up 1 minute (healthy)
<id>            auth-service       Up 30 seconds (healthy)
<id>            account-service    Up 30 seconds (healthy)
<id>            transaction-service Up 30 seconds (healthy)
<id>            ledger-service     Up 30 seconds (healthy)
```

## Health Check Responses
```json
{
  "success": true,
  "data": "Service is running",
  "message": "Health check passed"
}
```
```

---

## 3. Skill: End-to-End Transaction Test

**Purpose**: Execute complete transaction flow from registration to ledger settlement

**File**: `.claude/skills/e2e-transaction-test.md`

```markdown
# End-to-End Transaction Flow Test

## Objective
Test complete transaction lifecycle: Register user → Create account → Deposit → Verify ledger

## Prerequisites
- All services running (docker-compose up -d)
- curl installed

## Test Flow
\`\`\`bash
#!/bin/bash

# 1. REGISTER USER
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123",
    "fullName": "Test User"
  }')

USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.data.userId')
echo "✓ User registered: $USER_ID"

# 2. LOGIN USER
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPass123"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.accessToken')
echo "✓ Access token obtained"

# 3. CREATE ACCOUNT
echo "3. Creating account..."
ACCOUNT_RESPONSE=$(curl -X POST http://localhost:8002/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "userId": "'$USER_ID'",
    "name": "Test User",
    "dob": "1990-01-01",
    "email": "testuser@example.com",
    "accountType": "SAVINGS"
  }')

ACCOUNT_ID=$(echo $ACCOUNT_RESPONSE | jq -r '.data.account.id')
echo "✓ Account created: $ACCOUNT_ID"

# 4. DEPOSIT $100
echo "4. Depositing $100..."
DEPOSIT_RESPONSE=$(curl -X POST http://localhost:8003/api/v1/transactions/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "toAccountId": "'$ACCOUNT_ID'",
    "amount": 100.00,
    "description": "Initial deposit",
    "requestId": "req-deposit-001"
  }')

TRANSACTION_ID=$(echo $DEPOSIT_RESPONSE | jq -r '.data.id')
echo "✓ Transaction created: $TRANSACTION_ID"

# 5. VERIFY LEDGER ENTRIES
echo "5. Verifying ledger entries..."
sleep 1  # Wait for ledger processing

LEDGER_RESPONSE=$(curl -X GET http://localhost:8004/api/v1/ledger/journal/$TRANSACTION_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN")

ENTRY_COUNT=$(echo $LEDGER_RESPONSE | jq '.data | length')
echo "✓ Ledger entries created: $ENTRY_COUNT (expected: 2)"

# 6. VERIFY TRANSACTION COMPLETED
TRANSACTION_STATUS=$(curl -X GET http://localhost:8003/api/v1/transactions/$TRANSACTION_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq -r '.data.status')

echo "✓ Transaction status: $TRANSACTION_STATUS"

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "User ID: $USER_ID"
echo "Account ID: $ACCOUNT_ID"
echo "Transaction ID: $TRANSACTION_ID"
echo "Transaction Status: $TRANSACTION_STATUS"
echo "Ledger Entries: $ENTRY_COUNT"
echo "=========================================="
\`\`\`

## Success Criteria
- ✅ User registered successfully
- ✅ Account created
- ✅ Deposit transaction created
- ✅ 2 journal entries in ledger (debit & credit)
- ✅ Transaction status = COMPLETED
```

---

## 4. Skill: Code Quality Check

**Purpose**: Verify code quality, coverage, and style standards

**File**: `.claude/skills/code-quality-check.md`

```markdown
# Code Quality Check

## Objective
Verify test coverage, analyze code quality, generate reports.

## Checks Performed
1. Unit test coverage (target: > 80%)
2. Code duplication analysis
3. Potential bug detection
4. Security vulnerability scan
5. Test pass rate

## Commands
\`\`\`bash
cd C:\Veera\AI\agents\DigitalBanking

# 1. Run all tests with coverage
mvn clean verify jacoco:report

# 2. View coverage reports
# Coverage: <module>/target/site/jacoco/index.html
# Example: auth-service/target/site/jacoco/index.html

# 3. Check for code duplicates
mvn clean compile source:aggregate pmd:cpd

# 4. Security vulnerability scan
mvn clean install org.owasp:dependency-check-maven:check

# 5. Code style check
mvn clean compile checkstyle:check

# 6. Run all quality checks
mvn clean verify site
\`\`\`

## Reports Generated
- Coverage Report: target/site/jacoco/index.html
- Checkstyle Report: target/site/checkstyle.html
- Dependency Check: target/dependency-check-report.html
- PMD/CPD: target/site/cpd.html

## Quality Gates
```
Coverage:        >= 80%
Duplicated Code: <  5%
Critical Bugs:   =  0
High Bugs:       =  0
Vulnerabilities: =  0
```
```

---

## 5. Skill: Database Reset & Initialization

**Purpose**: Clear test data and reinitialize database schema

**File**: `.claude/skills/database-reset.md`

```markdown
# Database Reset & Initialization

## Objective
Reset PostgreSQL databases to clean state, run Liquibase migrations.

## ⚠️ WARNING
This skill DELETES all data. Use only in development environment.

## Steps
\`\`\`bash
cd C:\Veera\AI\agents\DigitalBanking

# 1. Connect to PostgreSQL
docker-compose exec postgres psql -U postgres

# 2. Drop and recreate databases
-- Inside psql
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS account_db;
DROP DATABASE IF EXISTS transaction_db;
DROP DATABASE IF EXISTS ledger_db;

CREATE DATABASE auth_db;
CREATE DATABASE account_db;
CREATE DATABASE transaction_db;
CREATE DATABASE ledger_db;

\\q  -- Exit psql

# 3. Run Liquibase migrations
mvn -pl auth-service liquibase:update
mvn -pl account-service liquibase:update
mvn -pl transaction-service liquibase:update
mvn -pl ledger-service liquibase:update

# 4. Verify schema created
docker-compose exec postgres psql -U postgres -d auth_db -c "\\dt"
# Expected: users, user_roles tables

# 5. Restart services
docker-compose down
docker-compose up -d
\`\`\`

## Verification
\`\`\`bash
# Check all databases exist
docker-compose exec postgres psql -U postgres -c "\\l"

# Check auth_db tables
docker-compose exec postgres psql -U postgres -d auth_db -c "\\dt"

# Check for migration history
docker-compose exec postgres psql -U postgres -d auth_db -c \
  "SELECT id, filename FROM databasechangelog ORDER BY orderexecuted DESC LIMIT 5;"
\`\`\`
```

---

## 6. Skill: Generate Test Data

**Purpose**: Create realistic test data for development and testing

**File**: `.claude/skills/generate-test-data.md`

```markdown
# Generate Test Data

## Objective
Populate databases with realistic test data for manual testing.

## Test Data Created
- 5 test users with roles
- 5 customer accounts (3 Savings, 2 Checking)
- 10 transactions (deposits, withdrawals, transfers)
- GL accounts initialized
- Journal entries created

## SQL Script
\`\`\`sql
-- Auth Service: Create test users
INSERT INTO users (id, email, password_hash, full_name, active, created_at, updated_at)
VALUES
  ('550e8400-e29b-41d4-a716-446655440001', 'alice@example.com', 
   '$2a$12$...hashed_password...', 'Alice Smith', true, NOW(), NOW()),
  ('550e8400-e29b-41d4-a716-446655440002', 'bob@example.com',
   '$2a$12$...hashed_password...', 'Bob Johnson', true, NOW(), NOW()),
  ('550e8400-e29b-41d4-a716-446655440003', 'charlie@example.com',
   '$2a$12$...hashed_password...', 'Charlie Brown', true, NOW(), NOW()),
  ('550e8400-e29b-41d4-a716-446655440004', 'diana@example.com',
   '$2a$12$...hashed_password...', 'Diana Prince', true, NOW(), NOW()),
  ('550e8400-e29b-41d4-a716-446655440005', 'eve@example.com',
   '$2a$12$...hashed_password...', 'Eve Wilson', true, NOW(), NOW());

-- Account Service: Create test customers & accounts
INSERT INTO customers (id, user_id, name, dob, email, phone, address_line1, 
  address_line2, city, state, zip_code, country, pan, aadhar, kyc_status, kyc_verified_at, created_at, updated_at)
VALUES
  ('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001',
   'Alice Smith', '1990-05-15', 'alice@example.com', '+1234567890',
   '123 Main St', 'Apt 4B', 'New York', 'NY', '10001', 'USA',
   'ABCDE1234F', '123456789012', 'VERIFIED', NOW(), NOW(), NOW()),
  ('650e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002',
   'Bob Johnson', '1985-03-22', 'bob@example.com', '+1987654321',
   '456 Oak Ave', NULL, 'Los Angeles', 'CA', '90001', 'USA',
   'FGHIJ5678K', '234567890123', 'VERIFIED', NOW(), NOW(), NOW());

INSERT INTO accounts (id, customer_id, account_number, account_type, status, created_at)
VALUES
  ('750e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001',
   'ACC001', 'SAVINGS', 'ACTIVE', NOW()),
  ('750e8400-e29b-41d4-a716-446655440002', '650e8400-e29b-41d4-a716-446655440002',
   'ACC002', 'CHECKING', 'ACTIVE', NOW());

-- Ledger Service: Initialize GL Accounts
INSERT INTO gl_accounts (id, code, name, type, balance, created_at, updated_at)
VALUES
  ('850e8400-e29b-41d4-a716-446655440001', 'ASSET-001', 'Customer Deposits', 'ASSET', 0, NOW(), NOW()),
  ('850e8400-e29b-41d4-a716-446655440002', 'LIABILITY-001', 'Bank Obligations', 'LIABILITY', 0, NOW(), NOW());
\`\`\`

## Credentials for Testing
\`\`\`
Email: alice@example.com
Password: (use hash, or set plaintext via SQL)

Email: bob@example.com
Password: (use hash, or set plaintext via SQL)
\`\`\`
```

---

## 7. Skill: Performance & Load Test

**Purpose**: Run load tests to verify throughput and latency targets

**File**: `.claude/skills/performance-test.md`

```markdown
# Performance & Load Test

## Objective
Test transaction throughput and latency under load.

## Tools
- Apache JMeter (for load testing)
- Gatling (for performance analysis)

## Test Scenarios
1. **Login Test**: 10 concurrent users, 100 requests/sec
2. **Deposit Test**: 20 concurrent users, 50 TPS
3. **Sustained Load**: 30 concurrent users, 2-minute duration

## JMeter Test Plan
\`\`\`xml
<!-- login-test.jmx -->
<jmeterTestPlan version="1.2">
  <hashTree>
    <ThreadGroup guiclass="ThreadGroupGui">
      <elementProp name="ThreadGroup.main_controller">
        <stringProp name="ThreadGroup.num_threads">10</stringProp>
        <stringProp name="ThreadGroup.ramp_time">10</stringProp>
      </elementProp>
    </ThreadGroup>
    <HTTPSampler guiclass="HttpTestSampleGui">
      <elementProp name="HTTPsampler.Arguments">
        <stringProp name="HTTPSampler.domain">localhost</stringProp>
        <stringProp name="HTTPSampler.port">8001</stringProp>
        <stringProp name="HTTPSampler.path">/api/v1/auth/login</stringProp>
        <stringProp name="HTTPSampler.method">POST</stringProp>
      </elementProp>
    </HTTPSampler>
  </hashTree>
</jmeterTestPlan>
\`\`\`

## Run Test
\`\`\`bash
# Install JMeter
# https://jmeter.apache.org/download_jmeter.cgi

# Run test with CSV output
jmeter -n -t login-test.jmx -l results.jtl -j jmeter.log

# Generate HTML report
jmeter -g results.jtl -o report/
\`\`\`

## Success Criteria
- Throughput: >= 100 TPS
- Latency P95: <= 500ms
- Error Rate: < 1%
- Memory: < 80% utilization
```

---

## 📋 How to Use Skills

### From Claude Code IDE
1. Open `.claude/skills/` folder
2. Select skill markdown file
3. Copy command blocks
4. Execute in terminal

### Via Command Line
```bash
# Read skill documentation
cat .claude/skills/full-build-test.md

# Extract and run commands
grep -A 20 "## Commands" .claude/skills/docker-build-deploy.md | bash
```

### In CI/CD Pipeline
Skills can be converted to GitHub Actions workflows:

```yaml
name: Full Build Test
on: [push, pull_request]

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-java@v3
        with:
          java-version: '17'
      - run: mvn clean verify
      - uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: '**/target/surefire-reports/'
```

---

## 🔧 Creating New Skills

### Template
```markdown
# Skill: [Name]

## Purpose
[What does this skill accomplish?]

## Prerequisites
- [Required software/setup]
- [Environment assumptions]

## Steps
1. [Step 1]
2. [Step 2]

## Commands
\`\`\`bash
# Command block
\`\`\`

## Expected Output
[What success looks like]

## Troubleshooting
[Common issues & fixes]
```

### Best Practices
- Keep skills focused (one task per skill)
- Include error handling and diagnostics
- Document expected output
- Provide success criteria
- Add troubleshooting section

---

**Next Steps**:
- Convert skills to GitHub Actions workflows
- Add more specialized skills (e.g., database backup, load testing)
- Integrate with CI/CD pipeline
