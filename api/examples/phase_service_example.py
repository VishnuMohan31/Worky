"""
Example usage of the Phase Service.

This script demonstrates how to use the PhaseService for:
- Creating phases
- Listing phases
- Updating phases
- Tracking phase usage
- Deactivating phases

Note: This is an example script and requires a running database connection.
"""
from uuid import uuid4
from app.services.phase_service import PhaseService
from app.schemas.hierarchy import PhaseCreate, PhaseUpdate
from app.models.user import User


async def example_phase_operations(db_session):
    """
    Example of phase CRUD operations.
    
    Args:
        db_session: AsyncSession database connection
    """
    # Initialize service
    phase_service = PhaseService(db_session)
    
    # Create a mock admin user
    admin_user = User(
        id=uuid4(),
        email="admin@example.com",
        role="Admin",
        client_id=uuid4()
    )
    
    print("=== Phase Service Examples ===\n")
    
    # 1. List all active phases
    print("1. Listing all active phases:")
    phases = await phase_service.list_phases(include_inactive=False, current_user=admin_user)
    for phase in phases:
        print(f"   - {phase.name} (Order: {phase.order}, Color: {phase.color})")
    print()
    
    # 2. Create a new phase
    print("2. Creating a new phase:")
    new_phase_data = PhaseCreate(
        name="Code Review",
        description="Code review and quality assurance phase",
        color="#e74c3c",
        order=5
    )
    try:
        new_phase = await phase_service.create_phase(new_phase_data, admin_user)
        print(f"   ✓ Created phase: {new_phase.name} (ID: {new_phase.id})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    print()
    
    # 3. Update a phase
    print("3. Updating a phase:")
    if phases:
        phase_to_update = phases[0]
        update_data = PhaseUpdate(
            description="Updated description for demonstration"
        )
        try:
            updated_phase = await phase_service.update_phase(
                phase_to_update.id, 
                update_data, 
                admin_user
            )
            print(f"   ✓ Updated phase: {updated_phase.name}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    print()
    
    # 4. Get phase usage count
    print("4. Checking phase usage:")
    if phases:
        phase = phases[0]
        usage_count = await phase_service.get_phase_usage_count(phase.id)
        print(f"   Phase '{phase.name}' is used by {usage_count} tasks/subtasks")
    print()
    
    # 5. Get detailed phase usage
    print("5. Getting detailed phase usage:")
    if phases:
        phase = phases[0]
        try:
            usage_details = await phase_service.get_phase_usage(phase.id)
            print(f"   Phase: {usage_details['phase_name']}")
            print(f"   Total usage: {usage_details['total_count']}")
            print(f"   Tasks: {usage_details['task_count']}")
            print(f"   Subtasks: {usage_details['subtask_count']}")
            if usage_details['task_breakdown']:
                print("   Task breakdown by status:")
                for status, count in usage_details['task_breakdown'].items():
                    print(f"     - {status}: {count}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    print()
    
    # 6. Try to deactivate a phase
    print("6. Attempting to deactivate a phase:")
    if phases:
        phase = phases[0]
        try:
            deactivated = await phase_service.deactivate_phase(phase.id, admin_user)
            print(f"   ✓ Deactivated phase: {deactivated.name}")
        except Exception as e:
            print(f"   ✗ Cannot deactivate: {e}")
    print()
    
    # 7. List all phases including inactive
    print("7. Listing all phases (including inactive):")
    all_phases = await phase_service.list_phases(include_inactive=True, current_user=admin_user)
    for phase in all_phases:
        status = "Active" if phase.is_active else "Inactive"
        print(f"   - {phase.name} ({status})")
    print()


async def example_phase_distribution(db_session, user_story_id):
    """
    Example of phase distribution calculation.
    
    Args:
        db_session: AsyncSession database connection
        user_story_id: UUID of a user story to analyze
    """
    phase_service = PhaseService(db_session)
    
    print("=== Phase Distribution Example ===\n")
    
    # Get phase distribution for a user story
    distribution = await phase_service.get_phase_distribution('userstory', user_story_id)
    
    print(f"Phase distribution for user story {user_story_id}:")
    for item in distribution:
        print(f"   - {item['phase_name']}: {item['count']} tasks/subtasks")
    print()


# Example of role-based access control
async def example_access_control(db_session):
    """
    Example demonstrating role-based access control.
    
    Args:
        db_session: AsyncSession database connection
    """
    phase_service = PhaseService(db_session)
    
    print("=== Access Control Example ===\n")
    
    # Create a non-admin user
    developer_user = User(
        id=uuid4(),
        email="developer@example.com",
        role="Developer",
        client_id=uuid4()
    )
    
    # Try to create a phase as developer (should fail)
    print("1. Attempting to create phase as Developer:")
    phase_data = PhaseCreate(
        name="Unauthorized Phase",
        description="This should fail",
        color="#000000",
        order=99
    )
    try:
        await phase_service.create_phase(phase_data, developer_user)
        print("   ✗ Unexpected: Phase created by non-admin user!")
    except Exception as e:
        print(f"   ✓ Access denied as expected: {e}")
    print()
    
    # Developers can still list phases
    print("2. Listing phases as Developer:")
    try:
        phases = await phase_service.list_phases(current_user=developer_user)
        print(f"   ✓ Developer can view {len(phases)} phases")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    print()


if __name__ == "__main__":
    print("Phase Service Example Script")
    print("=" * 50)
    print("\nThis script demonstrates the Phase Service functionality.")
    print("To run these examples, you need an active database connection.")
    print("\nExample usage:")
    print("  from sqlalchemy.ext.asyncio import create_async_session")
    print("  async with create_async_session() as session:")
    print("      await example_phase_operations(session)")
