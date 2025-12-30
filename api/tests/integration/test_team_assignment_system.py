"""
Comprehensive integration tests for team assignment system.
Tests complete assignment workflows end-to-end, cross-project isolation enforcement,
role-based access control scenarios, error handling and recovery scenarios,
and system behavior under load.

Requirements: 4.1, 4.2, 5.1, 12.5
"""
import pytest
import asyncio
import time
from typing import List, Dict, Any
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.hierarchy import Project, Task, UserStory, Usecase, Program
from app.models.client import Client
from app.models.team import Team, TeamMember, Assignment, AssignmentHistory
from app.services.team_service import TeamService
from app.services.assignment_service import AssignmentService
from app.services.validation_service import ValidationService
from app.core.exceptions import ValidationError, PermissionError


class TestTeamAssignmentIntegration:
    """Integration tests for complete assignment workflows"""
    
    @pytest.fixture
    async def admin_user(self, db: AsyncSession) -> User:
        """Create admin user for tests"""
        user = User(
            id="USR-ADMIN",
            email="admin@test.com",
            full_name="Admin User",
            primary_role="Admin",
            hashed_password="hashed",
            client_id="CLI-001"
        )
        db.add(user)
        await db.commit()
        return user
    
    @pytest.fixture
    async def developer_user(self, db: AsyncSession) -> User:
        """Create developer user for tests"""
        user = User(
            id="USR-DEV",
            email="dev@test.com",
            full_name="Developer User",
            primary_role="Developer",
            hashed_password="hashed",
            client_id="CLI-001"
        )
        db.add(user)
        await db.commit()
        return user
    
    @pytest.fixture
    async def test_project(self, db: AsyncSession) -> Project:
        """Create test project"""
        project = Project(
            id="PRJ-TEST",
            name="Test Project",
            description="Test project for integration tests",
            client_id="CLI-001"
        )
        db.add(project)
        await db.commit()
        return project
    
    @pytest.fixture
    async def test_task(self, db: AsyncSession, test_project: Project) -> Task:
        """Create test task"""
        task = Task(
            id="TSK-TEST",
            title="Test Task",
            description="Test task for integration tests",
            project_id=test_project.id
        )
        db.add(task)
        await db.commit()
        return task
    
    async def test_complete_assignment_workflow(
        self,
        db: AsyncSession,
        admin_user: User,
        developer_user: User,
        test_project: Project,
        test_task: Task
    ):
        """Test complete assignment workflow end-to-end"""
        
        # 1. Create team
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Test Team",
            description="Test team",
            project_id=test_project.id,
            current_user=admin_user
        )
        
        assert team.name == "Test Team"
        assert team.project_id == test_project.id
        
        # 2. Add member to team
        member = await team_service.add_member(
            team_id=team.id,
            user_id=developer_user.id,
            role="Developer",
            current_user=admin_user
        )
        
        assert member.user_id == developer_user.id
        assert member.role == "Developer"
        
        # 3. Assign task to user
        assignment_service = AssignmentService(db)
        assignment = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=test_task.id,
            user_id=developer_user.id,
            assignment_type="developer",
            current_user=admin_user
        )
        
        assert assignment.entity_type == "task"
        assert assignment.entity_id == test_task.id
        assert assignment.user_id == developer_user.id
        
        # 4. Verify assignment exists
        assignments = await assignment_service.get_entity_assignments(
            entity_type="task",
            entity_id=test_task.id
        )
        
        assert len(assignments) == 1
        assert assignments[0].user_id == developer_user.id
        
        # 5. Remove assignment
        success = await assignment_service.unassign_entity(
            entity_type="task",
            entity_id=test_task.id,
            assignment_type="developer",
            current_user=admin_user
        )
        
        assert success is True
        
        # 6. Verify assignment removed
        assignments = await assignment_service.get_entity_assignments(
            entity_type="task",
            entity_id=test_task.id
        )
        
        assert len(assignments) == 0
    
    async def test_cross_project_isolation(
        self,
        db: AsyncSession,
        admin_user: User,
        developer_user: User
    ):
        """Test that cross-project isolation is enforced"""
        
        # Create two projects
        project1 = Project(
            id="PRJ-001",
            name="Project 1",
            client_id="CLI-001"
        )
        project2 = Project(
            id="PRJ-002", 
            name="Project 2",
            client_id="CLI-001"
        )
        db.add_all([project1, project2])
        await db.commit()
        
        # Create teams for each project
        team_service = TeamService(db)
        team1 = await team_service.create_team(
            name="Team 1",
            description="Team for project 1",
            project_id=project1.id,
            current_user=admin_user
        )
        
        team2 = await team_service.create_team(
            name="Team 2", 
            description="Team for project 2",
            project_id=project2.id,
            current_user=admin_user
        )
        
        # Add user to team 1 only
        await team_service.add_member(
            team_id=team1.id,
            user_id=developer_user.id,
            role="Developer",
            current_user=admin_user
        )
        
        # Create tasks in both projects
        task1 = Task(
            id="TSK-001",
            title="Task 1",
            project_id=project1.id
        )
        task2 = Task(
            id="TSK-002",
            title="Task 2", 
            project_id=project2.id
        )
        db.add_all([task1, task2])
        await db.commit()
        
        assignment_service = AssignmentService(db)
        
        # Should succeed - user is in project 1 team
        assignment1 = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=task1.id,
            user_id=developer_user.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert assignment1 is not None
        
        # Should fail - user is not in project 2 team
        with pytest.raises((ValidationError, PermissionError, Exception)):
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task2.id,
                user_id=developer_user.id,
                assignment_type="developer",
                current_user=admin_user
            )
    
    async def test_role_based_assignment_validation(
        self,
        db: AsyncSession,
        admin_user: User,
        test_project: Project
    ):
        """Test role-based assignment validation"""
        
        # Create users with different roles
        owner_user = User(
            id="USR-OWNER",
            email="owner@test.com",
            full_name="Owner User",
            primary_role="Owner",
            hashed_password="hashed",
            client_id="CLI-001"
        )
        
        developer_user = User(
            id="USR-DEV2",
            email="dev2@test.com", 
            full_name="Developer User 2",
            primary_role="Developer",
            hashed_password="hashed",
            client_id="CLI-001"
        )
        
        db.add_all([owner_user, developer_user])
        await db.commit()
        
        # Create team and add members
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Mixed Team",
            description="Team with mixed roles",
            project_id=test_project.id,
            current_user=admin_user
        )
        
        await team_service.add_member(
            team_id=team.id,
            user_id=owner_user.id,
            role="Owner",
            current_user=admin_user
        )
        
        await team_service.add_member(
            team_id=team.id,
            user_id=developer_user.id,
            role="Developer", 
            current_user=admin_user
        )
        
        # Create different types of entities
        from app.models.hierarchy import UserStory
        
        user_story = UserStory(
            id="UST-001",
            title="Test User Story",
            project_id=test_project.id
        )
        
        task = Task(
            id="TSK-ROLE",
            title="Role Test Task",
            project_id=test_project.id
        )
        
        db.add_all([user_story, task])
        await db.commit()
        
        assignment_service = AssignmentService(db)
        
        # Owner should be able to be assigned to user story
        assignment1 = await assignment_service.assign_entity(
            entity_type="userstory",
            entity_id=user_story.id,
            user_id=owner_user.id,
            assignment_type="owner",
            current_user=admin_user
        )
        assert assignment1 is not None
        
        # Developer should be able to be assigned to task
        assignment2 = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=task.id,
            user_id=developer_user.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert assignment2 is not None
        
        # Developer should NOT be able to be assigned as owner to user story
        with pytest.raises((ValidationError, PermissionError, Exception)):
            await assignment_service.assign_entity(
                entity_type="userstory",
                entity_id=user_story.id,
                user_id=developer_user.id,
                assignment_type="owner",
                current_user=admin_user
            )


class TestTeamAssignmentAPI:
    """API integration tests"""
    
    async def test_team_api_workflow(self, client: AsyncClient, admin_token: str):
        """Test team management API workflow"""
        
        # Create team
        team_data = {
            "name": "API Test Team",
            "description": "Team created via API",
            "project_id": "PRJ-001"
        }
        
        response = await client.post(
            "/api/v1/teams/",
            json=team_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        team = response.json()
        team_id = team["id"]
        
        # Add member
        member_data = {
            "user_id": "USR-001",
            "role": "Developer"
        }
        
        response = await client.post(
            f"/api/v1/teams/{team_id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        
        # Get team members
        response = await client.get(
            f"/api/v1/teams/{team_id}/members",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 1
        assert members[0]["user_id"] == "USR-001"
    
    async def test_assignment_api_workflow(self, client: AsyncClient, admin_token: str):
        """Test assignment API workflow"""
        
        # Create assignment
        assignment_data = {
            "entity_type": "task",
            "entity_id": "TSK-001",
            "user_id": "USR-001",
            "assignment_type": "developer"
        }
        
        response = await client.post(
            "/api/v1/assignments/",
            json=assignment_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201
        assignment = response.json()
        
        # Get assignments
        response = await client.get(
            "/api/v1/assignments/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assignments = response.json()
        assert len(assignments) > 0
        
        # Remove assignment
        response = await client.delete(
            f"/api/v1/assignments/{assignment['id']}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


class TestComprehensiveWorkflows:
    """Test complete assignment workflows end-to-end"""
    
    @pytest.fixture
    async def complete_hierarchy_setup(self, db: AsyncSession) -> Dict[str, Any]:
        """Setup complete hierarchy for comprehensive testing"""
        
        # Create client
        client = Client(
            id="CLI-COMP",
            name="Comprehensive Test Client",
            description="Client for comprehensive testing"
        )
        db.add(client)
        
        # Create program
        program = Program(
            id="PRG-COMP",
            name="Comprehensive Program",
            description="Program for comprehensive testing",
     
            client_id=client.id
        )
        db.add(program)
        
        # Create project
        project = Project(
            id="PRJ-COMP",
            name="Comprehensive Project",
            description="Project for comprehensive testing",
            client_id=client.id,
            program_id=program.id
        )
        db.add(project)
        
        # Create use case
        use_case = Usecase(
            id="UC-COMP",
            name="Comprehensive Use Case",
            description="Use case for comprehensive testing",
            project_id=project.id
        )
        db.add(use_case)
        
        # Create user story
        user_story = UserStory(
            id="US-COMP",
            title="Comprehensive User Story",
            description="User story for comprehensive testing",
            project_id=project.id,
            use_case_id=use_case.id
        )
        db.add(user_story)
        
        # Create task
        task = Task(
            id="TSK-COMP",
            title="Comprehensive Task",
            description="Task for comprehensive testing",
            project_id=project.id,
            user_story_id=user_story.id
        )
        db.add(task)
        
        # Create users with different roles
        admin_user = User(
            id="USR-ADMIN-COMP",
            email="admin.comp@test.com",
            full_name="Admin User",
            primary_role="Admin",
            hashed_password="hashed",
            client_id=client.id
        )
        
        owner_user = User(
            id="USR-OWNER-COMP",
            email="owner.comp@test.com",
            full_name="Owner User",
            primary_role="Owner",
            hashed_password="hashed",
            client_id=client.id
        )
        
        developer_user = User(
            id="USR-DEV-COMP",
            email="dev.comp@test.com",
            full_name="Developer User",
            primary_role="Developer",
            hashed_password="hashed",
            client_id=client.id
        )
        
        contact_user = User(
            id="USR-CONTACT-COMP",
            email="contact.comp@test.com",
            full_name="Contact User",
            primary_role="Contact Person",
            is_contact_person=True,
            hashed_password="hashed",
            client_id=client.id
        )
        
        db.add_all([admin_user, owner_user, developer_user, contact_user])
        await db.commit()
        
        return {
            "client": client,
            "program": program,
            "project": project,
            "use_case": use_case,
            "user_story": user_story,
            "task": task,
            "admin_user": admin_user,
            "owner_user": owner_user,
            "developer_user": developer_user,
            "contact_user": contact_user
        }
    
    async def test_complete_hierarchy_assignment_workflow(
        self,
        db: AsyncSession,
        complete_hierarchy_setup: Dict[str, Any]
    ):
        """Test complete assignment workflow across entire hierarchy"""
        
        setup = complete_hierarchy_setup
        admin_user = setup["admin_user"]
        owner_user = setup["owner_user"]
        developer_user = setup["developer_user"]
        contact_user = setup["contact_user"]
        
        # Create team and add members
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Comprehensive Team",
            description="Team for comprehensive testing",
            project_id=setup["project"].id,
            current_user=admin_user
        )
        
        # Add all users to team with appropriate roles
        await team_service.add_member(
            team_id=team.id,
            user_id=owner_user.id,
            role="Owner",
            current_user=admin_user
        )
        
        await team_service.add_member(
            team_id=team.id,
            user_id=developer_user.id,
            role="Developer",
            current_user=admin_user
        )
        
        assignment_service = AssignmentService(db)
        
        # Test assignments at each hierarchy level
        
        # 1. Assign client to contact person (no team membership required)
        client_assignment = await assignment_service.assign_entity(
            entity_type="client",
            entity_id=setup["client"].id,
            user_id=contact_user.id,
            assignment_type="contact_person",
            current_user=admin_user
        )
        assert client_assignment.entity_type == "client"
        assert client_assignment.assigned_to == contact_user.id
        
        # 2. Assign program to owner (no team membership required)
        program_assignment = await assignment_service.assign_entity(
            entity_type="program",
            entity_id=setup["program"].id,
            user_id=owner_user.id,
            assignment_type="owner",
            current_user=admin_user
        )
        assert program_assignment.entity_type == "program"
        assert program_assignment.assigned_to == owner_user.id
        
        # 3. Assign project to owner (no team membership required)
        project_assignment = await assignment_service.assign_entity(
            entity_type="project",
            entity_id=setup["project"].id,
            user_id=owner_user.id,
            assignment_type="owner",
            current_user=admin_user
        )
        assert project_assignment.entity_type == "project"
        assert project_assignment.assigned_to == owner_user.id
        
        # 4. Assign use case to owner (requires team membership)
        usecase_assignment = await assignment_service.assign_entity(
            entity_type="usecase",
            entity_id=setup["use_case"].id,
            user_id=owner_user.id,
            assignment_type="owner",
            current_user=admin_user
        )
        assert usecase_assignment.entity_type == "usecase"
        assert usecase_assignment.assigned_to == owner_user.id
        
        # 5. Assign user story to owner (requires team membership)
        userstory_assignment = await assignment_service.assign_entity(
            entity_type="userstory",
            entity_id=setup["user_story"].id,
            user_id=owner_user.id,
            assignment_type="owner",
            current_user=admin_user
        )
        assert userstory_assignment.entity_type == "userstory"
        assert userstory_assignment.assigned_to == owner_user.id
        
        # 6. Assign task to developer (requires team membership)
        task_assignment = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=setup["task"].id,
            user_id=developer_user.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert task_assignment.entity_type == "task"
        assert task_assignment.assigned_to == developer_user.id
        
        # Verify all assignments exist
        all_assignments = await db.execute(
            select(Assignment).where(Assignment.is_active == True)
        )
        assignments = all_assignments.scalars().all()
        assert len(assignments) == 6
        
        # Test assignment history tracking
        history_records = await db.execute(
            select(AssignmentHistory)
        )
        history = history_records.scalars().all()
        assert len(history) == 6  # One for each assignment


class TestCrossProjectIsolation:
    """Test cross-project isolation enforcement"""
    
    async def test_strict_project_isolation(self, db: AsyncSession):
        """Test that project isolation is strictly enforced"""
        
        # Create two separate clients and projects
        client1 = Client(id="CLI-ISO1", name="Client 1")
        client2 = Client(id="CLI-ISO2", name="Client 2")
        
        project1 = Project(
            id="PRJ-ISO1",
            name="Project 1",
            client_id=client1.id
        )
        project2 = Project(
            id="PRJ-ISO2",
            name="Project 2",
            client_id=client2.id
        )
        
        # Create users for each client
        user1 = User(
            id="USR-ISO1",
            email="user1@client1.com",
            full_name="User 1",
            primary_role="Developer",
            hashed_password="hashed",
            client_id=client1.id
        )
        
        user2 = User(
            id="USR-ISO2",
            email="user2@client2.com",
            full_name="User 2",
            primary_role="Developer",
            hashed_password="hashed",
            client_id=client2.id
        )
        
        admin1 = User(
            id="USR-ADMIN-ISO1",
            email="admin1@client1.com",
            full_name="Admin 1",
            primary_role="Admin",
            hashed_password="hashed",
            client_id=client1.id
        )
        
        db.add_all([client1, client2, project1, project2, user1, user2, admin1])
        await db.commit()
        
        # Create teams for each project
        team_service = TeamService(db)
        
        team1 = await team_service.create_team(
            name="Team 1",
            description="Team for project 1",
            project_id=project1.id,
            current_user=admin1
        )
        
        # Add user1 to team1
        await team_service.add_member(
            team_id=team1.id,
            user_id=user1.id,
            role="Developer",
            current_user=admin1
        )
        
        # Create tasks in both projects
        task1 = Task(
            id="TSK-ISO1",
            title="Task 1",
            project_id=project1.id
        )
        task2 = Task(
            id="TSK-ISO2",
            title="Task 2",
            project_id=project2.id
        )
        
        db.add_all([task1, task2])
        await db.commit()
        
        assignment_service = AssignmentService(db)
        
        # Test 1: User1 can be assigned to task1 (same project)
        assignment1 = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=task1.id,
            user_id=user1.id,
            assignment_type="developer",
            current_user=admin1
        )
        assert assignment1 is not None
        
        # Test 2: User1 cannot be assigned to task2 (different project)
        with pytest.raises((ValidationError, PermissionError, Exception)):
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task2.id,
                user_id=user1.id,
                assignment_type="developer",
                current_user=admin1
            )


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios"""
    
    async def test_assignment_conflict_resolution(self, db: AsyncSession):
        """Test handling of assignment conflicts"""
        
        # Setup basic entities
        client = Client(id="CLI-ERR", name="Error Test Client")
        project = Project(id="PRJ-ERR", name="Error Test Project", client_id=client.id)
        
        admin_user = User(
            id="USR-ADMIN-ERR",
            email="admin@error.com",
            full_name="Admin User",
            primary_role="Admin",
            hashed_password="hashed",
            client_id=client.id
        )
        
        dev1 = User(
            id="USR-DEV1-ERR",
            email="dev1@error.com",
            full_name="Developer 1",
            primary_role="Developer",
            hashed_password="hashed",
            client_id=client.id
        )
        
        dev2 = User(
            id="USR-DEV2-ERR",
            email="dev2@error.com",
            full_name="Developer 2",
            primary_role="Developer",
            hashed_password="hashed",
            client_id=client.id
        )
        
        task = Task(
            id="TSK-ERR",
            title="Error Test Task",
            project_id=project.id
        )
        
        db.add_all([client, project, admin_user, dev1, dev2, task])
        await db.commit()
        
        # Create team and add members
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Error Test Team",
            description="Team for error testing",
            project_id=project.id,
            current_user=admin_user
        )
        
        await team_service.add_member(team_id=team.id, user_id=dev1.id, role="Developer", current_user=admin_user)
        await team_service.add_member(team_id=team.id, user_id=dev2.id, role="Developer", current_user=admin_user)
        
        assignment_service = AssignmentService(db)
        
        # Test 1: Assign task to dev1
        assignment1 = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=task.id,
            user_id=dev1.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert assignment1 is not None
        
        # Test 2: Try to assign same task to dev2 (should fail - conflict)
        with pytest.raises((ValidationError, Exception)):
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=dev2.id,
                assignment_type="developer",
                current_user=admin_user
            )
        
        # Test 3: Reassign task (unassign first, then assign)
        success = await assignment_service.unassign_entity(
            entity_type="task",
            entity_id=task.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert success
        
        assignment2 = await assignment_service.assign_entity(
            entity_type="task",
            entity_id=task.id,
            user_id=dev2.id,
            assignment_type="developer",
            current_user=admin_user
        )
        assert assignment2.assigned_to == dev2.id


class TestSystemBehaviorUnderLoad:
    """Test system behavior under load"""
    
    async def test_concurrent_assignment_operations(self, db: AsyncSession):
        """Test concurrent assignment operations"""
        
        # Setup
        client = Client(id="CLI-LOAD", name="Load Test Client")
        project = Project(id="PRJ-LOAD", name="Load Test Project", client_id=client.id)
        
        admin_user = User(
            id="USR-ADMIN-LOAD",
            email="admin@load.com",
            full_name="Admin User",
            primary_role="Admin",
            hashed_password="hashed",
            client_id=client.id
        )
        
        # Create multiple users and tasks
        users = []
        tasks = []
        for i in range(10):
            user = User(
                id=f"USR-LOAD-{i:02d}",
                email=f"user{i}@load.com",
                full_name=f"User {i}",
                primary_role="Developer",
                hashed_password="hashed",
                client_id=client.id
            )
            users.append(user)
            
            task = Task(
                id=f"TSK-LOAD-{i:02d}",
                title=f"Load Task {i}",
                project_id=project.id
            )
            tasks.append(task)
        
        db.add_all([client, project, admin_user] + users + tasks)
        await db.commit()
        
        # Create team and add users
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Load Test Team",
            description="Team for load testing",
            project_id=project.id,
            current_user=admin_user
        )
        
        for user in users:
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin_user
            )
        
        # Test concurrent assignments
        assignment_service = AssignmentService(db)
        
        async def assign_task(task: Task, user: User):
            """Assign a task to a user"""
            return await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=user.id,
                assignment_type="developer",
                current_user=admin_user
            )
        
        start_time = time.time()
        
        # Create concurrent assignment tasks
        assignment_tasks = [
            assign_task(task, user)
            for task, user in zip(tasks, users)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*assignment_tasks, return_exceptions=True)
        
        concurrent_time = time.time() - start_time
        
        # Check results
        successful_assignments = [r for r in results if not isinstance(r, Exception)]
        failed_assignments = [r for r in results if isinstance(r, Exception)]
        
        print(f"Concurrent assignments: {concurrent_time:.3f}s")
        print(f"Successful: {len(successful_assignments)}")
        print(f"Failed: {len(failed_assignments)}")
        
        # Should complete quickly and mostly succeed
        assert concurrent_time < 5.0
        assert len(successful_assignments) >= 8  # Allow some failures due to concurrency
    
    async def test_bulk_assignment_performance(self, db: AsyncSession):
        """Test performance of bulk assignment operations"""
        
        # Setup large dataset
        client = Client(id="CLI-BULK", name="Bulk Test Client")
        project = Project(id="PRJ-BULK", name="Bulk Test Project", client_id=client.id)
        
        admin_user = User(
            id="USR-ADMIN-BULK",
            email="admin@bulk.com",
            full_name="Admin User",
            primary_role="Admin",
            hashed_password="hashed",
            client_id=client.id
        )
        
        # Create 25 users and 25 tasks for reasonable test time
        users = []
        tasks = []
        
        for i in range(25):
            user = User(
                id=f"USR-BULK-{i:02d}",
                email=f"user{i}@bulk.com",
                full_name=f"User {i}",
                primary_role="Developer",
                hashed_password="hashed",
                client_id=client.id
            )
            users.append(user)
            
            task = Task(
                id=f"TSK-BULK-{i:02d}",
                title=f"Bulk Task {i}",
                project_id=project.id
            )
            tasks.append(task)
        
        db.add_all([client, project, admin_user] + users + tasks)
        await db.commit()
        
        # Create team and add all users
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Bulk Test Team",
            description="Team for bulk testing",
            project_id=project.id,
            current_user=admin_user
        )
        
        # Add all users to team
        for user in users:
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin_user
            )
        
        # Test bulk assignments
        assignment_service = AssignmentService(db)
        
        start_time = time.time()
        
        # Assign each task to a user
        for i, task in enumerate(tasks):
            user = users[i % len(users)]  # Cycle through users
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=user.id,
                assignment_type="developer",
                current_user=admin_user
            )
        
        assignment_time = time.time() - start_time
        
        print(f"25 bulk assignments: {assignment_time:.3f}s")
        print(f"Average per assignment: {assignment_time/25:.3f}s")
        
        # Should complete in reasonable time
        assert assignment_time < 10.0  # 10 seconds for 25 assignments
        
        # Verify all assignments were created
        all_assignments = await db.execute(
            select(Assignment).where(Assignment.is_active == True)
        )
        assignments = all_assignments.scalars().all()
        assert len(assignments) == 25


class TestSystemValidation:
    """Test comprehensive system validation"""
    
    async def test_end_to_end_system_validation(self, db: AsyncSession):
        """Test complete system validation end-to-end"""
        
        # This test validates the entire system works together
        # Create a realistic scenario with multiple clients, projects, teams, and assignments
        
        # Setup multiple clients
        client1 = Client(id="CLI-VAL1", name="Validation Client 1")
        client2 = Client(id="CLI-VAL2", name="Validation Client 2")
        
        # Setup projects
        project1 = Project(id="PRJ-VAL1", name="Validation Project 1", client_id=client1.id)
        project2 = Project(id="PRJ-VAL2", name="Validation Project 2", client_id=client2.id)
        
        # Setup users with different roles
        admin1 = User(
            id="USR-ADMIN-VAL1", email="admin1@val.com", full_name="Admin 1",
            primary_role="Admin", hashed_password="hashed", client_id=client1.id
        )
        admin2 = User(
            id="USR-ADMIN-VAL2", email="admin2@val.com", full_name="Admin 2",
            primary_role="Admin", hashed_password="hashed", client_id=client2.id
        )
        
        owner1 = User(
            id="USR-OWNER-VAL1", email="owner1@val.com", full_name="Owner 1",
            primary_role="Owner", hashed_password="hashed", client_id=client1.id
        )
        
        dev1 = User(
            id="USR-DEV-VAL1", email="dev1@val.com", full_name="Developer 1",
            primary_role="Developer", hashed_password="hashed", client_id=client1.id
        )
        dev2 = User(
            id="USR-DEV-VAL2", email="dev2@val.com", full_name="Developer 2",
            primary_role="Developer", hashed_password="hashed", client_id=client2.id
        )
        
        # Setup hierarchy entities
        use_case1 = Usecase(id="UC-VAL1", name="Validation Use Case 1", project_id=project1.id)
        user_story1 = UserStory(id="US-VAL1", title="Validation User Story 1", project_id=project1.id, use_case_id=use_case1.id)
        task1 = Task(id="TSK-VAL1", title="Validation Task 1", project_id=project1.id, user_story_id=user_story1.id)
        task2 = Task(id="TSK-VAL2", title="Validation Task 2", project_id=project2.id)
        
        db.add_all([
            client1, client2, project1, project2,
            admin1, admin2, owner1, dev1, dev2,
            use_case1, user_story1, task1, task2
        ])
        await db.commit()
        
        # Test complete workflow
        team_service = TeamService(db)
        assignment_service = AssignmentService(db)
        validation_service = ValidationService(db)
        
        # 1. Create teams
        team1 = await team_service.create_team(
            name="Validation Team 1", description="Team 1", project_id=project1.id, current_user=admin1
        )
        team2 = await team_service.create_team(
            name="Validation Team 2", description="Team 2", project_id=project2.id, current_user=admin2
        )
        
        # 2. Add members to teams
        await team_service.add_member(team_id=team1.id, user_id=owner1.id, role="Owner", current_user=admin1)
        await team_service.add_member(team_id=team1.id, user_id=dev1.id, role="Developer", current_user=admin1)
        await team_service.add_member(team_id=team2.id, user_id=dev2.id, role="Developer", current_user=admin2)
        
        # 3. Test valid assignments
        # Project assignment (no team membership required)
        project_assignment = await assignment_service.assign_entity(
            entity_type="project", entity_id=project1.id, user_id=owner1.id,
            assignment_type="owner", current_user=admin1
        )
        assert project_assignment is not None
        
        # Use case assignment (requires team membership)
        usecase_assignment = await assignment_service.assign_entity(
            entity_type="usecase", entity_id=use_case1.id, user_id=owner1.id,
            assignment_type="owner", current_user=admin1
        )
        assert usecase_assignment is not None
        
        # Task assignment (requires team membership)
        task_assignment = await assignment_service.assign_entity(
            entity_type="task", entity_id=task1.id, user_id=dev1.id,
            assignment_type="developer", current_user=admin1
        )
        assert task_assignment is not None
        
        # 4. Test cross-project isolation
        with pytest.raises((ValidationError, PermissionError, Exception)):
            await assignment_service.assign_entity(
                entity_type="task", entity_id=task2.id, user_id=dev1.id,
                assignment_type="developer", current_user=admin1
            )
        
        # 5. Test role validation
        with pytest.raises((ValidationError, PermissionError, Exception)):
            await assignment_service.assign_entity(
                entity_type="usecase", entity_id=use_case1.id, user_id=dev1.id,
                assignment_type="owner", current_user=admin1
            )
        
        # 6. Verify all assignments are tracked
        all_assignments = await db.execute(select(Assignment).where(Assignment.is_active == True))
        assignments = all_assignments.scalars().all()
        assert len(assignments) == 3  # project, usecase, task
        
        # 7. Test assignment history
        history = await db.execute(select(AssignmentHistory))
        history_records = history.scalars().all()
        assert len(history_records) == 3  # One for each assignment
        
        print("End-to-end system validation completed successfully")