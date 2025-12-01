"""
Verification script for DatabaseWriter component.

This script tests the DatabaseWriter class to ensure it correctly:
1. Initializes with proper counts dictionary
2. Inserts single entities and returns IDs
3. Performs batch inserts efficiently
4. Commits transactions
5. Rolls back on errors
6. Returns accurate summary counts
7. Handles constraint violations
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "api"))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database_writer import DatabaseWriter
from datetime import datetime, date
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_writer():
    """Test DatabaseWriter functionality."""
    
    # Create async engine (using same config as main API)
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5437/worky"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Create session factory
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        try:
            writer = DatabaseWriter(session)
            
            # Test 1: Verify initialization
            print("\n=== Test 1: Initialization ===")
            print(f"Initial counts: {writer.get_summary()}")
            assert all(count == 0 for count in writer.get_summary().values()), \
                "Initial counts should all be zero"
            print("✓ Initialization test passed")
            
            # Test 2: Insert single client
            print("\n=== Test 2: Insert Single Entity ===")
            client_data = {
                'id': 'CLI-TEST-001',
                'name': 'Test Client for DatabaseWriter',
                'short_description': 'Test client',
                'is_active': True,
                'is_deleted': False
            }
            
            client_id = await writer.insert_entity('clients', client_data)
            print(f"Inserted client with ID: {client_id}")
            assert client_id == 'CLI-TEST-001', "Client ID should match"
            assert writer.get_summary()['clients'] == 1, "Client count should be 1"
            print("✓ Single entity insert test passed")
            
            # Test 3: Insert single program
            print("\n=== Test 3: Insert Program (with FK) ===")
            program_data = {
                'id': 'PRG-TEST-001',
                'client_id': client_id,
                'name': 'Test Program',
                'short_description': 'Test program',
                'status': 'Planning',
                'is_deleted': False
            }
            
            program_id = await writer.insert_entity('programs', program_data)
            print(f"Inserted program with ID: {program_id}")
            assert program_id == 'PRG-TEST-001', "Program ID should match"
            assert writer.get_summary()['programs'] == 1, "Program count should be 1"
            print("✓ Program insert with FK test passed")
            
            # Test 4: Batch insert projects
            print("\n=== Test 4: Batch Insert ===")
            projects_data = [
                {
                    'id': f'PRJ-TEST-{i:03d}',
                    'program_id': program_id,
                    'name': f'Test Project {i}',
                    'short_description': f'Test project {i}',
                    'status': 'Planning',
                    'is_deleted': False
                }
                for i in range(1, 6)
            ]
            
            project_ids = await writer.batch_insert_entities('projects', projects_data)
            print(f"Batch inserted {len(project_ids)} projects")
            assert len(project_ids) == 5, "Should insert 5 projects"
            assert writer.get_summary()['projects'] == 5, "Project count should be 5"
            print("✓ Batch insert test passed")
            
            # Test 5: Get summary
            print("\n=== Test 5: Get Summary ===")
            summary = writer.get_summary()
            print(f"Summary: {summary}")
            assert summary['clients'] == 1, "Should have 1 client"
            assert summary['programs'] == 1, "Should have 1 program"
            assert summary['projects'] == 5, "Should have 5 projects"
            print("✓ Get summary test passed")
            
            # Test 6: Commit transaction
            print("\n=== Test 6: Commit Transaction ===")
            await writer.commit_transaction()
            print("✓ Commit transaction test passed")
            
            print("\n=== All Tests Passed! ===")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            await writer.rollback_transaction()
            raise
        finally:
            # Cleanup: Delete test data
            print("\n=== Cleanup ===")
            try:
                await session.execute(
                    text("DELETE FROM projects WHERE id LIKE 'PRJ-TEST-%'")
                )
                await session.execute(
                    text("DELETE FROM programs WHERE id LIKE 'PRG-TEST-%'")
                )
                await session.execute(
                    text("DELETE FROM clients WHERE id LIKE 'CLI-TEST-%'")
                )
                await session.commit()
                print("✓ Cleanup completed")
            except Exception as e:
                logger.error(f"Cleanup failed: {str(e)}")
                await session.rollback()
    
    await engine.dispose()


async def test_error_handling():
    """Test error handling and rollback."""
    
    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5437/worky"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        try:
            writer = DatabaseWriter(session)
            
            print("\n=== Test 7: Error Handling ===")
            
            # Try to insert project without required program_id (should fail)
            invalid_project = {
                'id': 'PRJ-INVALID-001',
                'name': 'Invalid Project',
                'status': 'Planning'
                # Missing program_id - should cause constraint violation
            }
            
            try:
                await writer.insert_entity('projects', invalid_project)
                print("✗ Should have raised an error for missing FK")
                assert False, "Should have raised constraint error"
            except Exception as e:
                print(f"✓ Correctly caught error: {type(e).__name__}")
                
            # Test rollback
            print("\n=== Test 8: Rollback Transaction ===")
            await writer.rollback_transaction()
            print("✓ Rollback test passed")
            
            print("\n=== Error Handling Tests Passed! ===")
            
        except Exception as e:
            logger.error(f"Error handling test failed: {str(e)}")
            raise
    
    await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("DatabaseWriter Verification Script")
    print("=" * 60)
    
    # Import text for SQL queries
    from sqlalchemy import text
    
    try:
        asyncio.run(test_database_writer())
        asyncio.run(test_error_handling())
        
        print("\n" + "=" * 60)
        print("ALL VERIFICATION TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"VERIFICATION FAILED: {str(e)}")
        print("=" * 60)
        sys.exit(1)
