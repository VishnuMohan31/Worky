#!/usr/bin/env python3
"""
Script to make phase_id nullable in tasks and subtasks tables.

This is needed for the Excel import to work properly since the Excel files
don't contain phase information.
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Database configuration
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5437"))
DATABASE_NAME = os.getenv("DATABASE_NAME", "worky")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"


async def make_phase_id_nullable():
    """Make phase_id nullable in tasks and subtasks tables."""
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("Making phase_id nullable in tasks table...")
            await conn.execute(text("""
                ALTER TABLE tasks 
                ALTER COLUMN phase_id DROP NOT NULL
            """))
            print("✓ tasks.phase_id is now nullable")
            
            print("\nMaking phase_id nullable in subtasks table...")
            await conn.execute(text("""
                ALTER TABLE subtasks 
                ALTER COLUMN phase_id DROP NOT NULL
            """))
            print("✓ subtasks.phase_id is now nullable")
            
            print("\n✓ Migration completed successfully!")
            
    except Exception as e:
        print(f"\n✗ Error during migration: {str(e)}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("Making phase_id nullable in tasks and subtasks tables")
    print("=" * 60)
    print()
    
    asyncio.run(make_phase_id_nullable())
