from logging.config import fileConfig
import os
import sys
from pathlib import Path
import asyncio

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import models
from app.db.base import Base
from app.models.user import User
from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask, Phase
from app.models.bug import Bug
from app.models.audit import AuditLog
from app.models.dependency import Dependency
from app.models.documentation import Documentation
from app.models.git import Commit, PullRequest
from app.models.sprint import Sprint, SprintTask

# Alembic Config object
config = context.config

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

DB_USER = os.getenv("DATABASE_USER", "postgres")
DB_PASS = os.getenv("DATABASE_PASSWORD", "postgres")
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = os.getenv("DATABASE_PORT", "5432")
DB_NAME = os.getenv("DATABASE_NAME", "worky")

db_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
config.set_main_option("sqlalchemy.url", db_url)

# Logging config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

# =========================
# Migration functions
# =========================

def do_run_migrations(connection):
    # Disable server default comparison for first migration if needed
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=False,  # <-- prevent crash if sequences/functions missing
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
