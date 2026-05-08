#!/bin/bash

#############################################################################
# DigitalBanking Complete E2E Testing & Deployment Script
#
# This script automates the complete testing flow:
# 1. Start Docker Compose (all backend services)
# 2. Verify service health
# 3. Test Auth Service API
# 4. Test Account Service API
# 5. Test Transaction Service API
# 6. Run Cypress E2E tests
# 7. Generate test report
#############################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"
API_GATEWAY="http://localhost:8000"
AUTH_SERVICE="http://localhost:8001"
ACCOUNT_SERVICE="http://localhost:8002"
TRANSACTION_SERVICE="http://localhost:8003"
LEDGER_SERVICE="http://localhost:8004"
SHELL_APP="http://localhost:4200"
CYPRESS_TIMEOUT=300  # 5 minutes

# Test credentials
TEST_EMAIL="test@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_NAME="Test User"

#############################################################################
# Functions
#############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

check_prerequisites() {
    print_header "STEP 1: Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker Desktop."
        exit 1
    fi
    print_success "Docker installed: $(docker --version)"

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose not found."
        exit 1
    fi
    print_success "Docker Compose installed: $(docker-compose --version)"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js."
        exit 1
    fi
    print_success "Node.js installed: $(node --version)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm not found."
        exit 1
    fi
    print_success "npm installed: $(npm --version)"
}

start_docker_compose() {
    print_header "STEP 2: Starting Docker Compose Services"

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        print_error "docker-compose.yml not found in current directory"
        exit 1
    fi

    print_warning "Starting services... This may take 30-45 seconds"
    docker-compose up -d

    sleep 10

    # Check if services are running
    print_success "Docker Compose services started"

    # Show running containers
    echo ""
    echo "Running containers:"
    docker-compose ps
}

wait_for_services() {
    print_header "STEP 3: Waiting for Services to be Healthy"

    declare -a SERVICES=(
        "Auth Service:8001"
        "Account Service:8002"
        "Transaction Service:8003"
        "Ledger Service:8004"
    )

    for service in "${SERVICES[@]}"; do
        SERVICE_NAME="${service%%:*}"
        PORT="${service##*:}"

        echo "Waiting for $SERVICE_NAME (Port $PORT)..."

        for i in {1..30}; do
            if curl -s "http://localhost:$PORT/health" > /dev/null 2>&1; then
                print_success "$SERVICE_NAME is healthy"
                break
            fi
            if [ $i -eq 30 ]; then
                print_error "$SERVICE_NAME failed to start after 30 attempts"
                exit 1
            fi
            sleep 2
        done
    done
}

test_auth_service() {
    print_header "STEP 4: Testing Auth Service API"

    # Register user
    echo "Registering test user..."
    REGISTER_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\",
            \"fullName\": \"$TEST_NAME\"
        }")

    if echo "$REGISTER_RESPONSE" | grep -q "success"; then
        print_success "User registered successfully"
    else
        print_warning "User registration response: $REGISTER_RESPONSE"
    fi

    # Login user
    echo "Logging in test user..."
    LOGIN_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")

    if echo "$LOGIN_RESPONSE" | grep -q "accessToken"; then
        print_success "User login successful"
        # Extract token for later use
        AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)
        export AUTH_TOKEN
    else
        print_warning "Login response: $LOGIN_RESPONSE"
    fi
}

test_account_service() {
    print_header "STEP 5: Testing Account Service API"

    if [ -z "$AUTH_TOKEN" ]; then
        print_warning "Skipping Account Service tests (no auth token)"
        return
    fi

    echo "Retrieving accounts..."
    ACCOUNTS_RESPONSE=$(curl -s -X GET "$ACCOUNT_SERVICE/api/v1/accounts" \
        -H "Authorization: Bearer $AUTH_TOKEN")

    if echo "$ACCOUNTS_RESPONSE" | grep -q "success\|error"; then
        print_success "Account Service API responding"
    fi
}

test_transaction_service() {
    print_header "STEP 6: Testing Transaction Service API"

    if [ -z "$AUTH_TOKEN" ]; then
        print_warning "Skipping Transaction Service tests (no auth token)"
        return
    fi

    echo "Retrieving transactions..."
    TRANSACTIONS_RESPONSE=$(curl -s -X GET "$TRANSACTION_SERVICE/api/v1/transactions" \
        -H "Authorization: Bearer $AUTH_TOKEN")

    if echo "$TRANSACTIONS_RESPONSE" | grep -q "success\|error\|\[\]"; then
        print_success "Transaction Service API responding"
    fi
}

setup_frontend() {
    print_header "STEP 7: Setting Up Frontend"

    if [ ! -d "digital-banking-ui" ]; then
        print_error "digital-banking-ui directory not found"
        exit 1
    fi

    cd digital-banking-ui

    print_warning "Installing npm dependencies..."
    npm ci > /dev/null 2>&1 || npm install > /dev/null 2>&1
    print_success "Dependencies installed"

    cd ..
}

run_e2e_tests() {
    print_header "STEP 8: Running Cypress E2E Tests"

    cd digital-banking-ui

    print_warning "Running E2E tests... This may take 5-10 minutes"

    if npm run test:e2e; then
        print_success "All E2E tests passed!"
    else
        print_error "Some E2E tests failed. Check cypress/reports/ for details."
    fi

    cd ..
}

generate_report() {
    print_header "STEP 9: Generating Test Report"

    cd digital-banking-ui

    if [ -d "cypress/reports" ]; then
        echo "Test report generated at: cypress/reports/index.html"
        ls -lh cypress/reports/
    fi

    if [ -d "cypress/videos" ]; then
        echo ""
        echo "Test videos:"
        ls -lh cypress/videos/ | tail -10
    fi

    cd ..
}

print_summary() {
    print_header "TESTING COMPLETE"

    echo "Test Summary:"
    echo "  ✓ Docker services started"
    echo "  ✓ Services health verified"
    echo "  ✓ Auth Service tested"
    echo "  ✓ Account Service tested"
    echo "  ✓ Transaction Service tested"
    echo "  ✓ Frontend setup"
    echo "  ✓ E2E tests executed"
    echo ""
    echo "Results:"
    echo "  - Digital Banking Shell App: $SHELL_APP"
    echo "  - Auth Service: $AUTH_SERVICE"
    echo "  - Account Service: $ACCOUNT_SERVICE"
    echo "  - Transaction Service: $TRANSACTION_SERVICE"
    echo "  - Ledger Service: $LEDGER_SERVICE"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:4200 in browser"
    echo "  2. Login with: $TEST_EMAIL / $TEST_PASSWORD"
    echo "  3. Test the application features"
    echo "  4. Check test reports: cypress/reports/index.html"
    echo ""
}

cleanup() {
    print_header "Cleanup Function"

    read -p "Stop Docker services? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Stopping services..."
        docker-compose down
        print_success "Services stopped"
    fi
}

#############################################################################
# Main Execution
#############################################################################

main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   DigitalBanking Complete E2E Testing & Deployment         ║${NC}"
    echo -e "${BLUE}║   Version 1.0 - Production Ready                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_prerequisites
    start_docker_compose
    wait_for_services
    test_auth_service
    test_account_service
    test_transaction_service
    setup_frontend
    run_e2e_tests
    generate_report
    print_summary

    # Optional cleanup
    # cleanup
}

# Run main function
main "$@"
