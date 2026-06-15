#!/usr/bin/env bash
# Checks that all observability components are reachable and healthy.
# Exit 0 = all OK. Exit 1 = one or more checks failed.

set -euo pipefail

PASS=0
FAIL=0

check() {
  local name="$1"
  local url="$2"
  local expected="${3:-200}"

  code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$url" 2>/dev/null || echo "000")
  if [ "$code" = "$expected" ]; then
    echo "[OK]   $name ($url) → $code"
    PASS=$((PASS + 1))
  else
    echo "[FAIL] $name ($url) → got $code, expected $expected"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Digital Banking Observability Health Check ==="
echo ""

echo "--- Prometheus (ai-agent-service) ---"
check "Prometheus metrics" "http://localhost:8010/metrics" "200"

echo ""
echo "--- LangFuse ---"
check "LangFuse UI" "http://localhost:3001" "200"
check "LangFuse API health" "http://localhost:3001/api/public/health" "200"

echo ""
echo "--- Datadog Agent ---"
check "DD Agent info" "http://localhost:8126/info" "200"

echo ""
echo "--- Core Banking Services ---"
check "ai-agent-service"    "http://localhost:8010/health"            "200"
check "auth-service"        "http://localhost:8001/api/v1/auth/health" "200"
check "account-service"     "http://localhost:8002/api/v1/accounts/health" "200"
check "transaction-service" "http://localhost:8003/api/v1/transactions/health" "200"
check "ledger-service"      "http://localhost:8004/api/v1/ledger/health" "200"
check "complaint-service"   "http://localhost:8011/api/v1/complaints/health" "200"
check "loan-service"        "http://localhost:8012/api/v1/loans/health" "200"
check "ops-service"         "http://localhost:8013/api/v1/ops/health" "200"

echo ""
echo "--- MCP Adapter Layer ---"
check "casa-mcp-server"      "http://localhost:8014/health" "200"
check "ml-mcp-server"        "http://localhost:8015/health" "200"
check "cul-mcp-server"       "http://localhost:8016/health" "200"
check "complaint-mcp-server" "http://localhost:8017/health" "200"

echo ""
echo "================================="
echo "Results: $PASS passed, $FAIL failed"
echo "================================="

[ "$FAIL" -eq 0 ]
