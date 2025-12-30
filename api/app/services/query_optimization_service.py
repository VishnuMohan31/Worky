"""
Query optimization service for team assignment system.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, and_, or_
from sqlalchemy.orm import selectinload, joinedload

from app.models.team import Team, TeamMember, Assignment
from app.models.user import User
from app.models.hierarchy import Project, Task, Subtask
from app.services.cache_service import cache_service, cached
from datetime import timedelta


class QueryOptimizationService:
    """Service for optimized database queries"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @cached(ttl=timedelta(minutes=10))
    async def get_team_members_optimized(self, team_id: str) -> List[Dict[str, Any]]:
        """Optimized query for team members with user details"""
        query = (
            select(TeamMember, User)
            .join(User, TeamMember.user_id == User.id)
            .where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.is_active == True,
                    User.is_active == True
                )
            )
            .options(joinedload(TeamMember.user))
        )
        
        result = await self.db.execute(query)
        members = []
        
        for team_member, user in result:
            members.append({
                "id": team_member.id,
                "user_id": user.id,
                "user_name": user.full_name,
                "user_email": user.email,
                "role": team_member.role,
                "joined_at": team_member.joined_at
            })
        
        return members
    
    @cached(ttl=timedelta(minutes=5))
    async def get_user_team_memberships(self, user_id: str) -> List[Dict[str, Any]]:
        """Optimized query for user's team memberships"""
        query = (
            select(TeamMember, Team, Project)
            .join(Team, TeamMember.team_id == Team.id)
            .join(Project, Team.project_id == Project.id)
            .where(
                and_(
                    TeamMember.user_id == user_id,
                    TeamMember.is_active == True,
                    Team.is_active == True
                )
            )
        )
        
        result = await self.db.execute(query)
        memberships = []
        
        for team_member, team, project in result:
            memberships.append({
                "team_id": team.id,
                "team_name": team.name,
                "project_id": project.id,
                "project_name": project.name,
                "role": team_member.role,
                "joined_at": team_member.joined_at
            })
        
        return memberships
    
    async def get_assignments_with_context(
        self, 
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Optimized query for assignments with full context"""
        
        # Build base query
        base_query = """
        SELECT 
            a.id as assignment_id,
            a.entity_type,
            a.entity_id,
            a.assignment_type,
            a.assigned_at,
            u.id as user_id,
            u.full_name as user_name,
            u.email as user_email,
            CASE 
                WHEN a.entity_type = 'task' THEN t.title
                WHEN a.entity_type = 'subtask' THEN s.title
                WHEN a.entity_type = 'userstory' THEN us.title
                ELSE NULL
            END as entity_title,
            CASE 
                WHEN a.entity_type = 'task' THEN t.project_id
                WHEN a.entity_type = 'subtask' THEN t2.project_id
                WHEN a.entity_type = 'userstory' THEN us.project_id
                ELSE NULL
            END as project_id,
            p.name as project_name
        FROM assignments a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN tasks t ON a.entity_type = 'task' AND a.entity_id = t.id
        LEFT JOIN subtasks s ON a.entity_type = 'subtask' AND a.entity_id = s.id
        LEFT JOIN tasks t2 ON a.entity_type = 'subtask' AND s.task_id = t2.id
        LEFT JOIN user_stories us ON a.entity_type = 'userstory' AND a.entity_id = us.id
        LEFT JOIN projects p ON (
            (a.entity_type = 'task' AND t.project_id = p.id) OR
            (a.entity_type = 'subtask' AND t2.project_id = p.id) OR
            (a.entity_type = 'userstory' AND us.project_id = p.id)
        )
        WHERE a.is_active = true
        """
        
        params = {}
        conditions = []
        
        if user_id:
            conditions.append("a.user_id = :user_id")
            params["user_id"] = user_id
        
        if project_id:
            conditions.append("""
                (
                    (a.entity_type = 'task' AND t.project_id = :project_id) OR
                    (a.entity_type = 'subtask' AND t2.project_id = :project_id) OR
                    (a.entity_type = 'userstory' AND us.project_id = :project_id)
                )
            """)
            params["project_id"] = project_id
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        base_query += " ORDER BY a.assigned_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = await self.db.execute(text(base_query), params)
        
        assignments = []
        for row in result:
            assignments.append({
                "assignment_id": row.assignment_id,
                "entity_type": row.entity_type,
                "entity_id": row.entity_id,
                "entity_title": row.entity_title,
                "assignment_type": row.assignment_type,
                "assigned_at": row.assigned_at,
                "user_id": row.user_id,
                "user_name": row.user_name,
                "user_email": row.user_email,
                "project_id": row.project_id,
                "project_name": row.project_name
            })
        
        return assignments
    
    async def get_team_workload_summary(self, team_id: str) -> Dict[str, Any]:
        """Get workload summary for a team"""
        
        query = text("""
        SELECT 
            tm.user_id,
            u.full_name,
            COUNT(a.id) as total_assignments,
            COUNT(CASE WHEN a.entity_type = 'task' THEN 1 END) as task_count,
            COUNT(CASE WHEN a.entity_type = 'subtask' THEN 1 END) as subtask_count,
            COUNT(CASE WHEN a.entity_type = 'userstory' THEN 1 END) as userstory_count
        FROM team_members tm
        JOIN users u ON tm.user_id = u.id
        LEFT JOIN assignments a ON tm.user_id = a.user_id AND a.is_active = true
        WHERE tm.team_id = :team_id AND tm.is_active = true
        GROUP BY tm.user_id, u.full_name
        ORDER BY total_assignments DESC
        """)
        
        result = await self.db.execute(query, {"team_id": team_id})
        
        workload = []
        total_assignments = 0
        
        for row in result:
            member_workload = {
                "user_id": row.user_id,
                "user_name": row.full_name,
                "total_assignments": row.total_assignments,
                "task_count": row.task_count,
                "subtask_count": row.subtask_count,
                "userstory_count": row.userstory_count
            }
            workload.append(member_workload)
            total_assignments += row.total_assignments
        
        return {
            "team_id": team_id,
            "total_assignments": total_assignments,
            "member_count": len(workload),
            "avg_assignments_per_member": total_assignments / len(workload) if workload else 0,
            "members": workload
        }
    
    async def get_project_assignment_stats(self, project_id: str) -> Dict[str, Any]:
        """Get assignment statistics for a project"""
        
        query = text("""
        SELECT 
            entity_type,
            assignment_type,
            COUNT(*) as count,
            COUNT(DISTINCT user_id) as unique_users
        FROM assignments a
        WHERE a.is_active = true
        AND (
            (entity_type = 'task' AND entity_id IN (SELECT id FROM tasks WHERE project_id = :project_id)) OR
            (entity_type = 'subtask' AND entity_id IN (
                SELECT s.id FROM subtasks s 
                JOIN tasks t ON s.task_id = t.id 
                WHERE t.project_id = :project_id
            )) OR
            (entity_type = 'userstory' AND entity_id IN (SELECT id FROM user_stories WHERE project_id = :project_id))
        )
        GROUP BY entity_type, assignment_type
        ORDER BY entity_type, assignment_type
        """)
        
        result = await self.db.execute(query, {"project_id": project_id})
        
        stats = {
            "project_id": project_id,
            "by_entity_type": {},
            "by_assignment_type": {},
            "total_assignments": 0,
            "total_unique_users": 0
        }
        
        unique_users = set()
        
        for row in result:
            # By entity type
            if row.entity_type not in stats["by_entity_type"]:
                stats["by_entity_type"][row.entity_type] = 0
            stats["by_entity_type"][row.entity_type] += row.count
            
            # By assignment type
            if row.assignment_type not in stats["by_assignment_type"]:
                stats["by_assignment_type"][row.assignment_type] = 0
            stats["by_assignment_type"][row.assignment_type] += row.count
            
            stats["total_assignments"] += row.count
        
        # Get unique users count
        unique_users_query = text("""
        SELECT COUNT(DISTINCT a.user_id) as unique_users
        FROM assignments a
        WHERE a.is_active = true
        AND (
            (entity_type = 'task' AND entity_id IN (SELECT id FROM tasks WHERE project_id = :project_id)) OR
            (entity_type = 'subtask' AND entity_id IN (
                SELECT s.id FROM subtasks s 
                JOIN tasks t ON s.task_id = t.id 
                WHERE t.project_id = :project_id
            )) OR
            (entity_type = 'userstory' AND entity_id IN (SELECT id FROM user_stories WHERE project_id = :project_id))
        )
        """)
        
        unique_result = await self.db.execute(unique_users_query, {"project_id": project_id})
        stats["total_unique_users"] = unique_result.scalar() or 0
        
        return stats
    
    async def bulk_check_team_membership(self, user_project_pairs: List[tuple]) -> Dict[tuple, bool]:
        """Bulk check team membership for multiple user-project pairs"""
        
        if not user_project_pairs:
            return {}
        
        # Build query for bulk checking
        conditions = []
        params = {}
        
        for i, (user_id, project_id) in enumerate(user_project_pairs):
            conditions.append(f"(tm.user_id = :user_id_{i} AND t.project_id = :project_id_{i})")
            params[f"user_id_{i}"] = user_id
            params[f"project_id_{i}"] = project_id
        
        query = text(f"""
        SELECT tm.user_id, t.project_id
        FROM team_members tm
        JOIN teams t ON tm.team_id = t.id
        WHERE tm.is_active = true 
        AND t.is_active = true
        AND ({' OR '.join(conditions)})
        """)
        
        result = await self.db.execute(query, params)
        
        # Build result mapping
        found_pairs = {(row.user_id, row.project_id) for row in result}
        
        return {
            pair: pair in found_pairs 
            for pair in user_project_pairs
        }