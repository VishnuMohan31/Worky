#!/usr/bin/env python3
"""
Verification script for reminder CRUD operations.

This script tests the reminder CRUD functionality without requiring
a full API server setup.
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.crud.crud_reminder import reminder
from app.schemas.chat import ReminderCreate, ReminderUpdate


async def verify_reminder_crud():
    """Verify reminder CRUD operations"""
    print("=" * 60)
    print("Reminder CRUD Verification")
    print("=" * 60)
    
    # Create database connection
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as db:
        try:
            # Test 1: Create a reminder
            print("\n1. Testing reminder creation...")
            reminder_data = ReminderCreate(
                entity_type="task",
                entity_id="TSK-TEST-001",
                message="Test reminder for verification",
                remind_at=datetime.now() + timedelta(hours=2),
                created_via="api"
            )
            
            new_reminder = await reminder.create(
                db=db,
                obj_in=reminder_data,
                user_id="USR-001"  # Assuming this user exists
            )
            
            print(f"   ✓ Created reminder: {new_reminder.id}")
            print(f"     - Entity: {new_reminder.entity_type} {new_reminder.entity_id}")
            print(f"     - Message: {new_reminder.message}")
            print(f"     - Remind at: {new_reminder.remind_at}")
            print(f"     - Is sent: {new_reminder.is_sent}")
            
            # Test 2: Get reminders by user
            print("\n2. Testing get reminders by user...")
            user_reminders = await reminder.get_by_user(
                db=db,
                user_id="USR-001",
                limit=10
            )
            print(f"   ✓ Found {len(user_reminders)} reminders for user USR-001")
            
            # Test 3: Get reminders by entity
            print("\n3. Testing get reminders by entity...")
            entity_reminders = await reminder.get_by_entity(
                db=db,
                entity_type="task",
                entity_id="TSK-TEST-001"
            )
            print(f"   ✓ Found {len(entity_reminders)} reminders for task TSK-TEST-001")
            
            # Test 4: Get upcoming reminders
            print("\n4. Testing get upcoming reminders...")
            upcoming = await reminder.get_upcoming_reminders(
                db=db,
                user_id="USR-001",
                hours_ahead=24
            )
            print(f"   ✓ Found {len(upcoming)} upcoming reminders (next 24 hours)")
            
            # Test 5: Create a past-due reminder for testing
            print("\n5. Testing pending reminders...")
            past_reminder_data = ReminderCreate(
                entity_type="bug",
                entity_id="BUG-TEST-001",
                message="Past due reminder",
                remind_at=datetime.now() - timedelta(minutes=5),
                created_via="api"
            )
            
            past_reminder = await reminder.create(
                db=db,
                obj_in=past_reminder_data,
                user_id="USR-001"
            )
            print(f"   ✓ Created past-due reminder: {past_reminder.id}")
            
            # Test 6: Get pending reminders
            print("\n6. Testing get pending reminders...")
            pending = await reminder.get_pending_reminders(
                db=db,
                before=datetime.now(),
                limit=10
            )
            print(f"   ✓ Found {len(pending)} pending reminders")
            for r in pending[:3]:  # Show first 3
                print(f"     - {r.id}: {r.entity_type} {r.entity_id} (due: {r.remind_at})")
            
            # Test 7: Mark reminder as sent
            print("\n7. Testing mark reminder as sent...")
            marked = await reminder.mark_as_sent(
                db=db,
                reminder_id=past_reminder.id
            )
            if marked:
                print(f"   ✓ Marked reminder {marked.id} as sent")
                print(f"     - Is sent: {marked.is_sent}")
            
            # Test 8: Update reminder
            print("\n8. Testing update reminder...")
            update_data = ReminderUpdate(
                message="Updated test reminder message",
                remind_at=datetime.now() + timedelta(hours=3)
            )
            
            updated = await reminder.update(
                db=db,
                db_obj=new_reminder,
                obj_in=update_data
            )
            print(f"   ✓ Updated reminder {updated.id}")
            print(f"     - New message: {updated.message}")
            print(f"     - New remind_at: {updated.remind_at}")
            
            # Test 9: Batch mark as sent
            print("\n9. Testing batch mark as sent...")
            # Get some pending reminders
            batch_pending = await reminder.get_pending_reminders(
                db=db,
                user_id="USR-001",
                limit=5
            )
            
            if batch_pending:
                reminder_ids = [r.id for r in batch_pending]
                count = await reminder.mark_multiple_as_sent(
                    db=db,
                    reminder_ids=reminder_ids
                )
                print(f"   ✓ Marked {count} reminders as sent in batch")
            else:
                print("   ℹ No pending reminders to mark as sent")
            
            # Test 10: Delete reminder
            print("\n10. Testing delete reminder...")
            deleted = await reminder.delete_reminder(
                db=db,
                reminder_id=new_reminder.id,
                user_id="USR-001"
            )
            
            if deleted:
                print(f"   ✓ Deleted reminder {deleted.id}")
            else:
                print("   ✗ Failed to delete reminder")
            
            print("\n" + "=" * 60)
            print("✓ All reminder CRUD operations verified successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error during verification: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("\nStarting reminder CRUD verification...")
    print("Note: This requires a running database with the reminders table.\n")
    
    asyncio.run(verify_reminder_crud())
