"""
User endpoints for the Worky API.
"""
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.base import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserResponse, UserUpdate, UserCreate, PasswordChangeRequest
from app.core.security import get_current_user, require_role, get_password_hash, verify_password
from app.core.exceptions import ResourceNotFoundException, ConflictException
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


async def create_audit_log(
    db: AsyncSession,
    user_id: str,
    client_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    changes: dict = None
):
    """Create an audit log entry for user operations."""
    try:
        audit_log = AuditLog(
            user_id=user_id,
            client_id=client_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes  # JSONB accepts dict directly
        )
        db.add(audit_log)
        logger.debug(f"Audit log added for {action} on {entity_type} {entity_id}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}", exc_info=True)
        # Don't fail the main operation if audit logging fails


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all users."""
    # Show all users (both active and inactive) for admins to manage
    query = select(User)
    
    # Non-admin users can only see active users from their own client
    if current_user.role != "Admin":
        query = query.where(User.client_id == current_user.client_id).where(User.is_active == True)
    
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


@router.post("/me/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's password."""
    logger.info(f"Password change request received for user: {current_user.id}")
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        logger.warning(f"Password change failed: Incorrect current password for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password (minimum length check)
    if len(password_data.new_password) < 6:
        logger.warning(f"Password change failed: New password too short for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    
    await db.commit()
    await db.refresh(current_user)
    
    logger.log_activity(
        action="change_password",
        entity_type="user",
        entity_id=current_user.id
    )
    
    logger.info(f"Password changed successfully for user: {current_user.id}")
    return {"message": "Password changed successfully"}


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
    # Set primary_role to match role (for backward compatibility)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,
        primary_role=user_data.role,  # Sync primary_role with role
        client_id=user_data.client_id,
        language=user_data.language,
        theme=user_data.theme,
        is_active=True
    )
    
    db.add(new_user)
    await db.flush()  # Flush to get the ID without committing
    
    # Create audit log before committing
    try:
        await create_audit_log(
            db=db,
            user_id=str(current_user.id),
            client_id=str(current_user.client_id),
            action="CREATE",
            entity_type="user",
            entity_id=str(new_user.id),
            changes={"email": new_user.email, "full_name": new_user.full_name, "role": new_user.role}
        )
    except Exception as e:
        logger.error(f"Failed to create audit log for new user: {e}", exc_info=True)
        # Continue even if audit log fails - don't rollback the user creation
    
    await db.commit()  # Commit both user and audit log
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
    
    # Admins can see all users (both active and inactive), non-admins only active users from their client
    query = select(User).where(User.id == user_id)
    
    if current_user.role != "Admin":
        query = query.where(User.client_id == current_user.client_id).where(User.is_active == True)
    
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
    
    # Get the user to update (admins can update any user including inactive ones)
    result = await db.execute(
        select(User).where(User.id == user_id)
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
    
    # Track changes for audit log
    changes_dict = {}
    
    # Update fields if provided
    if user_data.full_name is not None and user_data.full_name != user.full_name:
        changes_dict["full_name"] = {"old": user.full_name, "new": user_data.full_name}
        user.full_name = user_data.full_name
    if user_data.email is not None and user_data.email != user.email:
        changes_dict["email"] = {"old": user.email, "new": user_data.email}
        user.email = user_data.email
    if user_data.role is not None and user_data.role != user.role:
        changes_dict["role"] = {"old": user.role, "new": user_data.role}
        user.role = user_data.role
        # If primary_role not explicitly set, sync it with role
        if user_data.primary_role is None:
            user.primary_role = user_data.role
    if user_data.primary_role is not None and user_data.primary_role != user.primary_role:
        changes_dict["primary_role"] = {"old": user.primary_role, "new": user_data.primary_role}
        user.primary_role = user_data.primary_role
    if user_data.secondary_roles is not None:
        changes_dict["secondary_roles"] = {"old": user.secondary_roles, "new": user_data.secondary_roles}
        user.secondary_roles = user_data.secondary_roles
    if user_data.is_contact_person is not None and user_data.is_contact_person != user.is_contact_person:
        changes_dict["is_contact_person"] = {"old": user.is_contact_person, "new": user_data.is_contact_person}
        user.is_contact_person = user_data.is_contact_person
    if user_data.client_id is not None and user_data.client_id != user.client_id:
        changes_dict["client_id"] = {"old": user.client_id, "new": user_data.client_id}
        user.client_id = user_data.client_id
    if user_data.language is not None and user_data.language != user.language:
        changes_dict["language"] = {"old": user.language, "new": user_data.language}
        user.language = user_data.language
    if user_data.theme is not None and user_data.theme != user.theme:
        changes_dict["theme"] = {"old": user.theme, "new": user_data.theme}
        user.theme = user_data.theme
    if user_data.is_active is not None and user_data.is_active != user.is_active:
        changes_dict["is_active"] = {"old": user.is_active, "new": user_data.is_active}
        user.is_active = user_data.is_active
    
    await db.commit()
    await db.refresh(user)
    
    # Create audit log if there were changes
    if changes_dict:
        await create_audit_log(
            db=db,
            user_id=str(current_user.id),
            client_id=str(current_user.client_id),
            action="UPDATE",
            entity_type="user",
            entity_id=user_id,
            changes=changes_dict
        )
        await db.commit()  # Commit the audit log
    
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
    """Soft delete a user by marking as inactive (Admin only)."""
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise ConflictException("Cannot delete your own account")
    
    # Check if user exists and is active
    result = await db.execute(
        text("SELECT is_active FROM users WHERE id = :user_id"),
        {"user_id": user_id}
    )
    user_data = result.fetchone()
    
    if not user_data:
        raise ResourceNotFoundException("User", user_id)
    
    if not user_data[0]:  # is_active is False
        raise ConflictException("User is already inactive")
    
    # Simple direct SQL update - no ORM objects involved
    await db.execute(
        text("UPDATE users SET is_active = false WHERE id = :user_id"),
        {"user_id": user_id}
    )
    
    await db.commit()


@router.put("/{user_id}/reactivate", response_model=UserResponse)
async def reactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["Admin"]))
):
    """Reactivate an inactive user (Admin only)."""
    
    # Get the user to reactivate
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ResourceNotFoundException("User", user_id)
    
    # Check if user is already active
    if user.is_active:
        raise ConflictException("User is already active")
    
    # Simple approach: just update the is_active field
    await db.execute(
        text("UPDATE users SET is_active = true WHERE id = :user_id"),
        {"user_id": user_id}
    )
    
    await db.commit()
    
    # Refresh the user object to get updated data
    await db.refresh(user)
    
    logger.log_activity(
        action="reactivate_user",
        entity_type="user",
        entity_id=user_id,
        user_email=user.email,
        note="User reactivated"
    )
    
    return UserResponse.from_orm(user)
