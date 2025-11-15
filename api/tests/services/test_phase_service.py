"""
Tests for Phase Service.

These tests validate the core functionality of the PhaseService including:
- Phase CRUD operations
- Usage tracking and statistics
- Admin-only access control
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.phase_service import PhaseService
from app.models.hierarchy import Phase, Task, Subtask
from app.models.user import User
from app.schemas.hierarchy import PhaseCreate, PhaseUpdate
from fastapi import HTTPException


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def admin_user():
    """Create a mock admin user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.role = "Admin"
    user.client_id = uuid4()
    return user


@pytest.fixture
def developer_user():
    """Create a mock developer user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.role = "Developer"
    user.client_id = uuid4()
    return user


@pytest.fixture
def sample_phase():
    """Create a sample phase."""
    phase = Phase(
        id=uuid4(),
        name="Development",
        description="Development phase",
        color="#3498db",
        is_active=True,
        order=1,
        is_deleted=False
    )
    return phase


class TestPhaseServiceCRUD:
    """Test Phase CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_list_phases_active_only(self, mock_db, sample_phase):
        """Test listing only active phases."""
        service = PhaseService(mock_db)
        
        # Mock database response
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_phase]
        mock_db.execute.return_value = mock_result
        
        # Call service
        phases = await service.list_phases(include_inactive=False)
        
        # Verify
        assert len(phases) == 1
        assert phases[0].name == "Development"
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_phase_as_admin(self, mock_db, admin_user):
        """Test creating a phase as admin user."""
        service = PhaseService(mock_db)
        
        # Mock no existing phase with same name
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Create phase data
        phase_data = PhaseCreate(
            name="Testing",
            description="Testing phase",
            color="#1abc9c",
            order=4
        )
        
        # Call service
        phase = await service.create_phase(phase_data, admin_user)
        
        # Verify
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_phase_as_non_admin_fails(self, mock_db, developer_user):
        """Test that non-admin users cannot create phases."""
        service = PhaseService(mock_db)
        
        phase_data = PhaseCreate(
            name="Testing",
            description="Testing phase",
            color="#1abc9c",
            order=4
        )
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await service.create_phase(phase_data, developer_user)
        
        assert exc_info.value.status_code == 403
        assert "Only Admin users can create phases" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_phase_as_admin(self, mock_db, admin_user, sample_phase):
        """Test updating a phase as admin user."""
        service = PhaseService(mock_db)
        
        # Mock get_phase
        with patch.object(service, 'get_phase', return_value=sample_phase):
            # Mock no name conflict
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result
            
            # Update data
            update_data = PhaseUpdate(
                name="Development Updated",
                description="Updated description"
            )
            
            # Call service
            updated_phase = await service.update_phase(sample_phase.id, update_data, admin_user)
            
            # Verify
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deactivate_phase_with_usage_fails(self, mock_db, admin_user, sample_phase):
        """Test that phases in use cannot be deactivated."""
        service = PhaseService(mock_db)
        
        # Mock get_phase
        with patch.object(service, 'get_phase', return_value=sample_phase):
            # Mock usage count > 0
            with patch.object(service, 'get_phase_usage_count', return_value=5):
                # Should raise HTTPException
                with pytest.raises(HTTPException) as exc_info:
                    await service.deactivate_phase(sample_phase.id, admin_user)
                
                assert exc_info.value.status_code == 400
                assert "Cannot deactivate phase" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_deactivate_phase_without_usage_succeeds(self, mock_db, admin_user, sample_phase):
        """Test that phases not in use can be deactivated."""
        service = PhaseService(mock_db)
        
        # Mock get_phase
        with patch.object(service, 'get_phase', return_value=sample_phase):
            # Mock usage count = 0
            with patch.object(service, 'get_phase_usage_count', return_value=0):
                # Call service
                deactivated_phase = await service.deactivate_phase(sample_phase.id, admin_user)
                
                # Verify
                mock_db.commit.assert_called_once()
                mock_db.refresh.assert_called_once()


class TestPhaseServiceUsageTracking:
    """Test phase usage tracking and statistics."""
    
    @pytest.mark.asyncio
    async def test_get_phase_usage_count(self, mock_db, sample_phase):
        """Test getting total usage count for a phase."""
        service = PhaseService(mock_db)
        
        # Mock task count
        task_result = MagicMock()
        task_result.scalar.return_value = 3
        
        # Mock subtask count
        subtask_result = MagicMock()
        subtask_result.scalar.return_value = 5
        
        # Set up execute to return different results
        mock_db.execute.side_effect = [task_result, subtask_result]
        
        # Call service
        count = await service.get_phase_usage_count(sample_phase.id)
        
        # Verify
        assert count == 8  # 3 tasks + 5 subtasks
        assert mock_db.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_phase_usage_breakdown(self, mock_db, sample_phase):
        """Test getting detailed phase usage breakdown."""
        service = PhaseService(mock_db)
        
        # Mock get_phase
        with patch.object(service, 'get_phase', return_value=sample_phase):
            # Mock task breakdown
            task_result = MagicMock()
            task_result.__iter__ = lambda self: iter([
                MagicMock(status="To Do", count=2),
                MagicMock(status="In Progress", count=1)
            ])
            
            # Mock subtask breakdown
            subtask_result = MagicMock()
            subtask_result.__iter__ = lambda self: iter([
                MagicMock(status="To Do", count=3),
                MagicMock(status="Done", count=2)
            ])
            
            # Set up execute
            mock_db.execute.side_effect = [task_result, subtask_result]
            
            # Call service
            usage = await service.get_phase_usage(sample_phase.id)
            
            # Verify
            assert usage["phase_name"] == "Development"
            assert usage["total_count"] == 8  # 3 tasks + 5 subtasks
            assert usage["task_count"] == 3
            assert usage["subtask_count"] == 5
            assert "task_breakdown" in usage
            assert "subtask_breakdown" in usage


def test_phase_service_initialization():
    """Test that PhaseService can be initialized."""
    mock_db = MagicMock(spec=AsyncSession)
    service = PhaseService(mock_db)
    assert service.db == mock_db
