"""
User endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.core.security import get_current_user
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users."""
    query = select(User).where(User.is_active == True)
    
    # Non-admin users can only see users from their own client
    if current_user.role != "Admin":
        query = query.where(User.client_id == current_user.client_id)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    logger.log_activity(
        action="list_users",
        entity_type="user"
    )
    
    return [UserResponse.from_orm(user) for user in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.put("/me/preferences", response_model=UserResponse)
async def update_user_preferences(
    preferences: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user preferences."""
    if preferences.theme:
        current_user.theme = preferences.theme
    if preferences.language:
        current_user.language = preferences.language
    
    await db.commit()
    await db.refresh(current_user)
    
    logger.log_activity(
        action="update_preferences",
        entity_type="user",
        entity_id=current_user.id
    )
    
    return UserResponse.from_orm(current_user)
