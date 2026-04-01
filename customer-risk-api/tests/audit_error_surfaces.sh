#!/usr/bin/env bash
set -euo pipefail

# Read API_KEY from .env (must be run from customer-risk-api/)
if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Run from customer-risk-api/" >&2
  exit 1
fi
API_KEY=$(grep -E '^API_KEY=' .env | cut -d'=' -f2 | tr -d '[:space:]')
if [[ -z "$API_KEY" ]]; then
  echo "ERROR: API_KEY is empty in .env" >&2
  exit 1
fi

BASE_URL="http://localhost:8000"
CUSTOMER_URL="$BASE_URL/api/v1/customers"

FORBIDDEN=(
  "psycopg2"
  "Traceback"
  "postgres"
  "riskdb"
  "risk_profiles"
  "SELECT"
  "Exception"
  "Postgres"
  "POSTGRES_"
  "ERROR"
  "error at"
)

PASS_COUNT=0
FAIL_COUNT=0

check_response() {
  local label="$1"
  local body="$2"
  local headers="$3"
  local full="$headers $body"
  local failed=0

  for term in "${FORBIDDEN[@]}"; do
    if echo "$full" | grep -qF "$term"; then
      echo "  LEAK: '$term' found in response"
      failed=1
    fi
  done

  if [[ $failed -eq 0 ]]; then
    echo "PASS  $label"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo "FAIL  $label"
    echo "      body: $body"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
}

run_curl() {
  # Returns headers + body; captures both; does not fail on HTTP errors
  curl -s -D - "$@" 2>/dev/null
}

echo "========================================"
echo " INV-07 Error Surface Audit"
echo "========================================"
echo ""

# 1. Missing API key
echo "--- Test 1: Missing API key ---"
raw=$(run_curl "$CUSTOMER_URL/DEMO-001")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "Missing API key → 401" "$body" "$headers"

# 2. Wrong API key
echo "--- Test 2: Wrong API key ---"
raw=$(run_curl -H "X-API-Key: BADKEY" "$CUSTOMER_URL/DEMO-001")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "Wrong API key → 401" "$body" "$headers"

# 3. Unknown customer ID
echo "--- Test 3: Unknown customer ---"
raw=$(run_curl -H "X-API-Key: $API_KEY" "$CUSTOMER_URL/DEMO-XXXX")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "Unknown customer → 404" "$body" "$headers"

# 4. Malformed ID (lowercase)
echo "--- Test 4: Malformed ID (lowercase) ---"
raw=$(run_curl -H "X-API-Key: $API_KEY" "$CUSTOMER_URL/demo-001")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "Malformed ID → 422" "$body" "$headers"

# 5. Overlength ID (21 chars)
echo "--- Test 5: Overlength ID ---"
raw=$(run_curl -H "X-API-Key: $API_KEY" "$CUSTOMER_URL/ABCDEFGHIJKLMNOPQRSTU")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "Overlength ID → 422" "$body" "$headers"

# 6. DB down
echo "--- Test 6: DB down → 503 ---"
docker compose stop postgres > /dev/null 2>&1
sleep 2
raw=$(run_curl -H "X-API-Key: $API_KEY" "$CUSTOMER_URL/DEMO-001")
headers=$(echo "$raw" | sed '/^\r$/q')
body=$(echo "$raw" | sed '1,/^\r$/d')
check_response "DB down → 503" "$body" "$headers"

echo "  Restarting postgres..."
docker compose start postgres > /dev/null 2>&1
# Wait for healthy
for i in $(seq 1 20); do
  health=$(docker inspect --format='{{.State.Health.Status}}' \
    "$(docker compose ps -q postgres)" 2>/dev/null || echo "unknown")
  if [[ "$health" == "healthy" ]]; then
    echo "  postgres healthy."
    break
  fi
  sleep 2
done

echo ""
echo "========================================"
echo " Results: $PASS_COUNT passed, $FAIL_COUNT failed"
echo "========================================"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
fi
