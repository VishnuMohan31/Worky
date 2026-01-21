from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserResponse
from app.core.security import verify_password, create_access_token, get_current_user
from datetime import timedelta
from app.core.config import settings

router = APIRouter()


@router.get("/test-no-auth")
async def test_no_auth():
    """Test endpoint with no authentication required."""
    return {"message": "Auth router test endpoint works without authentication", "status": "success"}


@router.post("/login", response_model=Token, response_model_by_alias=True)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create user response with string conversion
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        client_id=str(user.client_id),
        language=user.language,
        theme=user.theme,
        is_active=user.is_active,
        created_at=user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=UserResponse, response_model_by_alias=True)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        client_id=str(current_user.client_id),
        language=current_user.language,
        theme=current_user.theme,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
