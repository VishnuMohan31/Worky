"""
User Story endpoints for the Worky API.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.db.base import get_db
from app.models.hierarchy import UserStory, Usecase, Project, Program
from app.models.user import User
from app.schemas.hierarchy import UserStoryCreate, UserStoryUpdate, UserStoryResponse
from app.core.security import get_current_user, require_role
from app.core.exceptions import ResourceNotFoundException, AccessDeniedException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[UserStoryResponse])
async def list_user_stories(
    usecase_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user stories with optional filters."""
    
    query = select(UserStory).where(UserStory.is_deleted == False)
    
    if usecase_id:
        query = query.where(UserStory.usecase_id == usecase_id)
    if status:
        query = query.where(UserStory.status == status)
    if priority:
        query = query.where(UserStory.priority == priority)
    
    # Apply client-level filtering for non-admin users
    if current_user.role != "Admin":
        query = query.join(Usecase).join(Project).join(Program).where(
            Program.client_id == current_user.client_id
        )
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    stories = result.scalars().all()
    
    return [UserStoryResponse.from_orm(story) for story in stories]


@router.get("/{story_id}", response_model=UserStoryResponse)
async def get_user_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user story by ID."""
    
    result = await db.execute(
        select(UserStory).where(
            and_(
                UserStory.id == story_id,
                UserStory.is_deleted == False
            )
        )
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise ResourceNotFoundException("UserStory", str(story_id))
    
    # Check access
    if current_user.role != "Admin":
        usecase_result = await db.execute(
            select(Usecase).join(Project).join(Program).where(
                and_(
                    Usecase.id == story.usecase_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not usecase_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    logger.log_activity(
        action="view_user_story",
        entity_type="user_story",
        entity_id=str(story_id)
    )
    
    return UserStoryResponse.from_orm(story)


@router.post("/", response_model=UserStoryResponse, status_code=status.HTTP_201_CREATED)
async def create_user_story(
    story_data: UserStoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Create a new user story."""
    
    # Verify usecase exists
    usecase_result = await db.execute(
        select(Usecase).where(Usecase.id == story_data.usecase_id)
    )
    usecase = usecase_result.scalar_one_or_none()
    
    if not usecase:
        raise ResourceNotFoundException("Usecase", str(story_data.usecase_id))
    
    # Check access
    if current_user.role != "Admin":
        project_result = await db.execute(
            select(Project).where(Project.id == usecase.project_id)
        )
        project = project_result.scalar_one_or_none()
        if not project:
            raise ResourceNotFoundException("Project", str(usecase.project_id))
        
        # Get the program to access client_id
        program_result = await db.execute(
            select(Program).where(Program.id == project.program_id)
        )
        program = program_result.scalar_one_or_none()
        if not program or program.client_id != current_user.client_id:
            raise AccessDeniedException()
    
    story = UserStory(
        **story_data.dict(),
        created_by=str(current_user.id),
        updated_by=str(current_user.id)
    )
    
    db.add(story)
    await db.commit()
    await db.refresh(story)
    
    logger.log_activity(
        action="create_user_story",
        entity_type="user_story",
        entity_id=str(story.id),
        usecase_id=str(story.usecase_id)
    )
    
    return UserStoryResponse.from_orm(story)


@router.put("/{story_id}", response_model=UserStoryResponse)
async def update_user_story(
    story_id: str,
    story_data: UserStoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect", "Designer"]))
):
    """Update a user story."""
    
    result = await db.execute(
        select(UserStory).where(
            and_(
                UserStory.id == story_id,
                UserStory.is_deleted == False
            )
        )
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise ResourceNotFoundException("UserStory", str(story_id))
    
    # Check access
    if current_user.role != "Admin":
        usecase_result = await db.execute(
            select(Usecase).join(Project).join(Program).where(
                and_(
                    Usecase.id == story.usecase_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not usecase_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    # Update fields
    for field, value in story_data.dict(exclude_unset=True).items():
        setattr(story, field, value)
    
    story.updated_by = str(current_user.id)
    
    await db.commit()
    await db.refresh(story)
    
    logger.log_activity(
        action="update_user_story",
        entity_type="user_story",
        entity_id=str(story_id)
    )
    
    return UserStoryResponse.from_orm(story)


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_story(
    story_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin", "Architect"]))
):
    """Soft delete a user story."""
    
    result = await db.execute(
        select(UserStory).where(
            and_(
                UserStory.id == story_id,
                UserStory.is_deleted == False
            )
        )
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise ResourceNotFoundException("UserStory", str(story_id))
    
    # Check access
    if current_user.role != "Admin":
        usecase_result = await db.execute(
            select(Usecase).join(Project).join(Program).where(
                and_(
                    Usecase.id == story.usecase_id,
                    Program.client_id == current_user.client_id
                )
            )
        )
        if not usecase_result.scalar_one_or_none():
            raise AccessDeniedException()
    
    story.is_deleted = True
    story.updated_by = str(current_user.id)
    
    await db.commit()
    
    logger.log_activity(
        action="delete_user_story",
        entity_type="user_story",
        entity_id=str(story_id)
    )
