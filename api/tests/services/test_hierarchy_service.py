"""
Tests for Hierarchy Service update and delete operations.

These tests validate the core functionality of update and delete methods including:
- Entity update operations
- Soft delete operations with cascade checks
- Role-based access control
- Cache invalidation placeholders
"""
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.hierarchy_service import HierarchyService
from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask
from app.models.user import User
from app.schemas.client import ClientUpdate
from app.schemas.hierarchy import ProgramUpdate, UsecaseUpdate, UserStoryUpdate, SubtaskUpdate
from app.schemas.project import ProjectUpdate
from app.schemas.task import TaskUpdate
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
def architect_user():
    """Create a mock architect user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.role = "Architect"
    user.client_id = uuid4()
    return user


@pytest.fixture
def sample_client():
    """Create a sample client."""
    client = Client(
        id=uuid4(),
        name="Test Client",
        description="Test Description",
        is_active=True,
        is_deleted=False
    )
    return client


@pytest.fixture
def sample_program(sample_client):
    """Create a sample program."""
    program = Program(
        id=uuid4(),
        client_id=sample_client.id,
        name="Test Program",
        description="Test Description",
        status="Planning",
        is_deleted=False
    )
    program.client = sample_client
    program.projects = []
    return program


@pytest.fixture
def sample_task():
    """Create a sample task."""
    task = Task(
        id=uuid4(),
        user_story_id=uuid4(),
        title="Test Task",
        description="Test Description",
        status="To Do",
        priority="Medium",
        is_deleted=False
    )
    task.subtasks = []
    return task


class TestHierarchyServiceUpdate:
    """Test entity update operations."""
    
    @pytest.mark.asyncio
    async def test_update_client_as_admin(self, mock_db, admin_user, sample_client):
        """Test updating a client as admin user."""
        service = HierarchyService(mock_db)
        
        # Mock get_and_verify_client_access
        with patch.object(service, '_get_and_verify_client_access', return_value=sample_client):
            # Update data
            update_data = ClientUpdate(
                name="Updated Client Name",
                description="Updated Description"
            )
            
            # Call service
            updated_client = await service.update_client(sample_client.id, update_data, admin_user)
            
            # Verify
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_client_as_non_admin_fails(self, mock_db, developer_user, sample_client):
        """Test that non-admin users cannot update clients."""
        service = HierarchyService(mock_db)
        
        update_data = ClientUpdate(name="Updated Name")
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await service.update_client(sample_client.id, update_data, developer_user)
        
        assert exc_info.value.status_code == 403
        assert "Only Admin users can update clients" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_program_as_architect(self, mock_db, architect_user, sample_program):
        """Test updating a program as architect user."""
        service = HierarchyService(mock_db)
        
        # Mock get_and_verify_program_access
        with patch.object(service, '_get_and_verify_program_access', return_value=sample_program):
            # Update data
            update_data = ProgramUpdate(
                name="Updated Program Name",
                status="Active"
            )
            
            # Call service
            updated_program = await service.update_program(sample_program.id, update_data, architect_user)
            
            # Verify
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_as_developer_assigned(self, mock_db, developer_user, sample_task):
        """Test that developers can update tasks assigned to them."""
        service = HierarchyService(mock_db)
        
        # Set task as assigned to developer
        sample_task.assigned_to = developer_user.id
        
        # Mock get_and_verify_task_access
        with patch.object(service, '_get_and_verify_task_access', return_value=sample_task):
            # Update data
            update_data = TaskUpdate(
                status="In Progress",
                actual_hours=2.5
            )
            
            # Call service
            updated_task = await service.update_task(sample_task.id, update_data, developer_user)
            
            # Verify
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_as_developer_not_assigned_fails(self, mock_db, developer_user, sample_task):
        """Test that developers cannot update tasks not assigned to them."""
        service = HierarchyService(mock_db)
        
        # Set task as assigned to someone else
        sample_task.assigned_to = uuid4()
        
        # Mock get_and_verify_task_access
        with patch.object(service, '_get_and_verify_task_access', return_value=sample_task):
            update_data = TaskUpdate(status="In Progress")
            
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await service.update_task(sample_task.id, update_data, developer_user)
            
            assert exc_info.value.status_code == 403
            assert "Developers can only update tasks assigned to them" in str(exc_info.value.detail)


class TestHierarchyServiceDelete:
    """Test soft delete operations."""
    
    @pytest.mark.asyncio
    async def test_delete_client_as_admin_no_children(self, mock_db, admin_user, sample_client):
        """Test deleting a client with no active children."""
        service = HierarchyService(mock_db)
        
        # Mock get_and_verify_client_access
        with patch.object(service, '_get_and_verify_client_access', return_value=sample_client):
            # Mock check_active_children (no children)
            with patch.object(service, '_check_active_children', return_value=None):
                # Call service
                result = await service.delete_client(sample_client.id, admin_user)
                
                # Verify
                assert "deleted" in result["message"]
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_client_as_non_admin_fails(self, mock_db, developer_user, sample_client):
        """Test that non-admin users cannot delete clients."""
        service = HierarchyService(mock_db)
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_client(sample_client.id, developer_user)
        
        assert exc_info.value.status_code == 403
        assert "Only Admin users can delete clients" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_program_with_active_children_fails(self, mock_db, admin_user, sample_program):
        """Test that programs with active children cannot be deleted."""
        service = HierarchyService(mock_db)
        
        # Add active project to program
        active_project = Project(
            id=uuid4(),
            program_id=sample_program.id,
            name="Active Project",
            is_deleted=False
        )
        sample_program.projects = [active_project]
        
        # Mock get_and_verify_program_access
        with patch.object(service, '_get_and_verify_program_access', return_value=sample_program):
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await service.delete_program(sample_program.id, admin_user)
            
            assert exc_info.value.status_code == 400
            assert "cannot be deleted because it has" in str(exc_info.value.detail)
            assert "active child entities" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_program_with_deleted_children_succeeds(self, mock_db, admin_user, sample_program):
        """Test that programs with only deleted children can be deleted."""
        service = HierarchyService(mock_db)
        
        # Add deleted project to program
        deleted_project = Project(
            id=uuid4(),
            program_id=sample_program.id,
            name="Deleted Project",
            is_deleted=True
        )
        sample_program.projects = [deleted_project]
        
        # Mock get_and_verify_program_access
        with patch.object(service, '_get_and_verify_program_access', return_value=sample_program):
            # Mock check_active_children (only deleted children)
            with patch.object(service, '_check_active_children', return_value=None):
                # Call service
                result = await service.delete_program(sample_program.id, admin_user)
                
                # Verify
                assert "deleted" in result["message"]
                mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_task_as_developer_fails(self, mock_db, developer_user, sample_task):
        """Test that developers cannot delete tasks."""
        service = HierarchyService(mock_db)
        
        # Mock get_and_verify_task_access
        with patch.object(service, '_get_and_verify_task_access', return_value=sample_task):
            # Should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await service.delete_task(sample_task.id, developer_user)
            
            assert exc_info.value.status_code == 403
            assert "Developers cannot delete tasks" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_delete_task_as_admin_no_children(self, mock_db, admin_user, sample_task):
        """Test deleting a task with no active children."""
        service = HierarchyService(mock_db)
        
        # Mock get_and_verify_task_access
        with patch.object(service, '_get_and_verify_task_access', return_value=sample_task):
            # Mock check_active_children (no children)
            with patch.object(service, '_check_active_children', return_value=None):
                # Call service
                result = await service.delete_task(sample_task.id, admin_user)
                
                # Verify
                assert "deleted" in result["message"]
                mock_db.commit.assert_called_once()


class TestCascadeChecks:
    """Test cascade delete validation."""
    
    @pytest.mark.asyncio
    async def test_check_active_children_with_active_children(self, mock_db):
        """Test that _check_active_children raises exception when active children exist."""
        service = HierarchyService(mock_db)
        
        # Create entity with active children
        entity = MagicMock()
        entity.children = [
            MagicMock(is_deleted=False),
            MagicMock(is_deleted=False),
            MagicMock(is_deleted=True)  # One deleted child
        ]
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await service._check_active_children(entity, "children", "Test Entity")
        
        assert exc_info.value.status_code == 400
        assert "2 active child entities" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_check_active_children_with_no_children(self, mock_db):
        """Test that _check_active_children passes when no children exist."""
        service = HierarchyService(mock_db)
        
        # Create entity with no children
        entity = MagicMock()
        entity.children = []
        
        # Should not raise exception
        await service._check_active_children(entity, "children", "Test Entity")
    
    @pytest.mark.asyncio
    async def test_check_active_children_with_only_deleted_children(self, mock_db):
        """Test that _check_active_children passes when only deleted children exist."""
        service = HierarchyService(mock_db)
        
        # Create entity with only deleted children
        entity = MagicMock()
        entity.children = [
            MagicMock(is_deleted=True),
            MagicMock(is_deleted=True)
        ]
        
        # Should not raise exception
        await service._check_active_children(entity, "children", "Test Entity")


def test_hierarchy_service_initialization():
    """Test that HierarchyService can be initialized."""
    mock_db = MagicMock(spec=AsyncSession)
    service = HierarchyService(mock_db)
    assert service.db == mock_db
