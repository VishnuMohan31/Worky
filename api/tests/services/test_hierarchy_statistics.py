"""
Tests for Hierarchy Service statistics and rollup operations.

These tests validate the statistics functionality including:
- Status counts for direct children
- Phase distribution calculations
- Rollup counts for all descendants
- Completion percentage calculations
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.hierarchy_service import HierarchyService
from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask, Phase
from app.models.user import User


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
def sample_user_story():
    """Create a sample user story."""
    return UserStory(
        id=uuid4(),
        usecase_id=uuid4(),
        title="Test User Story",
        description="Test Description",
        status="In Progress",
        is_deleted=False
    )


class TestHierarchyServiceStatistics:
    """Test statistics and rollup operations."""
    
    @pytest.mark.asyncio
    async def test_get_entity_statistics_basic_structure(self, mock_db, admin_user, sample_user_story):
        """Test that get_entity_statistics returns the correct structure."""
        service = HierarchyService(mock_db)
        
        # Mock the verification and helper methods
        with patch.object(service, '_verify_entity_access', return_value=None):
            with patch.object(service, '_get_status_counts', return_value={'To Do': 3, 'In Progress': 2, 'Done': 5}):
                with patch.object(service, '_get_phase_distribution', return_value=[
                    {'phase': 'Development', 'color': '#3498db', 'count': 5},
                    {'phase': 'Testing', 'color': '#1abc9c', 'count': 3}
                ]):
                    with patch.object(service, '_get_rollup_counts', return_value={'tasks': 10, 'subtasks': 5}):
                        # Call service
                        stats = await service.get_entity_statistics('userstory', sample_user_story.id, admin_user)
                        
                        # Verify structure
                        assert 'status_counts' in stats
                        assert 'phase_distribution' in stats
                        assert 'rollup_counts' in stats
                        assert 'completion_percentage' in stats
                        assert 'total_items' in stats
                        
                        # Verify values
                        assert stats['status_counts'] == {'To Do': 3, 'In Progress': 2, 'Done': 5}
                        assert stats['total_items'] == 10
                        assert stats['completion_percentage'] == 50.0  # 5 done out of 10 total
    
    @pytest.mark.asyncio
    async def test_get_entity_statistics_completion_percentage_zero_items(self, mock_db, admin_user, sample_user_story):
        """Test completion percentage calculation when there are no items."""
        service = HierarchyService(mock_db)
        
        # Mock the verification and helper methods with no items
        with patch.object(service, '_verify_entity_access', return_value=None):
            with patch.object(service, '_get_status_counts', return_value={}):
                with patch.object(service, '_get_phase_distribution', return_value=[]):
                    with patch.object(service, '_get_rollup_counts', return_value={}):
                        # Call service
                        stats = await service.get_entity_statistics('userstory', sample_user_story.id, admin_user)
                        
                        # Verify completion percentage is 0 when no items
                        assert stats['completion_percentage'] == 0.0
                        assert stats['total_items'] == 0
    
    @pytest.mark.asyncio
    async def test_get_entity_statistics_completion_percentage_all_completed(self, mock_db, admin_user, sample_user_story):
        """Test completion percentage calculation when all items are completed."""
        service = HierarchyService(mock_db)
        
        # Mock the verification and helper methods with all completed
        with patch.object(service, '_verify_entity_access', return_value=None):
            with patch.object(service, '_get_status_counts', return_value={'Done': 10}):
                with patch.object(service, '_get_phase_distribution', return_value=[]):
                    with patch.object(service, '_get_rollup_counts', return_value={'tasks': 10}):
                        # Call service
                        stats = await service.get_entity_statistics('userstory', sample_user_story.id, admin_user)
                        
                        # Verify completion percentage is 100 when all done
                        assert stats['completion_percentage'] == 100.0
                        assert stats['total_items'] == 10
    
    @pytest.mark.asyncio
    async def test_get_entity_statistics_no_phase_distribution_for_task(self, mock_db, admin_user):
        """Test that phase distribution is None for task entities."""
        service = HierarchyService(mock_db)
        task_id = uuid4()
        
        # Mock the verification and helper methods
        with patch.object(service, '_verify_entity_access', return_value=None):
            with patch.object(service, '_get_status_counts', return_value={'To Do': 2, 'Done': 3}):
                with patch.object(service, '_get_phase_distribution', return_value=None):
                    with patch.object(service, '_get_rollup_counts', return_value={'subtasks': 5}):
                        # Call service for a task (should not have phase distribution)
                        stats = await service.get_entity_statistics('task', task_id, admin_user)
                        
                        # Verify phase distribution is None for tasks
                        assert stats['phase_distribution'] is None
    
    @pytest.mark.asyncio
    async def test_get_status_counts_for_subtask_returns_empty(self, mock_db):
        """Test that status counts for subtask returns empty dict (no children)."""
        service = HierarchyService(mock_db)
        subtask_id = uuid4()
        
        # Call service
        status_counts = await service._get_status_counts('subtask', subtask_id)
        
        # Verify empty dict for subtask (no children)
        assert status_counts == {}
    
    @pytest.mark.asyncio
    async def test_get_rollup_counts_for_subtask_returns_empty(self, mock_db):
        """Test that rollup counts for subtask returns empty dict (no descendants)."""
        service = HierarchyService(mock_db)
        subtask_id = uuid4()
        
        # Call service
        rollup_counts = await service._get_rollup_counts('subtask', subtask_id)
        
        # Verify empty dict for subtask (no descendants)
        assert rollup_counts == {}


class TestPhaseDistribution:
    """Test phase distribution calculations."""
    
    @pytest.mark.asyncio
    async def test_get_descendant_task_ids_for_task(self, mock_db):
        """Test getting descendant task IDs for a task entity."""
        service = HierarchyService(mock_db)
        task_id = uuid4()
        
        # Call service
        task_ids = await service._get_descendant_task_ids('task', task_id)
        
        # Verify task returns itself
        assert task_ids == [task_id]
    
    @pytest.mark.asyncio
    async def test_get_descendant_task_ids_for_subtask(self, mock_db):
        """Test getting descendant task IDs for a subtask entity."""
        service = HierarchyService(mock_db)
        subtask_id = uuid4()
        
        # Call service
        task_ids = await service._get_descendant_task_ids('subtask', subtask_id)
        
        # Verify subtask returns empty list (no tasks under subtasks)
        assert task_ids == []


def test_hierarchy_service_statistics_initialization():
    """Test that HierarchyService can be initialized for statistics operations."""
    mock_db = MagicMock(spec=AsyncSession)
    service = HierarchyService(mock_db)
    assert service.db == mock_db
    assert hasattr(service, 'get_entity_statistics')
    assert hasattr(service, '_get_status_counts')
    assert hasattr(service, '_get_phase_distribution')
    assert hasattr(service, '_get_rollup_counts')
