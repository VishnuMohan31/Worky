# Worky API

FastAPI backend for the Worky project management system.

## Structure

```
api/
├── app/              # Application code
├── tests/            # Test files
├── scripts/          # Utility scripts
├── alembic/          # Database migrations (Alembic)
├── logs/             # Application logs
├── requirements.txt  # Python dependencies
└── Dockerfile        # Docker configuration
```

## Quick Start

```bash
# Start API with Docker
docker-compose up -d api

# Access API docs
http://localhost:8007/docs
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000
```

## Scripts

- `scripts/run_reminder_job.py` - Background job for processing reminders
- `scripts/migrate.sh` - Database migration helper
- `scripts/start_server.sh` - Server startup script
