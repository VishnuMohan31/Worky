# Worky Development Scripts

This folder contains scripts to start, stop, and manage the Worky application services.

## Prerequisites

- **Docker Desktop** installed and running
- **Node.js 18+** installed (for UI development)

## Quick Start

### Windows (PowerShell)

```powershell
# Start all services
.\start_all.ps1

# Stop all services
.\stop_all.ps1
```

### macOS/Linux (Bash)

```bash
# Make scripts executable (one-time)
chmod +x *.sh

# Start all services
./start_all.sh

# Stop all services
./stop_all.sh
```

## Available Scripts

### Start Scripts

| Script | Description |
|--------|-------------|
| `start_all.sh` / `start_all.ps1` | Start all services (Database, API, UI) |
| `start_db.sh` | Start PostgreSQL database only |
| `start_api.sh` | Start API server only |
| `start_ui.sh` | Start UI development server only |

### Stop Scripts

| Script | Description |
|--------|-------------|
| `stop_all.sh` / `stop_all.ps1` | Stop all services |
| `stop_db.sh` | Stop database only |
| `stop_api.sh` | Stop API server only |
| `stop_ui.sh` | Stop UI development server only |

### Restart Scripts

| Script | Description |
|--------|-------------|
| `restart_all.sh` | Restart all services |
| `restart_db.sh` | Restart database only |
| `restart_api.sh` | Rebuild and restart API |
| `restart_ui.sh` | Restart UI development server |

### Utility Scripts

| Script | Description |
|--------|-------------|
| `db_shell.sh` | Open PostgreSQL shell |

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| PostgreSQL | 5437 | `localhost:5437` |
| API | 8007 | http://localhost:8007 |
| API Docs | 8007 | http://localhost:8007/docs |
| UI | 3007 | http://localhost:3007 |

## Default Login

- **Email**: `admin@datalegos.com`
- **Password**: `password`

## Troubleshooting

### Docker not running

Make sure Docker Desktop is running before executing any scripts.

### Port already in use

If you get port conflict errors:

```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :3007

# macOS/Linux:
lsof -i :3007
```

### Database issues

```bash
# Reset database completely
cd ../db
./init_database.sh --reset   # or .\init_database.ps1 -Reset on Windows
```

### Logs

```bash
# View API logs
docker logs worky-api -f

# View database logs
docker logs worky-postgres -f

# View UI logs (if running in background)
tail -f ../logs/ui.log
```

