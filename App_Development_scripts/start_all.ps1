# PowerShell script to start all Worky services on Windows
# Usage: .\start_all.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "`n🚀 Starting All Worky Services..." -ForegroundColor Cyan
Write-Host "=" * 60

# Function to check if a command exists
function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-CommandExists "docker")) {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

if (-not (Test-CommandExists "docker-compose")) {
    # Try docker compose (v2 syntax)
    $dockerComposeCmd = "docker compose"
} else {
    $dockerComposeCmd = "docker-compose"
}

if (-not (Test-CommandExists "node")) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✓ All prerequisites found" -ForegroundColor Green

# Start Database and API via Docker Compose
Write-Host "`n1️⃣ Starting Database and API (Docker)..." -ForegroundColor Yellow
Set-Location $RootDir

# Check if containers are already running
$existingDb = docker ps --filter "name=worky-postgres" --format "{{.Names}}" 2>$null
$existingApi = docker ps --filter "name=worky-api" --format "{{.Names}}" 2>$null

if ($existingDb -or $existingApi) {
    Write-Host "   Found existing containers. Restarting..." -ForegroundColor Yellow
    Invoke-Expression "$dockerComposeCmd down"
}

# Start services
Invoke-Expression "$dockerComposeCmd up -d --build"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Docker services" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Database and API started" -ForegroundColor Green

# Wait for API to be healthy
Write-Host "`n   Waiting for API to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$apiReady = $false

while (-not $apiReady -and $attempt -lt $maxAttempts) {
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8007/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $apiReady = $true
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

if ($apiReady) {
    Write-Host "✓ API is ready and healthy" -ForegroundColor Green
} else {
    Write-Host "⚠️ API health check timed out (may still be starting)" -ForegroundColor Yellow
}

# Start UI
Write-Host "`n2️⃣ Starting UI (Vite)..." -ForegroundColor Yellow
Set-Location "$RootDir\ui"

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing UI dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install UI dependencies" -ForegroundColor Red
        exit 1
    }
}

# Create logs directory
$logsDir = "$RootDir\logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

# Start UI in a new PowerShell window
Write-Host "   Starting UI dev server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RootDir\ui'; npm run dev"

Write-Host "✓ UI started in new terminal window" -ForegroundColor Green

# Display summary
Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ All Worky Services Started!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Services:" -ForegroundColor White
Write-Host "   Database: localhost:5437 (PostgreSQL in Docker)" -ForegroundColor Gray
Write-Host "   API:      http://localhost:8007" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8007/docs" -ForegroundColor Gray
Write-Host "   UI:       http://localhost:3007" -ForegroundColor Gray

Write-Host "`n🔐 Login Credentials:" -ForegroundColor White
Write-Host "   Email:    admin@datalegos.com" -ForegroundColor Gray
Write-Host "   Password: password" -ForegroundColor Gray

Write-Host "`n📝 View Logs:" -ForegroundColor White
Write-Host "   API:  docker logs worky-api -f" -ForegroundColor Gray
Write-Host "   DB:   docker logs worky-postgres -f" -ForegroundColor Gray

Write-Host "`n🛑 Stop All Services:" -ForegroundColor White
Write-Host "   .\App_Development_scripts\stop_all.ps1" -ForegroundColor Gray
Write-Host ""

