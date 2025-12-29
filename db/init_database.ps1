# Database Initialization Script (PowerShell)
# This script initializes or resets the Worky database with all migrations
# Usage: .\init_database.ps1 [-Reset] [-ForceReset]
#
# IMPORTANT: For a fresh clone on a new device, always use -Reset flag
# to ensure clean database initialization with all migrations.

param(
    [switch]$Reset,
    [switch]$ForceReset
)

# Database connection details
$DB_CONTAINER = "worky-postgres"
$DB_NAME = "worky"
$DB_USER = "postgres"

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR

Write-Host "=== Worky Database Initialization ===" -ForegroundColor Blue
Write-Host ""

# Check if Docker is running
try {
    docker info 2>&1 | Out-Null
} catch {
    Write-Host "Error: Docker is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again."
    exit 1
}

# Navigate to project root for docker-compose
Set-Location $PROJECT_ROOT

# Reset database if requested
if ($Reset -or $ForceReset) {
    if (-not $ForceReset) {
        Write-Host "WARNING: Reset mode enabled - This will destroy all existing data!" -ForegroundColor Yellow
        $confirm = Read-Host "Are you sure you want to continue? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "Aborted" -ForegroundColor Red
            exit 0
        }
    } else {
        Write-Host "WARNING: Force reset mode - destroying all data without confirmation" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Stopping and removing database container and volumes..." -ForegroundColor Yellow
    docker-compose down -v 2>$null
    
    Write-Host "OK - Database container and volumes removed" -ForegroundColor Green
    Write-Host "Starting fresh database container..." -ForegroundColor Yellow
    docker-compose up -d db
    
    # Wait for database to be ready
    Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Wait for health check
    for ($i = 1; $i -le 60; $i++) {
        $ready = docker exec $DB_CONTAINER pg_isready -U $DB_USER 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "OK - Database is ready" -ForegroundColor Green
            break
        }
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 1
    }
    Write-Host ""
    
    # Wait for migrations to complete
    Write-Host "Waiting for migrations to complete..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check if migrations completed
    for ($i = 1; $i -le 30; $i++) {
        $tableCount = docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>$null
        $tableCount = $tableCount.Trim()
        if ([int]$tableCount -gt 20) {
            Write-Host "OK - Migrations completed ($tableCount tables created)" -ForegroundColor Green
            break
        }
        Write-Host -NoNewline "."
        Start-Sleep -Seconds 2
    }
    Write-Host ""
    
    Write-Host "OK - Fresh database created with all migrations" -ForegroundColor Green
    Write-Host ""
} else {
    # Check if container is running
    $running = docker ps | Select-String $DB_CONTAINER
    if (-not $running) {
        Write-Host "Database container is not running. Starting..." -ForegroundColor Yellow
        docker-compose up -d db
        
        # Wait for database to be ready
        Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
        for ($i = 1; $i -le 60; $i++) {
            $ready = docker exec $DB_CONTAINER pg_isready -U $DB_USER 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "OK - Database is ready" -ForegroundColor Green
                break
            }
            Write-Host -NoNewline "."
            Start-Sleep -Seconds 1
        }
        Write-Host ""
    } else {
        Write-Host "OK - Database container is running" -ForegroundColor Green
    }
}

# Verify migrations
Write-Host ""
Write-Host "Verifying migration files..." -ForegroundColor Yellow
$migrationFiles = Get-ChildItem "$SCRIPT_DIR\migrations\*.sql" -ErrorAction SilentlyContinue
$migrationCount = $migrationFiles.Count
Write-Host "Found $migrationCount migration files" -ForegroundColor Green

# List all tables in the database
Write-Host ""
Write-Host "Checking database tables..." -ForegroundColor Yellow
$tables = docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" 2>$null
$tables = $tables.Trim()

if ([int]$tables -gt 0) {
    Write-Host "OK - Found $tables tables in database" -ForegroundColor Green
} else {
    Write-Host "X - No tables found in database" -ForegroundColor Red
    Write-Host "This might indicate migrations haven't run yet" -ForegroundColor Yellow
    Write-Host "Try running: .\db\init_database.ps1 -Reset" -ForegroundColor Yellow
}

# Check for seed data
Write-Host ""
Write-Host "Checking for seed data..." -ForegroundColor Yellow
$userCount = docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM users;" 2>$null
$userCount = $userCount.Trim()
if ([int]$userCount -gt 0) {
    Write-Host "OK - Found $userCount users (seed data present)" -ForegroundColor Green
} else {
    Write-Host "WARNING - No users found - seed data may not have loaded" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Blue
Write-Host "Database: $DB_NAME" -ForegroundColor Green
Write-Host "Container: $DB_CONTAINER" -ForegroundColor Green
Write-Host "Total tables: $tables" -ForegroundColor Green
Write-Host "Migration files: $migrationCount" -ForegroundColor Green
Write-Host "Users: $userCount" -ForegroundColor Green

# Connection info
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Blue
Write-Host "  Host: localhost"
Write-Host "  Port: 5437"
Write-Host "  Database: $DB_NAME"
Write-Host "  User: $DB_USER"
Write-Host "  Password: postgres"

Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Blue
Write-Host "  View logs:        docker-compose logs db" -ForegroundColor Yellow
Write-Host "  Connect to DB:    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME" -ForegroundColor Yellow
Write-Host "  List tables:      docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c '\dt'" -ForegroundColor Yellow
Write-Host "  Reset database:   .\db\init_database.ps1 -Reset" -ForegroundColor Yellow



