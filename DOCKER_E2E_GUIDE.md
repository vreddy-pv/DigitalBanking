# Docker Build & E2E Testing Guide

## Overview

This guide walks through building the Digital Banking Platform frontend and backend services with Docker, deploying via docker-compose, and running comprehensive end-to-end tests.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                 Infrastructure Layer                 │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  PostgreSQL 15    Redis 7      RabbitMQ 3.12        │   │
│  │  (port 5432)      (port 6379)  (port 5672, 15672)   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Backend Services Layer                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  API Gateway:8000        Auth Service:8001          │   │
│  │  Account Service:8002    Transaction Service:8003   │   │
│  │  Ledger Service:8004     Notification Service:8006  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             Frontend Services Layer                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Shell App:4200          Account MFE:4201           │   │
│  │  Transaction MFE:4202    Transfer MFE:4203          │   │
│  │  Notification MFE:4204   Settings MFE:4205          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Testing & Monitoring                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  Cypress Tests  Prometheus  Grafana (optional)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Frontend Build

### 2-Stage Docker Build Explanation

The multi-stage Dockerfile optimizes for both build and runtime:

**Stage 1 (Builder)**:
- Uses `node:18-alpine` as base
- Large intermediate image size (~1.5GB with node_modules)
- Compiles Angular application to dist folder
- npm ci ensures reproducible builds
- npm run build:prod creates production bundle

**Stage 2 (Runtime)**:
- Uses minimal `node:18-alpine` again (fresh, clean image)
- ~150MB final size (much smaller than builder)
- Copies only the compiled dist folder from builder
- Installs lightweight `serve` package for static file serving
- Health check ensures container is running

### Building Frontend Images

```bash
# Navigate to project root
cd C:\Veera\AI\agents\SimpleAgent

# Build shell app image
docker build -f digital-banking-ui/Dockerfile -t digital-banking-shell:latest ./digital-banking-ui

# Build MFE images (using template)
docker build -f digital-banking-ui/Dockerfile.mfe -t digital-banking-account-mfe:latest ./digital-banking-ui

# Verify images built
docker images | grep digital-banking

# Expected output:
# digital-banking-shell         latest    abc123...    100MB
# digital-banking-account-mfe   latest    def456...    100MB
```

### Image Size Optimization

Check final image sizes:

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep digital-banking

# Expected sizes (optimized with .dockerignore):
# digital-banking-shell:latest           ~100MB
# digital-banking-account-mfe:latest     ~100MB
# digital-banking-transaction-mfe:latest ~100MB
```

## Phase 2: Complete Stack Deployment

### Prerequisites

```bash
# Ensure Docker and Docker Compose are installed
docker --version    # Docker version 20.10+
docker-compose --version  # Docker Compose version 1.29+

# Clone repository
git clone <repo-url>
cd C:\Veera\AI\agents\SimpleAgent
```

### Deploy with Docker Compose

```bash
# Start all services (infrastructure + backend + frontend)
docker-compose up -d

# Watch logs
docker-compose logs -f

# Verify all services are healthy
docker-compose ps

# Expected output:
# STATUS              PORTS
# healthy            5432/tcp  (PostgreSQL)
# healthy            6379/tcp  (Redis)
# healthy            5672/tcp, 15672/tcp  (RabbitMQ)
# healthy            8000/tcp  (API Gateway)
# healthy            8001/tcp  (Auth Service)
# healthy            8002/tcp  (Account Service)
# healthy            8003/tcp  (Transaction Service)
# healthy            8004/tcp  (Ledger Service)
# healthy            8006/tcp  (Notification Service)
# healthy            4200/tcp  (Shell App)
# healthy            4201/tcp  (Account MFE)
# healthy            4202/tcp  (Transaction MFE)
# healthy            4203/tcp  (Transfer MFE)
# healthy            4204/tcp  (Notification MFE)
# healthy            4205/tcp  (Settings MFE)
```

### Verify Services

```bash
# Check API Gateway health
curl http://localhost:8000/health

# Expected response:
# {"status":"UP","services":{"auth":"UP","account":"UP","transaction":"UP","ledger":"UP"}}

# Check auth service
curl http://localhost:8001/health

# Check all backend services
for port in 8000 8001 8002 8003 8004 8006; do
  echo "Port $port:"
  curl -s http://localhost:$port/health | jq .status
done
```

### Verify Frontend

```bash
# Open in browser
http://localhost:4200

# Shell app should load with:
# ✓ Logo and title
# ✓ Sidebar with 6 navigation items
# ✓ Header with theme toggle and notifications
# ✓ User menu in top right
# ✓ Login form visible (not authenticated yet)
```

## Phase 3: End-to-End Testing

### Test Environment Setup

```bash
# Ensure all services are running
docker-compose ps | grep "healthy"

# Should show 15 healthy services

# Install Cypress and dependencies (if not already done)
cd digital-banking-ui
npm ci

# Verify Cypress is installed
npx cypress --version
```

### Test Execution

#### Run All E2E Tests

```bash
# Open Cypress Test Runner (interactive)
npm run cypress:open

# In the Cypress window:
# 1. Select "E2E Testing"
# 2. Select "Chrome" browser
# 3. Click on test file (e.g., auth.cy.ts)
# 4. Watch tests run in real-time
```

#### Headless Test Execution

```bash
# Run all tests in headless mode (CI-friendly)
npm run test:e2e

# Expected output:
# ✓ Authentication Tests (35 tests)
# ✓ Navigation Tests (45 tests)
# ✓ Accounts Tests (25 tests)
# ✓ Transactions Tests (40 tests)
# ✓ Transfers Tests (30 tests)
# ✓ Notifications Tests (35 tests)
# ✓ Settings Tests (30 tests)
# ✓ API Integration Tests (25 tests)
#
# 265 tests, 265 passed, 0 failed
```

#### Run Specific Test Suite

```bash
# Authentication tests only
npx cypress run --spec "cypress/e2e/auth.cy.ts"

# Navigation and layout tests
npx cypress run --spec "cypress/e2e/navigation.cy.ts"

# Account operations
npx cypress run --spec "cypress/e2e/accounts.cy.ts"

# Transaction management
npx cypress run --spec "cypress/e2e/transactions.cy.ts"

# Transfer flows
npx cypress run --spec "cypress/e2e/transfers.cy.ts"

# Notifications
npx cypress run --spec "cypress/e2e/notifications.cy.ts"

# Settings
npx cypress run --spec "cypress/e2e/settings.cy.ts"

# API integration
npx cypress run --spec "cypress/e2e/api-integration.cy.ts"
```

#### Generate Test Reports

```bash
# Run with video recording
npm run test:e2e:record

# Run with screenshots on failure
npm run test:e2e

# Generate HTML report
npm run test:e2e:report

# View report
open cypress/reports/index.html
```

### Test Coverage

**265+ Test Cases** covering:

1. **Authentication (35 tests)**
   - Login/logout flows
   - Form validation
   - Token management
   - Session persistence
   - Error handling

2. **Navigation (45 tests)**
   - Sidebar navigation
   - Active route highlighting
   - Theme toggle
   - Responsive design
   - MFE loading

3. **Accounts (25 tests)**
   - Account listing
   - Account details
   - Filtering and search
   - Account actions

4. **Transactions (40 tests)**
   - Transaction listing
   - Filtering and sorting
   - Export functionality
   - Pagination

5. **Transfers (30 tests)**
   - Transfer form validation
   - Beneficiary management
   - Scheduled transfers
   - Transfer history

6. **Notifications (35 tests)**
   - Notification panel
   - Filtering and search
   - Preferences
   - ARIA compliance

7. **Settings (30 tests)**
   - Profile settings
   - Security settings
   - Preferences
   - Account management

8. **API Integration (25 tests)**
   - Authentication API
   - Account API
   - Transaction API
   - Error handling
   - Performance baselines

### Test Results Interpretation

**Passing Test Suite**:
```
✓ All tests passing
✓ No console errors
✓ No network failures
✓ All API endpoints responsive
✓ All microservices healthy
```

**Failed Tests**:
```
If tests fail:
1. Check service health: docker-compose ps
2. View service logs: docker-compose logs api-gateway
3. Check network connectivity: curl http://localhost:8000/health
4. Retry failed test: npx cypress run --spec "cypress/e2e/auth.cy.ts"
```

## Phase 4: Debugging & Troubleshooting

### View Service Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api-gateway
docker-compose logs -f auth-service
docker-compose logs -f shell-app

# View logs with tail
docker-compose logs -f --tail=100 api-gateway
```

### Enter Service Container

```bash
# Access shell app container
docker exec -it digital-banking-shell sh

# Access API gateway
docker exec -it api-gateway bash

# List files in shell app
docker exec digital-banking-shell ls -la /app/dist
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U postgres -d banking_db

# List tables
\dt

# View users table
SELECT * FROM users;

# Exit
\q
```

### Redis Access

```bash
# Connect to Redis
docker exec -it redis redis-cli

# Check keys
KEYS *

# Monitor commands
MONITOR

# Exit
EXIT
```

### Network Debugging

```bash
# Check container IP addresses
docker network inspect banking-network

# Test service connectivity
docker exec shell-app curl http://api-gateway:8000/health

# Check DNS resolution
docker exec shell-app nslookup api-gateway
```

## Phase 5: Cleanup & Shutdown

### Stop Services

```bash
# Stop all services but keep containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

### Clean Unused Resources

```bash
# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove unused networks
docker network prune

# Remove unused volumes
docker volume prune
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests with Docker

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start Docker Compose
        run: |
          cd digital-banking-ui
          docker-compose up -d
          sleep 30  # Wait for services to be healthy
      
      - name: Run E2E Tests
        run: |
          cd digital-banking-ui
          npm ci
          npm run test:e2e
      
      - name: Upload Test Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: cypress-reports
          path: digital-banking-ui/cypress/reports/
      
      - name: Cleanup
        if: always()
        run: |
          cd digital-banking-ui
          docker-compose down
```

### Local Development Workflow

```bash
# 1. Start docker-compose
docker-compose up -d

# 2. Develop and make changes
# ... edit code ...

# 3. Build images with changes
docker-compose build --no-cache

# 4. Restart services with new images
docker-compose up -d

# 5. Run tests
npm run test:e2e

# 6. Fix failing tests or code

# 7. Repeat steps 3-6 as needed

# 8. Shutdown
docker-compose down
```

## Performance Considerations

### Image Size Optimization

Current optimized sizes:
- Shell app: ~100MB
- Each MFE: ~100MB
- Total: ~700MB for all frontend services

### Memory Requirements

**Recommended Docker Resources**:
- CPU: 4 cores minimum
- RAM: 8GB recommended
- Disk: 10GB minimum free space

### Timeout Adjustments

For slower systems, increase timeouts in `cypress.config.ts`:

```typescript
defaultCommandTimeout: 15000,        // 15 seconds
pageLoadTimeout: 45000,              // 45 seconds
requestTimeout: 15000,               // 15 seconds
responseTimeout: 15000,              // 15 seconds
```

## Production Deployment

For production deployment:

1. Use production-grade image registry (ECR, GCR, DockerHub)
2. Tag images with version numbers: `digital-banking-shell:v1.0.0`
3. Use `docker-compose.prod.yml` with resource limits
4. Implement health checks with liveness and readiness probes
5. Enable container restart policies
6. Set up centralized logging (ELK Stack, CloudWatch)
7. Implement monitoring and alerting
8. Use reverse proxy (nginx, Traefik) for routing

## Verification Checklist

- [ ] All Docker images built successfully
- [ ] docker-compose up -d completes without errors
- [ ] All 15 services show as "healthy"
- [ ] Frontend accessible at http://localhost:4200
- [ ] API Gateway responds to health check
- [ ] Login works with test credentials
- [ ] Can navigate between sections
- [ ] E2E tests run without failures
- [ ] Performance baselines met (< 5 seconds)
- [ ] No console errors in browser
- [ ] No errors in service logs
- [ ] Theme toggle works correctly
- [ ] Responsive design verified on mobile

## Next Steps

1. ✅ Build Docker images
2. ✅ Deploy with docker-compose
3. ✅ Verify all services healthy
4. ✅ Run E2E test suite
5. ✅ Generate test reports
6. 🔄 Commit and push changes
7. 📦 Set up CI/CD pipeline
8. 🚀 Deploy to production

## Troubleshooting Common Issues

### Issue: "docker-compose: command not found"
```bash
# Install Docker Compose V2
docker compose --version

# Or upgrade docker-compose
pip install --upgrade docker-compose
```

### Issue: Ports already in use
```bash
# Find process using port
lsof -i :4200

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "4300:4200"  # Use 4300 instead of 4200
```

### Issue: Out of memory
```bash
# Increase Docker memory limit
# Docker Desktop → Preferences → Resources → Memory: 8GB

# Or use memory limits in docker-compose.yml
services:
  shell-app:
    mem_limit: 1g
```

### Issue: Services timeout during startup
```bash
# Increase health check timeout in docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:4200"]
  interval: 10s
  timeout: 10s    # Increase from 5s to 10s
  retries: 5      # Increase from 3 to 5
```

## Support & Documentation

- Cypress Docs: https://docs.cypress.io
- Docker Docs: https://docs.docker.com
- Angular Docs: https://angular.io/docs
- Module Federation: https://webpack.js.org/concepts/module-federation/
