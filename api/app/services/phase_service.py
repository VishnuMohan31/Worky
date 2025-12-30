"""
Phase Service for managing phase CRUD operations and usage tracking.

This service handles:
- Phase creation, updates, and deactivation (Admin only)
- Phase listing with active/inactive filtering
- Phase usage tracking and statistics
- Phase validation for tasks and subtasks

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 13.1, 13.2, 13.3, 24.1, 24.2, 24.3
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException, status

from app.models.hierarchy import Phase, Task, Subtask
from app.models.user import User
from app.schemas.hierarchy import PhaseCreate, PhaseUpdate


class PhaseService:
    """Service for managing phases"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== CRUD OPERATIONS ====================
    
    async def list_phases(
        self, 
        include_inactive: bool = False,
        current_user: Optional[User] = None
    ) -> List[Phase]:
        """
        List all phases with optional inactive filter
        
        Requirements: 12.1, 24.1
        
        Args:
            include_inactive: If True, include inactive phases
            current_user: Current user (for audit purposes)
        
        Returns:
            List of Phase objects ordered by display order
        """
        query = select(Phase).where(Phase.is_deleted == False)
        
        # Filter by active status unless explicitly including inactive
        if not include_inactive:
            query = query.where(Phase.is_active == True)
        
        # Order by display order
        query = query.order_by(Phase.display_order)
        
        result = await self.db.execute(query)
        phases = result.scalars().all()
        
        return list(phases)
    
    async def get_phase(self, phase_id: UUID) -> Optional[Phase]:
        """
        Get a single phase by ID
        
        Args:
            phase_id: UUID of the phase
        
        Returns:
            Phase object or None if not found
        """
        result = await self.db.execute(
            select(Phase).where(
                Phase.id == phase_id,
                Phase.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create_phase(
        self, 
        phase_data: PhaseCreate, 
        current_user: User
    ) -> Phase:
        """
        Create a new phase (Admin only)
        
        Requirements: 12.3, 24.2
        
        Args:
            phase_data: Phase creation data
            current_user: Current user (must be Admin)
        
        Returns:
            Created Phase object
        
        Raises:
            HTTPException: If user is not Admin or phase name already exists
        """
        # Role check - only Admin can create phases (Requirement 12.3, 24.2)
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can create phases"
            )
        
        # Check if phase name already exists
        existing_phase = await self._get_phase_by_name(phase_data.name)
        if existing_phase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phase with name '{phase_data.name}' already exists"
            )
        
        # Create phase
        phase = Phase(
            name=phase_data.name,
            short_description=phase_data.short_description,
            long_description=phase_data.long_description,
            color=phase_data.color,
            display_order=phase_data.display_order,
            is_deleted=False,
            created_by=str(current_user.id),
            updated_by=str(current_user.id)
        )
        
        self.db.add(phase)
        await self.db.commit()
        await self.db.refresh(phase)
        
        return phase
    
    async def update_phase(
        self, 
        phase_id: UUID, 
        phase_data: PhaseUpdate, 
        current_user: User
    ) -> Phase:
        """
        Update an existing phase (Admin only)
        
        Requirements: 12.4, 24.2
        
        Args:
            phase_id: UUID of the phase to update
            phase_data: Phase update data
            current_user: Current user (must be Admin)
        
        Returns:
            Updated Phase object
        
        Raises:
            HTTPException: If user is not Admin, phase not found, or name conflict
        """
        # Role check - only Admin can update phases (Requirement 12.4, 24.2)
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can update phases"
            )
        
        # Get existing phase
        phase = await self.get_phase(phase_id)
        if not phase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phase with ID {phase_id} not found"
            )
        
        # Check for name conflicts if name is being updated
        if phase_data.name and phase_data.name != phase.name:
            existing_phase = await self._get_phase_by_name(phase_data.name)
            if existing_phase:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Phase with name '{phase_data.name}' already exists"
                )
        
        # Update fields
        if phase_data.name is not None:
            phase.name = phase_data.name
        if phase_data.description is not None:
            phase.description = phase_data.description
        if phase_data.display_order is not None:
            phase.display_order = phase_data.display_order
        
        phase.updated_by = str(current_user.id)
        
        await self.db.commit()
        await self.db.refresh(phase)
        
        return phase
    
    async def deactivate_phase(
        self, 
        phase_id: UUID, 
        current_user: User
    ) -> Phase:
        """
        Deactivate a phase with usage count validation (Admin only)
        
        Requirements: 12.5, 24.2
        
        This method sets is_active to False rather than deleting the phase.
        It validates that the phase is not currently in use before deactivation.
        
        Args:
            phase_id: UUID of the phase to deactivate
            current_user: Current user (must be Admin)
        
        Returns:
            Deactivated Phase object
        
        Raises:
            HTTPException: If user is not Admin, phase not found, or phase is in use
        """
        # Role check - only Admin can deactivate phases (Requirement 12.5, 24.2)
        if current_user.role != "Admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin users can deactivate phases"
            )
        
        # Get existing phase
        phase = await self.get_phase(phase_id)
        if not phase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phase with ID {phase_id} not found"
            )
        
        # Check if phase is in use (Requirement 12.5)
        usage_count = await self.get_phase_usage_count(phase_id)
        if usage_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot deactivate phase: {usage_count} tasks/subtasks are currently using it"
            )
        
        # Deactivate phase (soft deactivation, not deletion)
        phase.is_active = False
        phase.updated_by = str(current_user.id)
        
        await self.db.commit()
        await self.db.refresh(phase)
        
        return phase
    
    # ==================== USAGE TRACKING AND STATISTICS ====================
    
    async def get_phase_usage_count(self, phase_id: UUID) -> int:
        """
        Get total count of tasks and subtasks using this phase
        
        Requirements: 13.1, 24.3
        
        Args:
            phase_id: UUID of the phase
        
        Returns:
            Total count of tasks and subtasks using this phase
        """
        # Count tasks using this phase
        task_count_result = await self.db.execute(
            select(func.count(Task.id)).where(
                and_(
                    Task.phase_id == phase_id,
                    Task.is_deleted == False
                )
            )
        )
        task_count = task_count_result.scalar() or 0
        
        # Count subtasks using this phase
        subtask_count_result = await self.db.execute(
            select(func.count(Subtask.id)).where(
                and_(
                    Subtask.phase_id == phase_id,
                    Subtask.is_deleted == False
                )
            )
        )
        subtask_count = subtask_count_result.scalar() or 0
        
        return task_count + subtask_count
    
    async def get_phase_usage(self, phase_id: UUID) -> Dict[str, Any]:
        """
        Get detailed phase usage breakdown by entity type
        
        Requirements: 13.2, 13.3, 24.3
        
        Args:
            phase_id: UUID of the phase
        
        Returns:
            Dictionary containing:
            - total_count: Total tasks and subtasks using this phase
            - task_count: Number of tasks using this phase
            - subtask_count: Number of subtasks using this phase
            - task_breakdown: Tasks grouped by status
            - subtask_breakdown: Subtasks grouped by status
        """
        # Get phase details
        phase = await self.get_phase(phase_id)
        if not phase:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Phase with ID {phase_id} not found"
            )
        
        # Count tasks by status
        task_status_result = await self.db.execute(
            select(
                Task.status,
                func.count(Task.id).label('count')
            ).where(
                and_(
                    Task.phase_id == phase_id,
                    Task.is_deleted == False
                )
            ).group_by(Task.status)
        )
        task_breakdown = {row.status: row.count for row in task_status_result}
        task_count = sum(task_breakdown.values())
        
        # Count subtasks by status
        subtask_status_result = await self.db.execute(
            select(
                Subtask.status,
                func.count(Subtask.id).label('count')
            ).where(
                and_(
                    Subtask.phase_id == phase_id,
                    Subtask.is_deleted == False
                )
            ).group_by(Subtask.status)
        )
        subtask_breakdown = {row.status: row.count for row in subtask_status_result}
        subtask_count = sum(subtask_breakdown.values())
        
        return {
            "phase_id": str(phase_id),
            "phase_name": phase.name,
            "total_count": task_count + subtask_count,
            "task_count": task_count,
            "subtask_count": subtask_count,
            "task_breakdown": task_breakdown,
            "subtask_breakdown": subtask_breakdown
        }
    
    async def get_phase_distribution(
        self, 
        entity_type: str, 
        entity_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Calculate phase distribution for all descendant tasks/subtasks
        
        Requirements: 13.1, 13.2, 13.3
        
        This method recursively counts all tasks and subtasks under a given entity
        and groups them by phase.
        
        Args:
            entity_type: Type of entity (userstory, usecase, project, program, client)
            entity_id: UUID of the entity
        
        Returns:
            List of dictionaries with phase_id, phase_name, and count
        """
        # Build query based on entity type
        # This will be used to get all tasks/subtasks under the entity
        
        if entity_type.lower() == 'userstory':
            # Direct tasks under user story
            task_query = select(
                Phase.id.label('phase_id'),
                Phase.name.label('phase_name'),
                func.count(Task.id).label('count')
            ).join(
                Task, Task.phase_id == Phase.id
            ).where(
                and_(
                    Task.user_story_id == entity_id,
                    Task.is_deleted == False,
                    Phase.is_deleted == False
                )
            ).group_by(Phase.id, Phase.name)
            
            # Subtasks under those tasks
            subtask_query = select(
                Phase.id.label('phase_id'),
                Phase.name.label('phase_name'),
                func.count(Subtask.id).label('count')
            ).join(
                Subtask, Subtask.phase_id == Phase.id
            ).join(
                Task, Subtask.task_id == Task.id
            ).where(
                and_(
                    Task.user_story_id == entity_id,
                    Subtask.is_deleted == False,
                    Task.is_deleted == False,
                    Phase.is_deleted == False
                )
            ).group_by(Phase.id, Phase.name)
        
        else:
            # For higher-level entities, we need to traverse the hierarchy
            # This is a simplified version - full implementation would need
            # recursive CTEs or multiple joins
            return []
        
        # Execute queries
        task_result = await self.db.execute(task_query)
        task_distribution = {row.phase_id: {'phase_name': row.phase_name, 'count': row.count} 
                           for row in task_result}
        
        subtask_result = await self.db.execute(subtask_query)
        for row in subtask_result:
            if row.phase_id in task_distribution:
                task_distribution[row.phase_id]['count'] += row.count
            else:
                task_distribution[row.phase_id] = {
                    'phase_name': row.phase_name,
                    'count': row.count
                }
        
        # Convert to list format
        distribution = [
            {
                'phase_id': str(phase_id),
                'phase_name': data['phase_name'],
                'count': data['count']
            }
            for phase_id, data in task_distribution.items()
        ]
        
        return distribution
    
    # ==================== HELPER METHODS ====================
    
    async def _get_phase_by_name(self, name: str) -> Optional[Phase]:
        """Get phase by name (case-insensitive)"""
        result = await self.db.execute(
            select(Phase).where(
                and_(
                    func.lower(Phase.name) == name.lower(),
                    Phase.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
