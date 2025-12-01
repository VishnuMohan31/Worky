"""
Database utilities for Excel data loader.

This module provides database connection management and session handling
for the Excel import process, reusing the existing Worky database configuration.
"""

import sys
import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Add the API directory to the path to import existing config
api_path = Path(__file__).resolve().parent.parent.parent.parent / "api"
sys.path.insert(0, str(api_path))

from app.core.config import settings


class DatabaseConfig:
    """Database configuration for Excel loader."""
    
    # Connection pooling settings
    POOL_SIZE = 5
    MAX_OVERFLOW = 10
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600  # Recycle connections after 1 hour
    
    # Import-specific settings
    EXCEL_UPLOAD_MAX_SIZE = 50 * 1024 * 1024  # 50MB
    EXCEL_IMPORT_TIMEOUT = 300  # 5 minutes


# Global engine instance
_engine: AsyncEngine | None = None
_async_session_maker: sessionmaker | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the async database engine.
    
    Returns:
        AsyncEngine: The SQLAlchemy async engine instance
    """
    global _engine
    
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.DEBUG,
            future=True,
            poolclass=QueuePool,
            pool_size=DatabaseConfig.POOL_SIZE,
            max_overflow=DatabaseConfig.MAX_OVERFLOW,
            pool_timeout=DatabaseConfig.POOL_TIMEOUT,
            pool_recycle=DatabaseConfig.POOL_RECYCLE,
            pool_pre_ping=True,  # Verify connections before using
        )
    
    return _engine


def get_session_maker() -> sessionmaker:
    """
    Get or create the async session maker.
    
    Returns:
        sessionmaker: The SQLAlchemy session maker
    """
    global _async_session_maker
    
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    This function provides an async context manager for database sessions,
    handling commits, rollbacks, and cleanup automatically.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        async with get_db() as session:
            # Use session here
            pass
    """
    session_maker = get_session_maker()
    
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """
    Get a new database session.
    
    This is a simpler alternative to get_db() for cases where you want
    to manage the session lifecycle manually.
    
    Returns:
        AsyncSession: A new database session
        
    Note:
        The caller is responsible for committing/rolling back and closing the session.
    """
    session_maker = get_session_maker()
    return session_maker()


async def close_engine():
    """
    Close the database engine and cleanup resources.
    
    This should be called when shutting down the application.
    """
    global _engine, _async_session_maker
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None


async def test_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        async with get_db() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
