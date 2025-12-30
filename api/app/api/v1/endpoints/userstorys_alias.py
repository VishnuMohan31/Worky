"""
Alias endpoint for userstorys -> user-stories
This provides backward compatibility for the frontend's pluralization.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.api.v1.endpoints.user_stories import list_user_stories

router = APIRouter()


@router.get("/")
async def list_userstorys_alias(
    usecase_id=None,
    status=None,
    priority=None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alias endpoint that forwards to the main user stories endpoint."""
    return await list_user_stories(
        usecase_id=usecase_id,
        status=status,
        priority=priority,
        skip=skip,
        limit=limit,
        db=db,
        current_user=current_user
    )
