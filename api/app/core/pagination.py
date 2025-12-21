"""
Pagination utilities for team assignment system.
"""
from typing import List, Dict, Any, Optional, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import Select
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    per_page: int = 50
    max_per_page: int = 100
    
    def __post_init__(self):
        # Validate and adjust parameters
        self.page = max(1, self.page)
        self.per_page = min(max(1, self.per_page), self.max_per_page)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls, 
        items: List[T], 
        total: int, 
        pagination: PaginationParams
    ) -> 'PaginatedResponse[T]':
        """Create paginated response"""
        total_pages = ceil(total / pagination.per_page) if total > 0 else 1
        
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            per_page=pagination.per_page,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1
        )


class PaginationService:
    """Service for handling pagination operations"""
    
    @staticmethod
    async def paginate_query(
        db: AsyncSession,
        query: Select,
        pagination: PaginationParams,
        count_query: Optional[Select] = None
    ) -> tuple[List[Any], int]:
        """
        Paginate a SQLAlchemy query.
        
        Args:
            db: Database session
            query: Main query to paginate
            pagination: Pagination parameters
            count_query: Optional separate count query for performance
            
        Returns:
            Tuple of (items, total_count)
        """
        # Get total count
        if count_query is not None:
            count_result = await db.execute(count_query)
            total = count_result.scalar()
        else:
            # Use the main query for counting
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar()
        
        # Get paginated items
        paginated_query = query.offset(pagination.offset).limit(pagination.limit)
        items_result = await db.execute(paginated_query)
        items = items_result.scalars().all()
        
        return list(items), total or 0
    
    @staticmethod
    async def paginate_teams(
        db: AsyncSession,
        base_query: Select,
        pagination: PaginationParams,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Paginate teams with filtering"""
        from app.models.team import Team, TeamMember
        from app.models.hierarchy import Project
        
        # Apply filters
        if user_id:
            base_query = base_query.join(TeamMember).where(
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        
        if project_id:
            base_query = base_query.where(Team.project_id == project_id)
        
        # Get results
        teams, total = await PaginationService.paginate_query(db, base_query, pagination)
        
        # Convert to dict format
        team_dicts = []
        for team in teams:
            # Get project info
            project = await db.get(Project, team.project_id)
            
            # Get member count
            member_count_query = select(func.count(TeamMember.id)).where(
                TeamMember.team_id == team.id,
                TeamMember.is_active == True
            )
            member_count_result = await db.execute(member_count_query)
            member_count = member_count_result.scalar() or 0
            
            team_dicts.append({
                "id": team.id,
                "name": team.name,
                "description": team.description,
                "project_id": team.project_id,
                "project_name": project.name if project else None,
                "member_count": member_count,
                "is_active": team.is_active,
                "created_at": team.created_at
            })
        
        return PaginatedResponse.create(team_dicts, total, pagination)
    
    @staticmethod
    async def paginate_assignments(
        db: AsyncSession,
        base_query: Select,
        pagination: PaginationParams,
        user_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> PaginatedResponse[Dict[str, Any]]:
        """Paginate assignments with filtering"""
        from app.models.team import Assignment
        from app.models.user import User
        
        # Apply filters
        if user_id:
            base_query = base_query.where(Assignment.user_id == user_id)
        
        if entity_type:
            base_query = base_query.where(Assignment.entity_type == entity_type)
        
        # Get results
        assignments, total = await PaginationService.paginate_query(db, base_query, pagination)
        
        # Convert to dict format with user info
        assignment_dicts = []
        for assignment in assignments:
            user = await db.get(User, assignment.user_id)
            
            assignment_dicts.append({
                "id": assignment.id,
                "entity_type": assignment.entity_type,
                "entity_id": assignment.entity_id,
                "user_id": assignment.user_id,
                "user_name": user.full_name if user else None,
                "user_email": user.email if user else None,
                "assignment_type": assignment.assignment_type,
                "is_active": assignment.is_active,
                "assigned_at": assignment.assigned_at,
                "created_by": assignment.created_by
            })
        
        return PaginatedResponse.create(assignment_dicts, total, pagination)
    
    @staticmethod
    def create_pagination_params(
        page: int = 1,
        per_page: int = 50,
        max_per_page: int = 100
    ) -> PaginationParams:
        """Create pagination parameters with validation"""
        return PaginationParams(
            page=max(1, page),
            per_page=min(max(1, per_page), max_per_page),
            max_per_page=max_per_page
        )


# Create a global instance for easy import
pagination_service = PaginationService()