"""
Integration tests for the TODO feature.
Tests complete user flows and feature integration.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.todo import TodoItem, AdhocNote
from app.models.hierarchy import Task, Subtask, UserStory, Project, Program, Usecase
from app.models.client import Client
from app.models.user import User


@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    user = User(
        id="USR-TEST-001",
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_2(db: Session):
    """Create a second test user."""
    user = User(
        id="USR-TEST-002",
        username="testuser2",
        email="test2@example.com",
        full_name="Test User 2"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_task(db: Session, test_user):
    """Create a test task for linking."""
    # Create hierarchy: Client -> Program -> Project -> Usecase -> UserStory -> Task
    client = Client(id="CLI-001", name="Test Client")
    db.add(client)
    
    program = Program(id="PRG-001", name="Test Program", client_id="CLI-001")
    db.add(program)
    
    project = Project(id="PRJ-001", name="Test Project", program_id="PRG-001")
    db.add(project)
    
    usecase = Usecase(
        id="USC-001",
        name="Test Usecase",
        project_id="PRJ-001",
        status="Active"
    )
    db.add(usecase)
    
    user_story = UserStory(
        id="UST-001",
        title="Test User Story",
        usecase_id="USC-001",
        status="In Progress"
    )
    db.add(user_story)
    
    task = Task(
        id="TSK-001",
        title="Test Task for Linking",
        user_story_id="UST-001",
        status="In Progress",
        assigned_to=test_user.id
    )
    db.add(task)
    
    db.commit()
    db.refresh(task)
    return task


@pytest.fixture
def test_subtask(db: Session, test_task, test_user):
    """Create a test subtask for linking."""
    subtask = Subtask(
        id="SUB-001",
        title="Test Subtask for Linking",
        task_id=test_task.id,
        status="To Do",
        assigned_to=test_user.id
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)
    return subtask


class TestTodoFeatureIntegration:
    """Integration tests for complete TODO feature workflows."""
    
    def test_complete_todo_item_lifecycle(self, client: TestClient, db: Session, test_user):
        """Test creating, updating, moving, and deleting a TODO item."""
        # 1. Create a TODO item
        create_data = {
            "title": "Review code changes",
            "description": "Check PR #123",
            "target_date": str(date.today()),
            "visibility": "private"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=create_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        todo_data = response.json()
        todo_id = todo_data["id"]
        assert todo_data["title"] == create_data["title"]
        assert todo_data["visibility"] == "private"
        
        # 2. Update the TODO item
        update_data = {
            "title": "Review code changes - UPDATED",
            "description": "Check PR #123 and #124"
        }
        
        response = client.put(
            f"/api/v1/todos/{todo_id}",
            json=update_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        updated_data = response.json()
        assert updated_data["title"] == update_data["title"]
        assert updated_data["description"] == update_data["description"]
        
        # 3. Move to different date (tomorrow)
        tomorrow = date.today() + timedelta(days=1)
        move_data = {"target_date": str(tomorrow)}
        
        response = client.patch(
            f"/api/v1/todos/{todo_id}/move",
            json=move_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        moved_data = response.json()
        assert moved_data["target_date"] == str(tomorrow)
        
        # 4. Delete the TODO item
        response = client.delete(
            f"/api/v1/todos/{todo_id}",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 204
        
        # 5. Verify it's soft deleted
        response = client.get(
            f"/api/v1/todos/{todo_id}",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 404
    
    def test_task_linking_workflow(self, client: TestClient, db: Session, test_user, test_task):
        """Test linking TODO item to task and fetching task info."""
        # 1. Create TODO item
        create_data = {
            "title": "Work on authentication",
            "target_date": str(date.today()),
            "visibility": "private"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=create_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        todo_id = response.json()["id"]
        
        # 2. Link to task
        link_data = {
            "entity_type": "task",
            "entity_id": test_task.id
        }
        
        response = client.post(
            f"/api/v1/todos/{todo_id}/link",
            json=link_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        linked_data = response.json()
        assert linked_data["linked_entity_type"] == "task"
        assert linked_data["linked_entity_id"] == test_task.id
        assert "linked_entity_info" in linked_data
        assert linked_data["linked_entity_info"]["title"] == test_task.title
        
        # 3. Fetch task summary directly
        response = client.get(
            f"/api/v1/tasks/{test_task.id}/summary",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        task_summary = response.json()
        assert task_summary["id"] == test_task.id
        assert task_summary["title"] == test_task.title
        assert task_summary["status"] == test_task.status
        
        # 4. Unlink from task
        response = client.delete(
            f"/api/v1/todos/{todo_id}/link",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        unlinked_data = response.json()
        assert unlinked_data["linked_entity_type"] is None
        assert unlinked_data["linked_entity_id"] is None
    
    def test_subtask_linking_workflow(self, client: TestClient, db: Session, test_user, test_subtask):
        """Test linking TODO item to subtask."""
        # 1. Create TODO item
        create_data = {
            "title": "Write unit tests",
            "target_date": str(date.today()),
            "visibility": "private"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=create_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        todo_id = response.json()["id"]
        
        # 2. Link to subtask
        link_data = {
            "entity_type": "subtask",
            "entity_id": test_subtask.id
        }
        
        response = client.post(
            f"/api/v1/todos/{todo_id}/link",
            json=link_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        linked_data = response.json()
        assert linked_data["linked_entity_type"] == "subtask"
        assert linked_data["linked_entity_id"] == test_subtask.id
        
        # 3. Fetch subtask summary
        response = client.get(
            f"/api/v1/subtasks/{test_subtask.id}/summary",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        subtask_summary = response.json()
        assert subtask_summary["id"] == test_subtask.id
        assert subtask_summary["title"] == test_subtask.title
    
    def test_public_private_visibility(self, client: TestClient, db: Session, test_user, test_user_2):
        """Test public and private visibility controls."""
        # 1. User 1 creates private TODO
        private_data = {
            "title": "Private TODO",
            "target_date": str(date.today()),
            "visibility": "private"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=private_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        private_id = response.json()["id"]
        
        # 2. User 1 creates public TODO
        public_data = {
            "title": "Public TODO",
            "target_date": str(date.today()),
            "visibility": "public"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=public_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        public_id = response.json()["id"]
        
        # 3. User 1 can see both
        response = client.get(
            "/api/v1/todos",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        user1_todos = response.json()["items"]
        assert len(user1_todos) == 2
        
        # 4. User 2 can only see their own items (none yet)
        response = client.get(
            "/api/v1/todos",
            headers={"X-User-ID": test_user_2.id}
        )
        assert response.status_code == 200
        user2_todos = response.json()["items"]
        assert len(user2_todos) == 0
        
        # 5. User 2 can see public items when requested
        response = client.get(
            "/api/v1/todos?include_public=true",
            headers={"X-User-ID": test_user_2.id}
        )
        assert response.status_code == 200
        user2_public_todos = response.json()["items"]
        assert len(user2_public_todos) == 1
        assert user2_public_todos[0]["id"] == public_id
        assert user2_public_todos[0]["visibility"] == "public"
        
        # 6. User 2 cannot access User 1's private TODO
        response = client.get(
            f"/api/v1/todos/{private_id}",
            headers={"X-User-ID": test_user_2.id}
        )
        assert response.status_code == 404
    
    def test_adhoc_notes_workflow(self, client: TestClient, db: Session, test_user):
        """Test ADHOC notes creation, reordering, and deletion."""
        # 1. Create multiple ADHOC notes
        note_ids = []
        for i in range(3):
            note_data = {
                "title": f"Note {i+1}",
                "content": f"Content for note {i+1}",
                "color": "#FFEB3B"
            }
            
            response = client.post(
                "/api/v1/adhoc-notes",
                json=note_data,
                headers={"X-User-ID": test_user.id}
            )
            assert response.status_code == 201
            note_ids.append(response.json()["id"])
        
        # 2. Fetch all notes
        response = client.get(
            "/api/v1/adhoc-notes",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        notes = response.json()["notes"]
        assert len(notes) == 3
        
        # 3. Reorder a note
        reorder_data = {"position": 0}
        response = client.patch(
            f"/api/v1/adhoc-notes/{note_ids[2]}/reorder",
            json=reorder_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        
        # 4. Update a note
        update_data = {
            "title": "Updated Note",
            "content": "Updated content",
            "color": "#FF5722"
        }
        response = client.put(
            f"/api/v1/adhoc-notes/{note_ids[0]}",
            json=update_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        updated_note = response.json()
        assert updated_note["title"] == update_data["title"]
        assert updated_note["color"] == update_data["color"]
        
        # 5. Delete a note
        response = client.delete(
            f"/api/v1/adhoc-notes/{note_ids[1]}",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 204
        
        # 6. Verify only 2 notes remain
        response = client.get(
            "/api/v1/adhoc-notes",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        remaining_notes = response.json()["notes"]
        assert len(remaining_notes) == 2
    
    def test_date_range_filtering(self, client: TestClient, db: Session, test_user):
        """Test filtering TODO items by date range."""
        yesterday = date.today() - timedelta(days=1)
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)
        
        # Create TODO items for different dates
        dates = [yesterday, today, tomorrow, day_after]
        for i, target_date in enumerate(dates):
            todo_data = {
                "title": f"TODO for {target_date}",
                "target_date": str(target_date),
                "visibility": "private"
            }
            
            response = client.post(
                "/api/v1/todos",
                json=todo_data,
                headers={"X-User-ID": test_user.id}
            )
            assert response.status_code == 201
        
        # Fetch all
        response = client.get(
            "/api/v1/todos",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        all_todos = response.json()["items"]
        assert len(all_todos) == 4
        
        # Fetch only today and tomorrow
        response = client.get(
            f"/api/v1/todos?start_date={today}&end_date={tomorrow}",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        filtered_todos = response.json()["items"]
        assert len(filtered_todos) == 2
        
        # Verify dates are correct
        todo_dates = [item["target_date"] for item in filtered_todos]
        assert str(today) in todo_dates
        assert str(tomorrow) in todo_dates
    
    def test_task_hierarchy_read_only(self, client: TestClient, db: Session, test_user, test_task):
        """Verify that task hierarchy cannot be modified from TODO context."""
        # Get task summary (should work - read-only)
        response = client.get(
            f"/api/v1/tasks/{test_task.id}/summary",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        
        # Attempt to modify task (should fail or not be available)
        # The summary endpoint should only support GET
        update_data = {"title": "Modified Title"}
        response = client.put(
            f"/api/v1/tasks/{test_task.id}/summary",
            json=update_data,
            headers={"X-User-ID": test_user.id}
        )
        # Should return 405 Method Not Allowed or 404 Not Found
        assert response.status_code in [404, 405]
        
        # Verify task was not modified
        db.refresh(test_task)
        assert test_task.title == "Test Task for Linking"
    
    def test_authorization_checks(self, client: TestClient, db: Session, test_user, test_user_2):
        """Test that users can only modify their own TODO items."""
        # User 1 creates a TODO
        todo_data = {
            "title": "User 1 TODO",
            "target_date": str(date.today()),
            "visibility": "private"
        }
        
        response = client.post(
            "/api/v1/todos",
            json=todo_data,
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 201
        todo_id = response.json()["id"]
        
        # User 2 tries to update User 1's TODO
        update_data = {"title": "Hacked!"}
        response = client.put(
            f"/api/v1/todos/{todo_id}",
            json=update_data,
            headers={"X-User-ID": test_user_2.id}
        )
        assert response.status_code == 404  # Should not find it
        
        # User 2 tries to delete User 1's TODO
        response = client.delete(
            f"/api/v1/todos/{todo_id}",
            headers={"X-User-ID": test_user_2.id}
        )
        assert response.status_code == 404
        
        # Verify TODO is unchanged
        response = client.get(
            f"/api/v1/todos/{todo_id}",
            headers={"X-User-ID": test_user.id}
        )
        assert response.status_code == 200
        assert response.json()["title"] == todo_data["title"]
