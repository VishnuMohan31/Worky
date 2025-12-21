#!/usr/bin/env python3
"""
Direct assignment test to isolate the async context error
"""
import asyncio
import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.team import Assignment
from app.core.utils import generate_id

async def test_direct_assignment():
    """Test direct assignment creation with async SQLAlchemy"""
    
    # Create async engine
    DATABASE_URL = "postgresql+asyncpg://worky_user:worky_password@localhost:5432/worky_db"
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Create async session
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        try:
            print("Creating assignment object...")
            
            assignment = Assignment(
                id=generate_id("TEST"),
                entity_type="task",
                entity_id="TSK-000001",
                user_id="USR-004",
                assignment_type="developer",
                created_by="USR-001",
                updated_by="USR-001"
            )
            
            print("Adding to session...")
            session.add(assignment)
            
            print("Committing...")
            await session.commit()
            
            print("Refreshing...")
            await session.refresh(assignment)
            
            print(f"✅ Assignment created successfully: {assignment.id}")
            
            # Clean up
            print("Cleaning up...")
            await session.delete(assignment)
            await session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating assignment: {str(e)}")
            await session.rollback()
            return False
        finally:
            await session.close()

if __name__ == "__main__":
    success = asyncio.run(test_direct_assignment())
    if success:
        print("✅ Direct assignment test passed")
    else:
        print("❌ Direct assignment test failed")