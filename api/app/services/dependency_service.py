"""
Dependency validation and management service.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Set, Tuple, Optional
from uuid import UUID
from datetime import date

from app.models.dependency import Dependency
from app.models.hierarchy import Program, Project, Usecase, UserStory, Task, Subtask


class DependencyValidationError(Exception):
    """Custom exception for dependency validation errors"""
    pass


class DependencyService:
    """Service for dependency validation and management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def validate_circular_dependency(
        self,
        entity_type: str,
        entity_id: UUID,
        depends_on_type: str,
        depends_on_id: UUID
    ) -> bool:
        """
        Check if creating a dependency would create a circular dependency.
        
        Returns True if circular dependency would be created, False otherwise.
        """
        # If entity depends on itself, it's circular
        if entity_id == depends_on_id and entity_type == depends_on_type:
            return True
        
        # Check if depends_on_id already depends on entity_id (direct or indirect)
        visited: Set[Tuple[str, str]] = set()
        
        async def has_path(from_type: str, from_id: UUID, to_type: str, to_id: UUID) -> bool:
            """Check if there's a dependency path from 'from' to 'to'"""
            if (from_type, str(from_id)) in visited:
                return False
            
            visited.add((from_type, str(from_id)))
            
            # Get all dependencies of the 'from' entity
            result = await self.db.execute(
                select(Dependency).where(
                    and_(
                        Dependency.entity_type == from_type,
                        Dependency.entity_id == from_id
                    )
                )
            )
            dependencies = result.scalars().all()
            
            for dep in dependencies:
                # If we found a direct path to target
                if dep.depends_on_type == to_type and dep.depends_on_id == to_id:
                    return True
                
                # Recursively check if there's a path from this dependency to target
                if await has_path(dep.depends_on_type, dep.depends_on_id, to_type, to_id):
                    return True
            
            return False
        
        # Check if depends_on already has a path back to entity
        return await has_path(depends_on_type, depends_on_id, entity_type, entity_id)
    
    async def validate_scheduling_conflicts(
        self,
        entity_type: str,
        entity_id: UUID,
        depends_on_type: str,
        depends_on_id: UUID,
        dependency_type: str
    ) -> Optional[str]:
        """
        Validate that the dependency doesn't create scheduling conflicts.
        
        Returns None if valid, or error message if there's a conflict.
        """
        # Get entity dates
        entity_dates = await self._get_entity_dates(entity_type, entity_id)
        depends_on_dates = await self._get_entity_dates(depends_on_type, depends_on_id)
        
        if not entity_dates or not depends_on_dates:
            # If dates are not set, we can't validate scheduling
            return None
        
        entity_start, entity_end = entity_dates
        depends_on_start, depends_on_end = depends_on_dates
        
        # Validate based on dependency type
        if dependency_type == "finish_to_start":
            # Entity should start after dependency finishes
            if entity_start and depends_on_end and entity_start < depends_on_end:
                return f"Entity starts ({entity_start}) before dependency finishes ({depends_on_end}). Finish-to-start dependency violated."
        
        elif dependency_type == "start_to_start":
            # Entity should start at or after dependency starts
            if entity_start and depends_on_start and entity_start < depends_on_start:
                return f"Entity starts ({entity_start}) before dependency starts ({depends_on_start}). Start-to-start dependency violated."
        
        elif dependency_type == "finish_to_finish":
            # Entity should finish at or after dependency finishes
            if entity_end and depends_on_end and entity_end < depends_on_end:
                return f"Entity finishes ({entity_end}) before dependency finishes ({depends_on_end}). Finish-to-finish dependency violated."
        
        elif dependency_type == "start_to_finish":
            # Entity should finish at or after dependency starts
            if entity_end and depends_on_start and entity_end < depends_on_start:
                return f"Entity finishes ({entity_end}) before dependency starts ({depends_on_start}). Start-to-finish dependency violated."
        
        return None
    
    async def _get_entity_dates(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> Optional[Tuple[Optional[date], Optional[date]]]:
        """
        Get start and end dates for an entity.
        
        Returns (start_date, end_date) tuple or None if entity not found.
        """
        model_map = {
            "Program": Program,
            "Project": Project,
            "Usecase": Usecase,
            "UserStory": UserStory,
            "Task": Task,
            "Subtask": Subtask
        }
        
        model = model_map.get(entity_type)
        if not model:
            return None
        
        result = await self.db.execute(
            select(model).where(model.id == entity_id)
        )
        entity = result.scalar_one_or_none()
        
        if not entity:
            return None
        
        # Get dates based on entity type
        if hasattr(entity, 'start_date') and hasattr(entity, 'end_date'):
            return (entity.start_date, entity.end_date)
        elif hasattr(entity, 'start_date') and hasattr(entity, 'due_date'):
            return (entity.start_date, entity.due_date)
        
        return None
    
    async def get_dependency_chain(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> List[Dependency]:
        """
        Get the complete dependency chain for an entity.
        
        Returns all dependencies in the chain (direct and transitive).
        """
        visited: Set[Tuple[str, str]] = set()
        chain: List[Dependency] = []
        
        async def traverse(etype: str, eid: UUID):
            """Recursively traverse dependency chain"""
            if (etype, str(eid)) in visited:
                return
            
            visited.add((etype, str(eid)))
            
            # Get direct dependencies
            result = await self.db.execute(
                select(Dependency).where(
                    and_(
                        Dependency.entity_type == etype,
                        Dependency.entity_id == eid
                    )
                )
            )
            dependencies = result.scalars().all()
            
            for dep in dependencies:
                chain.append(dep)
                # Recursively get dependencies of this dependency
                await traverse(dep.depends_on_type, dep.depends_on_id)
        
        await traverse(entity_type, entity_id)
        return chain
    
    async def validate_dependency_chain(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> List[str]:
        """
        Validate the entire dependency chain for an entity.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        chain = await self.get_dependency_chain(entity_type, entity_id)
        
        for dep in chain:
            # Check for scheduling conflicts
            conflict = await self.validate_scheduling_conflicts(
                dep.entity_type,
                dep.entity_id,
                dep.depends_on_type,
                dep.depends_on_id,
                dep.dependency_type
            )
            if conflict:
                errors.append(conflict)
        
        return errors
    
    async def get_critical_path(
        self,
        entity_type: str,
        entity_id: UUID
    ) -> List[Dependency]:
        """
        Calculate the critical path for an entity's dependency chain.
        
        The critical path is the longest sequence of dependent tasks.
        """
        chain = await self.get_dependency_chain(entity_type, entity_id)
        
        # Build adjacency list
        graph = {}
        for dep in chain:
            key = (dep.entity_type, str(dep.entity_id))
            if key not in graph:
                graph[key] = []
            graph[key].append(dep)
        
        # Find longest path using DFS
        visited: Set[Tuple[str, str]] = set()
        longest_path: List[Dependency] = []
        
        async def dfs(etype: str, eid: UUID, current_path: List[Dependency]):
            nonlocal longest_path
            
            key = (etype, str(eid))
            if key in visited:
                return
            
            visited.add(key)
            
            if len(current_path) > len(longest_path):
                longest_path = current_path.copy()
            
            if key in graph:
                for dep in graph[key]:
                    current_path.append(dep)
                    await dfs(dep.depends_on_type, dep.depends_on_id, current_path)
                    current_path.pop()
            
            visited.remove(key)
        
        await dfs(entity_type, entity_id, [])
        return longest_path
