---
name: test-api
description: Run a complete end-to-end API test of the Digital Banking system — register, login, create account, deposit, withdraw, transfer, verify KYC, check analytics, and verify notification enrichment. All user-facing requests go through the API Gateway on port 8000. Analytics/Notifications queried directly.
---

# End-to-End API Test

Runs a full Phase 1 + Phase 2 user journey through the platform.

## Complete Test Flow

1. Register a new test user
2. Login and capture JWT access token
3. Create a bank account → capture CUSTOMER_ID and ACCOUNT_ID
4. Deposit ₹10,000
5. Withdraw ₹2,000
6. Verify notification was created with enriched email
7. Check analytics statement and summary
8. Submit a KYC document
9. Add a beneficiary

## Commands

```bash
cd C:/Veera/AI/agents/DigitalBanking
BASE_URL="http://localhost:8000"
TIMESTAMP=$(date +%s)
EMAIL="apitest_${TIMESTAMP}@bank.com"
PASSWORD="TestPass123!"

echo "=== Step 1: Register User ==="
REGISTER=$(curl -s -X POST $BASE_URL/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"fullName\":\"API Test User\"}")
echo $REGISTER
USER_ID=$(echo $REGISTER | grep -o '"userId":"[^"]*"' | cut -d'"' -f4)
echo "USER_ID: $USER_ID"

echo ""
echo "=== Step 2: Login ==="
LOGIN=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
TOKEN=$(echo $LOGIN | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:40}..."

echo ""
echo "=== Step 3: Create Account ==="
ACCOUNT=$(curl -s -X POST $BASE_URL/api/v1/accounts/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"userId\":\"$USER_ID\",
    \"name\":\"API Test User\",
    \"email\":\"$EMAIL\",
    \"phone\":\"9876543210\",
    \"dob\":\"1990-01-15\",
    \"addressLine1\":\"456 Test Ave\",
    \"city\":\"Mumbai\",
    \"state\":\"MH\",
    \"zipCode\":\"400001\",
    \"country\":\"India\",
    \"pan\":\"TESTF${TIMESTAMP: -4}X\",
    \"accountType\":\"SAVINGS\"
  }")
echo $ACCOUNT
CUSTOMER_ID=$(echo $ACCOUNT | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "CUSTOMER_ID: $CUSTOMER_ID"

# Get ACCOUNT_ID from database
ACCOUNT_ID=$(docker exec digital-banking-postgres psql -U postgres -d account_db -t -c \
  "SELECT a.id FROM accounts a JOIN customers c ON a.customer_id=c.id WHERE c.email='$EMAIL';" \
  | tr -d ' \n')
echo "ACCOUNT_ID: $ACCOUNT_ID"

echo ""
echo "=== Step 4: Deposit ₹10,000 ==="
DEPOSIT=$(curl -s -X POST $BASE_URL/api/v1/transactions/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"toAccountId\":\"$ACCOUNT_ID\",
    \"amount\":10000,
    \"requestId\":\"req-deposit-${TIMESTAMP}\",
    \"description\":\"Initial deposit\"
  }")
echo $DEPOSIT
TXN_ID=$(echo $DEPOSIT | grep -o '"transactionId":"[^"]*"' | cut -d'"' -f4)
echo "TXN_ID: $TXN_ID"

echo ""
echo "=== Step 5: Withdraw ₹2,000 ==="
curl -s -X POST $BASE_URL/api/v1/transactions/withdraw \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"fromAccountId\":\"$ACCOUNT_ID\",
    \"amount\":2000,
    \"requestId\":\"req-withdraw-${TIMESTAMP}\",
    \"description\":\"ATM withdrawal\"
  }"

echo ""
echo "=== Step 6: Check Notification (KYC enrichment) ==="
sleep 3
curl -s "http://localhost:8006/api/v1/notifications?transaction_id=$TXN_ID" | \
  grep -o '"recipient":"[^"]*"\|"status":"[^"]*"'
# Expected: "recipient":"apitest_...@bank.com" (not empty — KYC enrichment working)

echo ""
echo "=== Step 7: Analytics Statement ==="
curl -s "http://localhost:8007/api/v1/analytics/accounts/$ACCOUNT_ID/statement"

echo ""
echo "=== Step 8: Analytics Summary ==="
curl -s "http://localhost:8007/api/v1/analytics/accounts/$ACCOUNT_ID/summary"

echo ""
echo "=== Step 9: Submit KYC Document ==="
curl -s -X POST "$BASE_URL/api/v1/customers/$CUSTOMER_ID/kyc/documents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"documentType":"PAN_CARD","documentReference":"ABCDE1234F"}'

echo ""
echo "=== Step 10: KYC Status ==="
curl -s "$BASE_URL/api/v1/customers/$CUSTOMER_ID/kyc/status" \
  -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== All Tests Complete ==="
echo "Email:       $EMAIL"
echo "USER_ID:     $USER_ID"
echo "CUSTOMER_ID: $CUSTOMER_ID"
echo "ACCOUNT_ID:  $ACCOUNT_ID"
echo "TXN_ID:      $TXN_ID"
```

## Expected Results

| Step | Expected Response |
|------|------------------|
| Register | `"success":true`, userId returned |
| Login | `"success":true`, accessToken returned |
| Create Account | `"success":true`, id (CUSTOMER_ID) returned, kycStatus: PENDING |
| Deposit | `"success":true`, status: PENDING, type: DEPOSIT |
| Withdraw | `"success":true`, status: PENDING, type: WITHDRAWAL |
| Notification | `"recipient":"<real email>"` — NOT empty (KYC enrichment) |
| Statement | 2 transactions with direction CREDIT/DEBIT |
| Summary | total_credits=10000, total_debits=2000, net=8000 |
| KYC Doc | `"success":true`, status: PENDING, documentType: PAN_CARD |
| KYC Status | totalDocuments:1, pendingDocuments:1, overallStatus: PENDING |

## Quick Smoke Test (30 seconds)

```bash
cd C:/Veera/AI/agents/DigitalBanking

# All services healthy?
docker-compose ps | grep -v healthy

# Auth + gateway working?
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","password":"Smoke123!","fullName":"Smoke"}' \
  | grep -o '"success":true'

# Analytics working?
curl -s http://localhost:8007/api/v1/analytics/health | grep -o '"status":"healthy"'

# Customer service working?
curl -s http://localhost:8005/api/v1/customers/health | grep -o '"success":true'

# Notifications working?
curl -s "http://localhost:8006/api/v1/notifications/stats"
```
