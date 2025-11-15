# Worky API - FastAPI Backend

A high-performance async FastAPI backend for the Worky project management platform.

## Features

✅ **FastAPI** - Modern async Python web framework
✅ **PostgreSQL** - Relational database with async support
✅ **SQLAlchemy 2.0** - Async ORM
✅ **JWT Authentication** - Secure token-based auth
✅ **Role-Based Access Control** - 7 user roles with permissions
✅ **Pydantic** - Data validation and settings management
✅ **Alembic** - Database migrations
✅ **Prometheus** - Metrics collection
✅ **Structured Logging** - JSON logs with correlation IDs

## Quick Start

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Set up PostgreSQL Database

```bash
# Create database
createdb worky

# Run migrations
cd ../db
psql -U postgres -d worky -f migrations/001_initial_schema.sql
psql -U postgres -d worky -f migrations/002_supporting_tables.sql

# Load seed data (optional)
psql -U postgres -d worky -f seeds/dev_data.sql
```

### 3. Configure Environment

Create `.env` file in `api/` directory:

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=worky
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services (optional)
GITHUB_TOKEN=your_github_token
DISCORD_WEBHOOK_URL=your_discord_webhook
```

### 4. Run the API

```bash
cd api
uvicorn app.main:app --reload --port 8000
```

API will be available at: **http://localhost:8000**

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── clients.py
│   │       │   ├── projects.py
│   │       │   ├── tasks.py
│   │       │   └── ...
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   └── base.py
│   ├── models/
│   │   ├── user.py
│   │   ├── client.py
│   │   └── ...
│   ├── schemas/
│   │   └── (Pydantic models)
│   ├── services/
│   │   └── (Business logic)
│   └── main.py
├── requirements.txt
└── .env
```

## Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@datalegos.com", "password": "password"}'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@datalegos.com",
    "full_name": "Admin User",
    "role": "Admin"
  }
}
```

### Use Token

```bash
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Schema

The database follows a hierarchical structure:

```
Client
  └── Program
        └── Project
              └── Usecase
                    └── User Story
                          └── Task
                                └── Subtask
```

Supporting tables:
- `users` - User accounts with roles
- `dependencies` - Cross-entity dependencies
- `commits` - Git commit tracking
- `bugs` - Bug reports
- `documentation` - Versioned docs
- `audit_logs` - Audit trail
- `sprints` - Agile sprints

## Next Steps

1. **Complete Model Implementation** - Finish all SQLAlchemy models
2. **Create API Endpoints** - Implement CRUD for all entities
3. **Add Business Logic** - Services for complex operations
4. **Implement Git Integration** - GitHub/GitLab webhooks
5. **Add Monitoring** - Prometheus metrics and Grafana dashboards
6. **Write Tests** - Unit and integration tests

## Development

### Run with Auto-reload

```bash
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
pytest
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Production Deployment

See `../infra/ansible/` for deployment playbooks.

## API Endpoints (Planned)

- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/clients` - List clients
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task
- `PUT /api/v1/tasks/{id}` - Update task
- `GET /api/v1/bugs` - List bugs
- `POST /api/v1/bugs` - Create bug
- And many more...

## Notes

This is the backend foundation. The UI is already connected and will work once you:
1. Set up the database
2. Run the API server
3. Update `USE_DUMMY_DATA = false` in `ui/src/services/api.ts`
