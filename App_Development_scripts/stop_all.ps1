# PowerShell script to stop all Worky services on Windows
# Usage: .\stop_all.ps1

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "`n🛑 Stopping All Worky Services..." -ForegroundColor Cyan
Write-Host "=" * 60

# Stop Docker services
Write-Host "`n1️⃣ Stopping Docker services..." -ForegroundColor Yellow
Set-Location $RootDir

# Check for docker-compose command
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    docker-compose down
} else {
    docker compose down
}

Write-Host "✓ Docker services stopped" -ForegroundColor Green

# Kill any running node processes for UI (vite)
Write-Host "`n2️⃣ Stopping UI processes..." -ForegroundColor Yellow
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
    $_.MainWindowTitle -like "*vite*" -or $_.MainWindowTitle -like "*worky*"
}

if ($nodeProcesses) {
    $nodeProcesses | Stop-Process -Force
    Write-Host "✓ UI processes stopped" -ForegroundColor Green
} else {
    Write-Host "   No UI processes found running" -ForegroundColor Gray
}

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "✅ All Worky Services Stopped!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

