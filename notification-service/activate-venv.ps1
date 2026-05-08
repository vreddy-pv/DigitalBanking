# PowerShell activation script for notification-service virtual environment

Write-Host "Activating notification-service virtual environment..." -ForegroundColor Green

# Get the directory of this script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate the virtual environment
& "$scriptDir\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""
Write-Host "Python: $(python --version)"
Write-Host "Pip: $(pip --version)"
Write-Host ""
Write-Host "Available commands:"
Write-Host "  uvicorn    - Run ASGI server"
Write-Host "  pytest     - Run tests"
Write-Host "  alembic    - Database migrations"
Write-Host "  python     - Python interpreter"
Write-Host ""
Write-Host "To deactivate: deactivate"
