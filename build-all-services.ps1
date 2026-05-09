param(
    [switch]$SkipTests = $true
)

$services = @(
    "auth-service",
    "account-service",
    "transaction-service",
    "ledger-service",
    "api-gateway"
)

Write-Host "Building all DigitalBanking services..." -ForegroundColor Cyan
Write-Host ""

foreach ($service in $services) {
    Write-Host "Building $service..." -ForegroundColor Yellow

    Push-Location $service

    if ($SkipTests) {
        mvn clean package -DskipTests
    } else {
        mvn clean package
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "$service built successfully!" -ForegroundColor Green
    } else {
        Write-Host "$service build FAILED!" -ForegroundColor Red
        Pop-Location
        exit 1
    }

    Pop-Location
    Write-Host ""
}

Write-Host "All services built successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "JAR files are ready in:"
foreach ($service in $services) {
    Write-Host "  - $service/target/$service-1.0.0.jar"
}
