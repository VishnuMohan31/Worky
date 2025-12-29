# Stop All Worky Services (PowerShell)
# Usage: .\stop_all.ps1

Write-Host "Stopping All Worky Services..." -ForegroundColor Cyan

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

# Navigate to project root
Set-Location $PROJECT_ROOT

# Stop UI (kill any npm/node processes for Vite)
Write-Host ""
Write-Host "1. Stopping UI..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*vite*" -or $_.CommandLine -like "*vite*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

# Also try to stop by port
$viteProcess = Get-NetTCPConnection -LocalPort 3007 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique
if ($viteProcess) {
    Stop-Process -Id $viteProcess -Force -ErrorAction SilentlyContinue
}
Write-Host "OK - UI stopped" -ForegroundColor Green

# Stop Docker services
Write-Host ""
Write-Host "2. Stopping Docker services (API and Database)..." -ForegroundColor Yellow
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - Docker services stopped" -ForegroundColor Green
} else {
    Write-Host "WARNING - Some services may not have stopped cleanly" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "All Worky Services Stopped!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start again:" -ForegroundColor Blue
Write-Host "   .\App_Development_scripts\start_all.ps1"



