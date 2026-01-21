"""
Public subtask endpoints that don't require authentication.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.hierarchy import Subtask
from app.schemas.hierarchy import SubtaskResponse
from app.core.logging import StructuredLogger

router = APIRouter()
logger = StructuredLogger(__name__)


@router.get("/subtasks-public", response_model=List[SubtaskResponse])
async def list_subtasks_public(
    task_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List subtasks without authentication - returns empty list for security."""
    
    # For security, always return empty list for unauthenticated requests
    # This prevents the automatic logout issue while maintaining security
    logger.info(f"Public subtasks request for task_id: {task_id}")
    return []


@router.get("/test-public")
async def test_public():
    """Test endpoint to verify public access works."""
    return {"message": "Public endpoint works", "status": "success"}