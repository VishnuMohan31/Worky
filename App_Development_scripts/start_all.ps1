# Start All Worky Services (PowerShell)
# Usage: .\start_all.ps1

Write-Host "Starting All Worky Services..." -ForegroundColor Cyan

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

# Navigate to project root
Set-Location $PROJECT_ROOT

# Start Database and API via Docker
Write-Host ""
Write-Host "1. Starting Database and API (Docker)..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "X - Docker services failed to start" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Database and API started" -ForegroundColor Green

# Wait for services to be healthy
Write-Host ""
Write-Host "2. Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check database
$dbReady = docker exec worky-postgres pg_isready -U postgres 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Database is healthy" -ForegroundColor Green
} else {
    Write-Host "WARNING - Database may still be starting" -ForegroundColor Yellow
}

# Check API
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8007/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "OK - API is healthy" -ForegroundColor Green
} catch {
    Write-Host "WARNING - API may still be starting" -ForegroundColor Yellow
}

# Start UI
Write-Host ""
Write-Host "3. Starting UI..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\ui"

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing UI dependencies..." -ForegroundColor Yellow
    npm install
}

# Start UI in a new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\ui'; npm run dev"
Write-Host "OK - UI started in new window" -ForegroundColor Green

# Return to project root
Set-Location $PROJECT_ROOT

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "All Worky Services Started!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor Blue
Write-Host "   Database: localhost:5437 (Docker)"
Write-Host "   API:      http://localhost:8007"
Write-Host "   UI:       http://localhost:3007"
Write-Host ""
Write-Host "Login:" -ForegroundColor Blue
Write-Host "   Email:    admin@datalegos.com"
Write-Host "   Password: password"
Write-Host ""
Write-Host "Logs:" -ForegroundColor Blue
Write-Host "   API: docker logs worky-api -f"
Write-Host "   DB:  docker logs worky-postgres -f"
Write-Host ""
Write-Host "Stop:" -ForegroundColor Blue
Write-Host "   .\App_Development_scripts\stop_all.ps1"



