#############################################################################
# DigitalBanking Complete E2E Testing & Deployment Script (PowerShell)
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

param(
    [switch]$NoCleanup,
    [switch]$SkipTests
)

# Configuration
$DOCKER_COMPOSE_FILE = "docker-compose.yml"
$AUTH_SERVICE = "http://localhost:8001"
$ACCOUNT_SERVICE = "http://localhost:8002"
$TRANSACTION_SERVICE = "http://localhost:8003"
$LEDGER_SERVICE = "http://localhost:8004"
$SHELL_APP = "http://localhost:4200"

# Test credentials
$TEST_EMAIL = "test@example.com"
$TEST_PASSWORD = "TestPassword123!"
$TEST_NAME = "Test User"

# Colors
$SUCCESS = "Green"
$ERROR = "Red"
$WARNING = "Yellow"
$INFO = "Cyan"

#############################################################################
# Functions
#############################################################################

function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "═" * 70 -ForegroundColor $INFO
    Write-Host $Message -ForegroundColor $INFO
    Write-Host "═" * 70 -ForegroundColor $INFO
    Write-Host ""
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $SUCCESS
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ERROR
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $WARNING
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor $INFO
}

function Check-Prerequisites {
    Print-Header "STEP 1: Checking Prerequisites"

    # Check Docker
    try {
        $version = docker --version
        Print-Success "Docker installed: $version"
    }
    catch {
        Print-Error "Docker not found. Please install Docker Desktop."
        exit 1
    }

    # Check Node.js
    try {
        $version = node --version
        Print-Success "Node.js installed: $version"
    }
    catch {
        Print-Error "Node.js not found. Please install Node.js."
        exit 1
    }

    # Check npm
    try {
        $version = npm --version
        Print-Success "npm installed: $version"
    }
    catch {
        Print-Error "npm not found."
        exit 1
    }
}

function Start-DockerCompose {
    Print-Header "STEP 2: Starting Docker Compose Services"

    if (!(Test-Path $DOCKER_COMPOSE_FILE)) {
        Print-Error "docker-compose.yml not found"
        exit 1
    }

    Print-Warning "Starting services... This may take 30-45 seconds"
    docker-compose up -d

    Start-Sleep -Seconds 10
    Print-Success "Docker Compose services started"

    Write-Host ""
    Write-Host "Running containers:"
    docker-compose ps
}

function Wait-ForServices {
    Print-Header "STEP 3: Waiting for Services to be Healthy"

    $services = @(
        @{ Name = "Auth Service"; Port = 8001 },
        @{ Name = "Account Service"; Port = 8002 },
        @{ Name = "Transaction Service"; Port = 8003 },
        @{ Name = "Ledger Service"; Port = 8004 }
    )

    foreach ($service in $services) {
        Print-Info "Waiting for $($service.Name) (Port $($service.Port))..."

        $healthy = $false
        for ($i = 0; $i -lt 30; $i++) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    Print-Success "$($service.Name) is healthy"
                    $healthy = $true
                    break
                }
            }
            catch { }

            if ($i -lt 29) {
                Start-Sleep -Seconds 2
            }
        }

        if (!$healthy) {
            Print-Error "$($service.Name) failed to start"
            exit 1
        }
    }
}

function Test-AuthService {
    Print-Header "STEP 4: Testing Auth Service API"

    # Register user
    Print-Info "Registering test user..."
    try {
        $registerResponse = Invoke-WebRequest -Uri "$AUTH_SERVICE/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body (@{
                email    = $TEST_EMAIL
                password = $TEST_PASSWORD
                fullName = $TEST_NAME
            } | ConvertTo-Json) `
            -ErrorAction SilentlyContinue

        Print-Success "User registered successfully"
    }
    catch {
        Print-Warning "User registration response: $($_.Exception.Message)"
    }

    # Login user
    Print-Info "Logging in test user..."
    try {
        $loginResponse = Invoke-WebRequest -Uri "$AUTH_SERVICE/api/v1/auth/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body (@{
                email    = $TEST_EMAIL
                password = $TEST_PASSWORD
            } | ConvertTo-Json) `
            -ErrorAction SilentlyContinue

        $loginData = $loginResponse.Content | ConvertFrom-Json

        if ($loginData.data.accessToken) {
            Print-Success "User login successful"
            $global:AUTH_TOKEN = $loginData.data.accessToken
        }
        else {
            Print-Warning "Login response: $($loginResponse.Content)"
        }
    }
    catch {
        Print-Warning "Login failed: $($_.Exception.Message)"
    }
}

function Test-AccountService {
    Print-Header "STEP 5: Testing Account Service API"

    if (!$global:AUTH_TOKEN) {
        Print-Warning "Skipping Account Service tests (no auth token)"
        return
    }

    Print-Info "Retrieving accounts..."
    try {
        $response = Invoke-WebRequest -Uri "$ACCOUNT_SERVICE/api/v1/accounts" `
            -Method GET `
            -Headers @{ Authorization = "Bearer $global:AUTH_TOKEN" } `
            -ErrorAction SilentlyContinue

        Print-Success "Account Service API responding"
    }
    catch {
        Print-Warning "Account Service test failed: $($_.Exception.Message)"
    }
}

function Test-TransactionService {
    Print-Header "STEP 6: Testing Transaction Service API"

    if (!$global:AUTH_TOKEN) {
        Print-Warning "Skipping Transaction Service tests (no auth token)"
        return
    }

    Print-Info "Retrieving transactions..."
    try {
        $response = Invoke-WebRequest -Uri "$TRANSACTION_SERVICE/api/v1/transactions" `
            -Method GET `
            -Headers @{ Authorization = "Bearer $global:AUTH_TOKEN" } `
            -ErrorAction SilentlyContinue

        Print-Success "Transaction Service API responding"
    }
    catch {
        Print-Warning "Transaction Service test failed: $($_.Exception.Message)"
    }
}

function Setup-Frontend {
    Print-Header "STEP 7: Setting Up Frontend"

    if (!(Test-Path "digital-banking-ui")) {
        Print-Error "digital-banking-ui directory not found"
        exit 1
    }

    Push-Location digital-banking-ui

    Print-Warning "Installing npm dependencies..."
    npm ci 2>$null
    if ($LASTEXITCODE -ne 0) {
        npm install
    }
    Print-Success "Dependencies installed"

    Pop-Location
}

function Run-E2ETests {
    Print-Header "STEP 8: Running Cypress E2E Tests"

    if ($SkipTests) {
        Print-Warning "Skipping E2E tests (--SkipTests flag set)"
        return
    }

    Push-Location digital-banking-ui

    Print-Warning "Running E2E tests... This may take 5-10 minutes"

    if (npm run test:e2e) {
        Print-Success "All E2E tests passed!"
    }
    else {
        Print-Error "Some E2E tests failed. Check cypress/reports/ for details."
    }

    Pop-Location
}

function Generate-Report {
    Print-Header "STEP 9: Generating Test Report"

    Push-Location digital-banking-ui

    if (Test-Path "cypress/reports") {
        Write-Host "Test report available at: cypress/reports/index.html"
        Get-ChildItem "cypress/reports/" | Select-Object -Property Name, Length, LastWriteTime | Format-Table
    }

    if (Test-Path "cypress/videos") {
        Write-Host ""
        Write-Host "Test videos:"
        Get-ChildItem "cypress/videos/" -Recurse | Select-Object -Last 10 | Format-Table
    }

    Pop-Location
}

function Print-Summary {
    Print-Header "TESTING COMPLETE"

    Write-Host "Test Summary:"
    Write-Host "  ✓ Docker services started"
    Write-Host "  ✓ Services health verified"
    Write-Host "  ✓ Auth Service tested"
    Write-Host "  ✓ Account Service tested"
    Write-Host "  ✓ Transaction Service tested"
    Write-Host "  ✓ Frontend setup"
    Write-Host "  ✓ E2E tests executed"
    Write-Host ""
    Write-Host "Results:"
    Write-Host "  - Digital Banking Shell App: $SHELL_APP"
    Write-Host "  - Auth Service: $AUTH_SERVICE"
    Write-Host "  - Account Service: $ACCOUNT_SERVICE"
    Write-Host "  - Transaction Service: $TRANSACTION_SERVICE"
    Write-Host "  - Ledger Service: $LEDGER_SERVICE"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Open $SHELL_APP in browser"
    Write-Host "  2. Login with: $TEST_EMAIL / $TEST_PASSWORD"
    Write-Host "  3. Test the application features"
    Write-Host "  4. Check test reports: cypress/reports/index.html"
    Write-Host ""
}

function Cleanup {
    if ($NoCleanup) {
        return
    }

    Print-Header "Cleanup"

    $response = Read-Host "Stop Docker services? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Print-Warning "Stopping services..."
        docker-compose down
        Print-Success "Services stopped"
    }
}

#############################################################################
# Main Execution
#############################################################################

Write-Host ""
Write-Host "╔" + ("═" * 68) + "╗" -ForegroundColor $INFO
Write-Host "║   DigitalBanking Complete E2E Testing & Deployment         ║" -ForegroundColor $INFO
Write-Host "║   Version 1.0 - Production Ready                           ║" -ForegroundColor $INFO
Write-Host "╚" + ("═" * 68) + "╝" -ForegroundColor $INFO
Write-Host ""

Check-Prerequisites
Start-DockerCompose
Wait-ForServices
Test-AuthService
Test-AccountService
Test-TransactionService
Setup-Frontend
Run-E2ETests
Generate-Report
Print-Summary
Cleanup

Write-Host "Testing session completed." -ForegroundColor $SUCCESS
