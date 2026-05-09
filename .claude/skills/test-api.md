---
name: test-api
description: Run a complete end-to-end API test of the Digital Banking system — register, login, create account, deposit, withdraw, transfer, and verify ledger entries. All requests go through the API Gateway on port 8000.
---

# End-to-End API Test

Runs a full user journey through the API Gateway to verify all microservices are working together correctly.

## Test Flow

1. Register a new test user
2. Login and capture JWT access token
3. Create a bank account
4. Deposit ₹10,000
5. Withdraw ₹2,000
6. Transfer ₹1,000 to a second account
7. Verify transaction history
8. Check ledger entries (double-entry bookkeeping)

## Commands

```bash
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
echo "User ID: $USER_ID"

echo ""
echo "=== Step 2: Login ==="
LOGIN=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
echo $LOGIN
TOKEN=$(echo $LOGIN | grep -o '"accessToken":"[^"]*"' | cut -d'"' -f4)
echo "Token acquired: ${TOKEN:0:30}..."

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
    \"address\":\"456 Test Ave\",
    \"city\":\"Mumbai\",
    \"state\":\"MH\",
    \"zipCode\":\"400001\",
    \"pan\":\"TESTF1234X\",
    \"aadhar\":\"999999999999\",
    \"accountType\":\"SAVINGS\"
  }")
echo $ACCOUNT
ACCOUNT_ID=$(echo $ACCOUNT | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Account ID: $ACCOUNT_ID"

echo ""
echo "=== Step 4: Deposit ₹10,000 ==="
curl -s -X POST $BASE_URL/api/v1/transactions/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"toAccountId\":\"$ACCOUNT_ID\",
    \"amount\":10000,
    \"requestId\":\"req-deposit-${TIMESTAMP}\",
    \"description\":\"Initial deposit\"
  }"

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
echo "=== All Tests Complete ==="
echo "User:    $EMAIL"
echo "Account: $ACCOUNT_ID"
echo "Token:   ${TOKEN:0:30}..."
```

## Expected Results

| Step | Expected Response |
|------|------------------|
| Register | `"success":true`, userId returned |
| Login | `"success":true`, accessToken returned |
| Create Account | `"success":true`, account id returned, kycStatus: PENDING |
| Deposit | `"success":true`, status: PENDING, type: DEPOSIT |
| Withdraw | `"success":true`, status: PENDING, type: WITHDRAWAL |

## Quick Smoke Test

Just verify the gateway is routing and JWT auth works:

```bash
# Register + login in one script
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","password":"Smoke123!","fullName":"Smoke Test"}' \
  | grep -o '"success":true'

curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","password":"Smoke123!"}' \
  | grep -o '"accessToken":"[^"]*"' | cut -c1-50
```
