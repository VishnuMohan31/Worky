# Apply Database Migrations (PowerShell)
# This script applies migrations to running Worky PostgreSQL container
# Usage: .\apply_migrations.ps1 [migration_file]

param(
    [string]$MigrationFile
)

# Database connection details
$DB_CONTAINER = "worky-postgres"
$DB_NAME = "worky"
$DB_USER = "postgres"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Worky Database Migration Tool ===" -ForegroundColor Green
Write-Host ""

# Check if container is running
$running = docker ps | Select-String $DB_CONTAINER
if (-not $running) {
    Write-Host "Error: Database container '$DB_CONTAINER' is not running" -ForegroundColor Red
    Write-Host "Start it with: docker-compose up -d db"
    exit 1
}

# If migration file is provided, apply only that migration
if ($MigrationFile) {
    $fullPath = Join-Path $SCRIPT_DIR "migrations\$MigrationFile"
    if (-not (Test-Path $fullPath)) {
        Write-Host "Error: Migration file '$fullPath' not found" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Applying migration: $MigrationFile" -ForegroundColor Yellow
    Get-Content $fullPath | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
    Write-Host "OK - Migration applied successfully" -ForegroundColor Green
    exit 0
}

# Apply all migrations in order
Write-Host "Applying all migrations..." -ForegroundColor Yellow
Write-Host ""

$migrations = Get-ChildItem "$SCRIPT_DIR\migrations\*.sql" | Sort-Object Name

foreach ($migration in $migrations) {
    Write-Host "Applying: $($migration.Name)" -ForegroundColor Yellow
    
    $result = Get-Content $migration.FullName | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME 2>&1
    
    if ($result -match "ERROR") {
        Write-Host "  WARNING - Error or already applied (continuing)" -ForegroundColor Yellow
    } else {
        Write-Host "  OK - Applied successfully" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Migration process complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To verify, run:" -ForegroundColor Blue
Write-Host "  docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c '\dt'"



