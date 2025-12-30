"""
Tests for Hierarchy Service search functionality.

These tests validate the search_entities method including:
- Full-text search across entity types
- Entity type filtering
- Pagination
- Hierarchy path generation
- Client-level filtering for non-Admin users
"""
import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.hierarchy_service import HierarchyService
from app.models.client import Client
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask
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
def developer_user():
    """Create a mock developer user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.role = "Developer"
    user.client_id = uuid4()
    return user


@pytest.fixture
def sample_client():
    """Create a sample client."""
    client = Client(
        id=uuid4(),
        name="Acme Corporation",
        description="Test client for search",
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
        name="Digital Transformation",
        description="Program for digital transformation",
        status="Active",
        is_deleted=False
    )
    return program


@pytest.fixture
def sample_project(sample_program):
    """Create a sample project."""
    project = Project(
        id=uuid4(),
        program_id=sample_program.id,
        name="E-commerce Platform",
        description="Building an e-commerce platform",
        status="In Progress",
        is_deleted=False
    )
    return project


class TestSearchEntities:
    """Test class for search_entities method."""
    
    @pytest.mark.asyncio
    async def test_search_entities_basic(self, mock_db, admin_user, sample_client, sample_program):
        """Test basic search functionality."""
        service = HierarchyService(mock_db)
        
        # Mock the _search_entity_type method to return sample results
        with patch.object(service, '_search_entity_type', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {
                    "entity_type": "client",
                    "id": str(sample_client.id),
                    "name": "Acme Corporation",
                    "status": None,
                    "description": "Test client for search"
                }
            ]
            
            # Mock _generate_hierarchy_path
            with patch.object(service, '_generate_hierarchy_path', new_callable=AsyncMock) as mock_path:
                mock_path.return_value = "Acme Corporation"
                
                # Execute search with specific entity type
                result = await service.search_entities(
                    query="Acme",
                    entity_types=['client'],  # Specify entity type to get predictable results
                    current_user=admin_user,
                    page=1,
                    page_size=50
                )
                
                # Verify results
                assert result['total'] == 1
                assert result['page'] == 1
                assert result['page_size'] == 50
                assert len(result['results']) == 1
                assert result['results'][0]['name'] == "Acme Corporation"
                assert result['results'][0]['hierarchy_path'] == "Acme Corporation"
    
    @pytest.mark.asyncio
    async def test_search_entities_with_type_filter(self, mock_db, admin_user):
        """Test search with entity type filtering."""
        service = HierarchyService(mock_db)
        
        # Mock the _search_entity_type method
        with patch.object(service, '_search_entity_type', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []
            
            # Execute search with type filter
            result = await service.search_entities(
                query="test",
                entity_types=['program', 'project'],
                current_user=admin_user,
                page=1,
                page_size=50
            )
            
            # Verify that only specified types were searched
            assert mock_search.call_count == 2
            call_args = [call[0][0] for call in mock_search.call_args_list]
            assert 'program' in call_args
            assert 'project' in call_args
    
    @pytest.mark.asyncio
    async def test_search_entities_pagination(self, mock_db, admin_user):
        """Test search pagination."""
        service = HierarchyService(mock_db)
        
        # Create mock results (10 items)
        mock_results = [
            {
                "entity_type": "program",
                "id": str(uuid4()),
                "name": f"Program {i}",
                "status": "Active",
                "description": f"Description {i}"
            }
            for i in range(10)
        ]
        
        with patch.object(service, '_search_entity_type', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_results
            
            with patch.object(service, '_generate_hierarchy_path', new_callable=AsyncMock) as mock_path:
                mock_path.return_value = "Test Path"
                
                # Test page 1 with page_size 5
                result = await service.search_entities(
                    query="Program",
                    entity_types=['program'],
                    current_user=admin_user,
                    page=1,
                    page_size=5
                )
                
                assert result['total'] == 10
                assert result['page'] == 1
                assert result['page_size'] == 5
                assert len(result['results']) == 5
                assert result['total_pages'] == 2
                
                # Test page 2
                result = await service.search_entities(
                    query="Program",
                    entity_types=['program'],
                    current_user=admin_user,
                    page=2,
                    page_size=5
                )
                
                assert len(result['results']) == 5
                assert result['page'] == 2


class TestSearchEntityType:
    """Test class for _search_entity_type helper method."""
    
    @pytest.mark.asyncio
    async def test_search_client_by_name(self, mock_db, admin_user, sample_client):
        """Test searching clients by name."""
        service = HierarchyService(mock_db)
        
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_client]
        mock_db.execute.return_value = mock_result
        
        # Execute search
        results = await service._search_entity_type(
            entity_type='client',
            query='Acme',
            current_user=admin_user
        )
        
        # Verify results
        assert len(results) == 1
        assert results[0]['entity_type'] == 'client'
        assert results[0]['name'] == 'Acme Corporation'
        assert results[0]['id'] == str(sample_client.id)
    
    @pytest.mark.asyncio
    async def test_search_task_by_title(self, mock_db, admin_user):
        """Test searching tasks by title."""
        service = HierarchyService(mock_db)
        
        # Create sample task
        task = Task(
            id=uuid4(),
            user_story_id=uuid4(),
            title="Implement search feature",
            description="Add search functionality",
            status="In Progress",
            is_deleted=False
        )
        
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [task]
        mock_db.execute.return_value = mock_result
        
        # Mock _apply_client_filter
        with patch.object(service, '_apply_client_filter', new_callable=AsyncMock) as mock_filter:
            mock_filter.return_value = MagicMock()
            
            # Execute search
            results = await service._search_entity_type(
                entity_type='task',
                query='search',
                current_user=admin_user
            )
            
            # Verify results
            assert len(results) == 1
            assert results[0]['entity_type'] == 'task'
            assert results[0]['name'] == 'Implement search feature'


class TestHierarchyPath:
    """Test class for hierarchy path generation."""
    
    @pytest.mark.asyncio
    async def test_generate_hierarchy_path(self, mock_db):
        """Test generating hierarchy path for an entity."""
        service = HierarchyService(mock_db)
        
        # Mock breadcrumb
        mock_breadcrumb = [
            {"type": "client", "id": str(uuid4()), "name": "Acme Corp"},
            {"type": "program", "id": str(uuid4()), "name": "Digital Transform"},
            {"type": "project", "id": str(uuid4()), "name": "E-commerce"}
        ]
        
        with patch.object(service, '_get_breadcrumb_for_entity', new_callable=AsyncMock) as mock_bc:
            mock_bc.return_value = mock_breadcrumb
            
            # Generate path
            path = await service._generate_hierarchy_path('project', str(uuid4()))
            
            # Verify path
            assert path == "Acme Corp > Digital Transform > E-commerce"
    
    @pytest.mark.asyncio
    async def test_generate_hierarchy_path_empty(self, mock_db):
        """Test generating hierarchy path when no breadcrumb exists."""
        service = HierarchyService(mock_db)
        
        with patch.object(service, '_get_breadcrumb_for_entity', new_callable=AsyncMock) as mock_bc:
            mock_bc.return_value = []
            
            # Generate path
            path = await service._generate_hierarchy_path('client', str(uuid4()))
            
            # Verify empty path
            assert path == ""


def test_hierarchy_service_search_initialization():
    """Test that HierarchyService search methods are available."""
    mock_db = MagicMock(spec=AsyncSession)
    service = HierarchyService(mock_db)
    
    # Verify search methods exist
    assert hasattr(service, 'search_entities')
    assert hasattr(service, '_search_entity_type')
    assert hasattr(service, '_generate_hierarchy_path')
    assert hasattr(service, '_apply_client_filter')
