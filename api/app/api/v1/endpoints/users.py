"""
User endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.core.security import get_current_user, require_role, get_password_hash
from app.core.exceptions import ResourceNotFoundException, ConflictException
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


@router.get("/me", response_model=UserResponse, response_model_by_alias=True)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.put("/me/preferences", response_model=UserResponse, response_model_by_alias=True)
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


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Create a new user (Admin only)."""
    
    # Check if user with this email already exists
    existing_user = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.scalar_one_or_none():
        raise ConflictException(f"User with email '{user_data.email}' already exists")
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        client_id=user_data.client_id,
        language=user_data.language,
        theme=user_data.theme,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.log_activity(
        action="create_user",
        entity_type="user",
        entity_id=new_user.id,
        user_email=new_user.email
    )
    
    return UserResponse.from_orm(new_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID."""
    
    query = select(User).where(User.id == user_id, User.is_active == True)
    
    # Non-admin users can only see users from their own client
    if current_user.role != "Admin":
        query = query.where(User.client_id == current_user.client_id)
    
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise ResourceNotFoundException("User", user_id)
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Update a user (Admin only)."""
    
    # Get the user to update
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ResourceNotFoundException("User", user_id)
    
    # Check for email conflicts if email is being updated
    if user_data.email is not None and user_data.email != user.email:
        existing_user = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if existing_user.scalar_one_or_none():
            raise ConflictException(f"User with email '{user_data.email}' already exists")
    
    # Update fields if provided
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.language is not None:
        user.language = user_data.language
    if user_data.theme is not None:
        user.theme = user_data.theme
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db.commit()
    await db.refresh(user)
    
    logger.log_activity(
        action="update_user",
        entity_type="user",
        entity_id=user_id,
        changes=user_data.dict(exclude_unset=True)
    )
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Soft delete a user (Admin only)."""
    
    # Get the user to delete
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ResourceNotFoundException("User", user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        raise ConflictException("Cannot delete your own account")
    
    # Soft delete by setting is_active to False
    user.is_active = False
    
    await db.commit()
    
    logger.log_activity(
        action="delete_user",
        entity_type="user",
        entity_id=user_id,
        user_email=user.email
    )
