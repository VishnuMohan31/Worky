"""
Performance tests for team assignment system.
"""
import pytest
import asyncio
import time
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.hierarchy import Project, Task
from app.models.team import Team
from app.services.team_service import TeamService
from app.services.assignment_service import AssignmentService
from app.services.query_optimization_service import QueryOptimizationService


class TestAssignmentPerformance:
    """Performance tests for assignment operations"""
    
    @pytest.fixture
    async def large_team_setup(self, db: AsyncSession) -> dict:
        """Setup for large team performance tests"""
        
        # Create admin user
        admin = User(
            id="USR-ADMIN-PERF",
            email="admin.perf@test.com",
            full_name="Admin Performance",
            primary_role="Admin",
            hashed_password="hashed",
            client_id="CLI-PERF"
        )
        db.add(admin)
        
        # Create project
        project = Project(
            id="PRJ-PERF",
            name="Performance Test Project",
            client_id="CLI-PERF"
        )
        db.add(project)
        
        # Create 100 users
        users = []
        for i in range(100):
            user = User(
                id=f"USR-PERF-{i:03d}",
                email=f"user{i}@test.com",
                full_name=f"User {i}",
                primary_role="Developer",
                hashed_password="hashed",
                client_id="CLI-PERF"
            )
            users.append(user)
            db.add(user)
        
        # Create 50 tasks
        tasks = []
        for i in range(50):
            task = Task(
                id=f"TSK-PERF-{i:03d}",
                title=f"Performance Task {i}",
                project_id=project.id
            )
            tasks.append(task)
            db.add(task)
        
        await db.commit()
        
        return {
            "admin": admin,
            "project": project,
            "users": users,
            "tasks": tasks
        }
    
    async def test_large_team_creation_performance(
        self,
        db: AsyncSession,
        large_team_setup: dict
    ):
        """Test performance of creating large teams"""
        
        admin = large_team_setup["admin"]
        project = large_team_setup["project"]
        users = large_team_setup["users"]
        
        team_service = TeamService(db)
        
        # Measure team creation time
        start_time = time.time()
        
        team = await team_service.create_team(
            name="Large Performance Team",
            description="Team with 100 members",
            project_id=project.id,
            current_user=admin
        )
        
        creation_time = time.time() - start_time
        
        # Should create team quickly (< 1 second)
        assert creation_time < 1.0
        
        # Measure bulk member addition time
        start_time = time.time()
        
        for user in users:
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin
            )
        
        addition_time = time.time() - start_time
        
        # Should add 100 members in reasonable time (< 10 seconds)
        assert addition_time < 10.0
        
        print(f"Team creation: {creation_time:.3f}s")
        print(f"100 member additions: {addition_time:.3f}s")
        print(f"Average per member: {addition_time/100:.3f}s")
    
    async def test_bulk_assignment_performance(
        self,
        db: AsyncSession,
        large_team_setup: dict
    ):
        """Test performance of bulk assignments"""
        
        admin = large_team_setup["admin"]
        project = large_team_setup["project"]
        users = large_team_setup["users"]
        tasks = large_team_setup["tasks"]
        
        # Create team and add all users
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Bulk Assignment Team",
            description="Team for bulk assignment test",
            project_id=project.id,
            current_user=admin
        )
        
        for user in users[:50]:  # Add 50 users
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin
            )
        
        # Measure bulk assignment performance
        assignment_service = AssignmentService(db)
        
        start_time = time.time()
        
        # Assign each task to a different user
        for i, task in enumerate(tasks):
            user = users[i % 50]  # Cycle through users
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=user.id,
                assignment_type="developer",
                current_user=admin
            )
        
        assignment_time = time.time() - start_time
        
        # Should complete 50 assignments in reasonable time (< 5 seconds)
        assert assignment_time < 5.0
        
        print(f"50 assignments: {assignment_time:.3f}s")
        print(f"Average per assignment: {assignment_time/50:.3f}s")
    
    async def test_concurrent_assignment_operations(
        self,
        db: AsyncSession,
        large_team_setup: dict
    ):
        """Test concurrent assignment operations"""
        
        admin = large_team_setup["admin"]
        project = large_team_setup["project"]
        users = large_team_setup["users"][:10]  # Use 10 users
        tasks = large_team_setup["tasks"][:10]  # Use 10 tasks
        
        # Setup team
        team_service = TeamService(db)
        team = await team_service.create_team(
            name="Concurrent Test Team",
            description="Team for concurrent test",
            project_id=project.id,
            current_user=admin
        )
        
        for user in users:
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin
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
                current_user=admin
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
        assert concurrent_time < 3.0
        assert len(successful_assignments) >= 8  # Allow some failures due to concurrency
    
    async def test_query_optimization_performance(
        self,
        db: AsyncSession,
        large_team_setup: dict
    ):
        """Test optimized query performance"""
        
        admin = large_team_setup["admin"]
        project = large_team_setup["project"]
        users = large_team_setup["users"][:20]
        tasks = large_team_setup["tasks"][:20]
        
        # Setup team with assignments
        team_service = TeamService(db)
        assignment_service = AssignmentService(db)
        
        team = await team_service.create_team(
            name="Query Optimization Team",
            description="Team for query optimization test",
            project_id=project.id,
            current_user=admin
        )
        
        for user in users:
            await team_service.add_member(
                team_id=team.id,
                user_id=user.id,
                role="Developer",
                current_user=admin
            )
        
        for i, task in enumerate(tasks):
            user = users[i % len(users)]
            await assignment_service.assign_entity(
                entity_type="task",
                entity_id=task.id,
                user_id=user.id,
                assignment_type="developer",
                current_user=admin
            )
        
        # Test optimized queries
        optimization_service = QueryOptimizationService(db)
        
        # Test team members query
        start_time = time.time()
        members = await optimization_service.get_team_members_optimized(team.id)
        members_time = time.time() - start_time
        
        assert len(members) == 20
        assert members_time < 0.5  # Should be very fast
        
        # Test workload summary
        start_time = time.time()
        workload = await optimization_service.get_team_workload_summary(team.id)
        workload_time = time.time() - start_time
        
        assert workload["member_count"] == 20
        assert workload_time < 1.0  # Should be reasonably fast
        
        # Test project stats
        start_time = time.time()
        stats = await optimization_service.get_project_assignment_stats(project.id)
        stats_time = time.time() - start_time
        
        assert stats["total_assignments"] == 20
        assert stats_time < 1.0  # Should be reasonably fast
        
        print(f"Team members query: {members_time:.3f}s")
        print(f"Workload summary: {workload_time:.3f}s")
        print(f"Project stats: {stats_time:.3f}s")
    
    async def test_memory_usage_under_load(
        self,
        db: AsyncSession,
        large_team_setup: dict
    ):
        """Test memory usage under load"""
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        admin = large_team_setup["admin"]
        project = large_team_setup["project"]
        users = large_team_setup["users"]
        
        team_service = TeamService(db)
        
        # Create multiple teams
        teams = []
        for i in range(10):
            team = await team_service.create_team(
                name=f"Memory Test Team {i}",
                description=f"Team {i} for memory test",
                project_id=project.id,
                current_user=admin
            )
            teams.append(team)
            
            # Add members to each team
            for j in range(10):
                user = users[j]
                await team_service.add_member(
                    team_id=team.id,
                    user_id=user.id,
                    role="Developer",
                    current_user=admin
                )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Initial memory: {initial_memory:.1f} MB")
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory increase: {memory_increase:.1f} MB")
        
        # Memory increase should be reasonable (< 50 MB for this test)
        assert memory_increase < 50.0


class TestScalabilityLimits:
    """Test system behavior at scale limits"""
    
    async def test_maximum_team_size(self, db: AsyncSession):
        """Test behavior with maximum team size"""
        
        # This test would create a very large team to test limits
        # Skipped in normal test runs due to time/resource requirements
        pytest.skip("Scalability test - run manually for performance validation")
    
    async def test_maximum_concurrent_users(self, db: AsyncSession):
        """Test behavior with many concurrent users"""
        
        # This test would simulate many concurrent users
        # Skipped in normal test runs due to complexity
        pytest.skip("Scalability test - run manually for performance validation")
    
    async def test_database_connection_pooling(self, db: AsyncSession):
        """Test database connection pooling under load"""
        
        # This test would stress test database connections
        # Skipped in normal test runs
        pytest.skip("Scalability test - run manually for performance validation")