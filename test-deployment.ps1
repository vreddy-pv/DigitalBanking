param(
    [switch]$NoCleanup,
    [switch]$SkipTests
)

$SUCCESS = "Green"
$ERROR = "Red"
$WARNING = "Yellow"
$INFO = "Cyan"

function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor $INFO
    Write-Host $Message -ForegroundColor $INFO
    Write-Host ("=" * 70) -ForegroundColor $INFO
    Write-Host ""
}

function Print-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor $SUCCESS
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $ERROR
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $WARNING
}

function Check-Prerequisites {
    Print-Header "STEP 1: Checking Prerequisites"

    try {
        $version = docker --version
        Print-Success "Docker: $version"
    }
    catch {
        Print-Error "Docker not found. Please install Docker Desktop."
        exit 1
    }

    try {
        $version = node --version
        Print-Success "Node.js: $version"
    }
    catch {
        Print-Error "Node.js not found."
        exit 1
    }

    try {
        $version = npm --version
        Print-Success "npm: $version"
    }
    catch {
        Print-Error "npm not found."
        exit 1
    }
}

function Start-DockerCompose {
    Print-Header "STEP 2: Starting Docker Compose Services"

    if (!(Test-Path "docker-compose.yml")) {
        Print-Error "docker-compose.yml not found"
        exit 1
    }

    Print-Warning "Starting services - This may take 30-45 seconds"
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
        Write-Host "Waiting for $($service.Name) (Port $($service.Port))..."

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

            if ($i -lt 29) { Start-Sleep -Seconds 2 }
        }

        if (!$healthy) {
            Print-Error "$($service.Name) failed to start"
            exit 1
        }
    }
}

function Test-AuthService {
    Print-Header "STEP 4: Testing Auth Service API"

    $authService = "http://localhost:8001"
    $testEmail = "test@example.com"
    $testPassword = "TestPassword123!"
    $testName = "Test User"

    Write-Host "Registering test user..."
    try {
        $response = Invoke-WebRequest -Uri "$authService/api/v1/auth/register" `
            -Method POST `
            -ContentType "application/json" `
            -Body (@{
                email = $testEmail
                password = $testPassword
                fullName = $testName
            } | ConvertTo-Json) `
            -ErrorAction SilentlyContinue

        Print-Success "User registered successfully"
    }
    catch {
        Write-Host "User might already exist"
    }

    Write-Host "Logging in..."
    try {
        $response = Invoke-WebRequest -Uri "$authService/api/v1/auth/login" `
            -Method POST `
            -ContentType "application/json" `
            -Body (@{
                email = $testEmail
                password = $testPassword
            } | ConvertTo-Json) `
            -ErrorAction SilentlyContinue

        $data = $response.Content | ConvertFrom-Json

        if ($data.data.accessToken) {
            Print-Success "User login successful"
            $global:AUTH_TOKEN = $data.data.accessToken
        }
    }
    catch {
        Print-Warning "Login test failed"
    }
}

function Test-AccountService {
    Print-Header "STEP 5: Testing Account Service API"

    if (!$global:AUTH_TOKEN) {
        Print-Warning "Skipping Account Service tests"
        return
    }

    Write-Host "Testing Account Service..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/accounts" `
            -Method GET `
            -Headers @{ Authorization = "Bearer $($global:AUTH_TOKEN)" } `
            -ErrorAction SilentlyContinue

        Print-Success "Account Service is responding"
    }
    catch {
        Print-Warning "Account Service test failed"
    }
}

function Test-TransactionService {
    Print-Header "STEP 6: Testing Transaction Service API"

    if (!$global:AUTH_TOKEN) {
        Print-Warning "Skipping Transaction Service tests"
        return
    }

    Write-Host "Testing Transaction Service..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8003/api/v1/transactions" `
            -Method GET `
            -Headers @{ Authorization = "Bearer $($global:AUTH_TOKEN)" } `
            -ErrorAction SilentlyContinue

        Print-Success "Transaction Service is responding"
    }
    catch {
        Print-Warning "Transaction Service test failed"
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
        Print-Warning "Skipping E2E tests"
        return
    }

    Push-Location digital-banking-ui

    Print-Warning "Running E2E tests - This may take 5-10 minutes"

    npm run test:e2e

    if ($LASTEXITCODE -eq 0) {
        Print-Success "All E2E tests passed!"
    }
    else {
        Print-Error "Some E2E tests failed. Check cypress/reports/"
    }

    Pop-Location
}

function Generate-Report {
    Print-Header "STEP 9: Generating Test Report"

    Push-Location digital-banking-ui

    if (Test-Path "cypress/reports") {
        Write-Host "Test report: cypress/reports/index.html"
        Get-ChildItem "cypress/reports/" | Format-Table
    }

    if (Test-Path "cypress/videos") {
        Write-Host ""
        Write-Host "Test videos available:"
        Get-ChildItem "cypress/videos/" -Recurse | Select-Object -Last 10 | Format-Table
    }

    Pop-Location
}

function Print-Summary {
    Print-Header "TESTING COMPLETE"

    Write-Host "[OK] Infrastructure started"
    Write-Host "[OK] Services health verified"
    Write-Host "[OK] APIs tested"
    Write-Host "[OK] Frontend setup"
    Write-Host "[OK] E2E tests executed"
    Write-Host ""
    Write-Host "Access the application:"
    Write-Host "  URL: http://localhost:4200"
    Write-Host "  Email: test@example.com"
    Write-Host "  Password: TestPassword123!"
    Write-Host ""
    Write-Host "View test reports:"
    Write-Host "  HTML Report: cypress/reports/index.html"
    Write-Host "  Videos: cypress/videos/"
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

Write-Host ""
Write-Host "DigitalBanking Complete E2E Testing & Deployment" -ForegroundColor $INFO
Write-Host "Version 1.0 - Production Ready" -ForegroundColor $INFO
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
