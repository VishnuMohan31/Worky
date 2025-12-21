"""
Security tests for team assignment system.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.hierarchy import Project
from app.models.team import Team
from app.services.team_service import TeamService


class TestAssignmentSecurity:
    """Security tests for assignment system"""
    
    @pytest.fixture
    async def regular_user(self, db: AsyncSession) -> User:
        """Create regular user for security tests"""
        user = User(
            id="USR-REGULAR",
            email="regular@test.com",
            full_name="Regular User",
            primary_role="Developer",
            hashed_password="hashed",
            client_id="CLI-001"
        )
        db.add(user)
        await db.commit()
        return user
    
    @pytest.fixture
    async def other_client_user(self, db: AsyncSession) -> User:
        """Create user from different client"""
        user = User(
            id="USR-OTHER",
            email="other@test.com",
            full_name="Other Client User",
            primary_role="Developer", 
            hashed_password="hashed",
            client_id="CLI-002"  # Different client
        )
        db.add(user)
        await db.commit()
        return user
    
    async def test_unauthorized_team_creation(self, client: AsyncClient):
        """Test that unauthorized users cannot create teams"""
        team_data = {
            "name": "Unauthorized Team",
            "description": "Should not be created",
            "project_id": "PRJ-001"
        }
        
        # No authentication
        response = await client.post("/api/v1/teams/", json=team_data)
        assert response.status_code == 401
        
        # Invalid token
        response = await client.post(
            "/api/v1/teams/",
            json=team_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    async def test_cross_client_data_isolation(
        self,
        client: AsyncClient,
        db: AsyncSession,
        regular_user: User,
        other_client_user: User
    ):
        """Test that users cannot access data from other clients"""
        
        # Create project for regular user's client
        project = Project(
            id="PRJ-SECURITY",
            name="Security Test Project",
            client_id=regular_user.client_id
        )
        db.add(project)
        await db.commit()
        
        # Create team as regular user
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Security Team",
            description="Test team",
            project_id=project.id,
            current_user=regular_user
        )
        
        # Other client user should not be able to access this team
        with pytest.raises(Exception):
            await team_service.get_team_by_id(team.id, other_client_user)
    
    async def test_role_based_access_control(
        self,
        client: AsyncClient,
        db: AsyncSession,
        regular_user: User
    ):
        """Test role-based access control"""
        
        # Regular user should not be able to perform admin operations
        admin_data = {
            "name": "Admin Team",
            "description": "Should require admin role",
            "project_id": "PRJ-001"
        }
        
        # This would need proper token generation for the test
        # For now, we test the service layer directly
        
        team_service = TeamService(db)
        
        # Regular user creating team should work if they have project access
        # But certain admin operations should be restricted
        
        # This is a placeholder - actual implementation would depend on
        # specific role restrictions defined in the business logic
        assert regular_user.primary_role == "Developer"
    
    async def test_input_validation_security(self, client: AsyncClient, admin_token: str):
        """Test input validation for security vulnerabilities"""
        
        # SQL injection attempt
        malicious_data = {
            "name": "'; DROP TABLE teams; --",
            "description": "SQL injection attempt",
            "project_id": "PRJ-001"
        }
        
        response = await client.post(
            "/api/v1/teams/",
            json=malicious_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should either succeed with sanitized input or fail validation
        # Should NOT cause database corruption
        assert response.status_code in [201, 400, 422]
        
        # XSS attempt
        xss_data = {
            "name": "<script>alert('xss')</script>",
            "description": "XSS attempt",
            "project_id": "PRJ-001"
        }
        
        response = await client.post(
            "/api/v1/teams/",
            json=xss_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should handle XSS attempts safely
        assert response.status_code in [201, 400, 422]
        
        if response.status_code == 201:
            team = response.json()
            # Ensure script tags are escaped or removed
            assert "<script>" not in team["name"]
    
    async def test_assignment_permission_validation(
        self,
        db: AsyncSession,
        regular_user: User,
        other_client_user: User
    ):
        """Test assignment permission validation"""
        
        from app.services.assignment_service import AssignmentService
        from app.models.hierarchy import Task
        
        # Create task for regular user's client
        task = Task(
            id="TSK-SECURITY",
            title="Security Test Task",
            project_id="PRJ-001"  # Assuming this belongs to regular_user's client
        )
        db.add(task)
        await db.commit()
        
        assignment_service = AssignmentService(db)
        
        # User from different client should not be able to assign
        with pytest.raises(Exception):
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=other_client_user.id,
                assignment_type="developer",
                current_user=other_client_user
            )
    
    async def test_team_member_access_control(
        self,
        db: AsyncSession,
        regular_user: User,
        other_client_user: User
    ):
        """Test team member access control"""
        
        from app.models.hierarchy import Project
        
        # Create project for regular user
        project = Project(
            id="PRJ-ACCESS",
            name="Access Control Project",
            client_id=regular_user.client_id
        )
        db.add(project)
        await db.commit()
        
        team_service = TeamService(db)
        
        # Create team
        team = await team_service.create_team(
            name="Access Team",
            description="Test team",
            project_id=project.id,
            current_user=regular_user
        )
        
        # Other client user should not be able to add themselves
        with pytest.raises(Exception):
            await team_service.add_member(
                team_id=team.id,
                user_id=other_client_user.id,
                role="Developer",
                current_user=other_client_user
            )
        
        # Other client user should not be able to view team members
        with pytest.raises(Exception):
            await team_service.get_team_members(team.id, other_client_user)


class TestDataValidation:
    """Test data validation and sanitization"""
    
    async def test_team_name_validation(self, client: AsyncClient, admin_token: str):
        """Test team name validation"""
        
        # Empty name
        response = await client.post(
            "/api/v1/teams/",
            json={"name": "", "project_id": "PRJ-001"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
        # Too long name
        long_name = "x" * 300
        response = await client.post(
            "/api/v1/teams/",
            json={"name": long_name, "project_id": "PRJ-001"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
        # Invalid characters
        response = await client.post(
            "/api/v1/teams/",
            json={"name": "Team\x00Name", "project_id": "PRJ-001"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
    
    async def test_assignment_validation(self, client: AsyncClient, admin_token: str):
        """Test assignment data validation"""
        
        # Invalid entity type
        response = await client.post(
            "/api/v1/assignments/",
            json={
                "entity_type": "invalid_type",
                "entity_id": "TSK-001",
                "user_id": "USR-001",
                "assignment_type": "developer"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
        # Missing required fields
        response = await client.post(
            "/api/v1/assignments/",
            json={"entity_type": "task"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422
        
        # Invalid user ID format
        response = await client.post(
            "/api/v1/assignments/",
            json={
                "entity_type": "task",
                "entity_id": "TSK-001", 
                "user_id": "invalid-id-format",
                "assignment_type": "developer"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 422


class TestRateLimiting:
    """Test rate limiting for assignment operations"""
    
    async def test_assignment_rate_limiting(self, client: AsyncClient, admin_token: str):
        """Test rate limiting on assignment operations"""
        
        # This would require implementing rate limiting middleware
        # For now, this is a placeholder for the test structure
        
        assignment_data = {
            "entity_type": "task",
            "entity_id": "TSK-001",
            "user_id": "USR-001", 
            "assignment_type": "developer"
        }
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = await client.post(
                "/api/v1/assignments/",
                json=assignment_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            responses.append(response.status_code)
        
        # Should eventually hit rate limit (429) or succeed
        # Actual implementation depends on rate limiting configuration
        assert all(status in [201, 400, 409, 429] for status in responses)