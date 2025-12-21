"""
Performance monitoring and optimization endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import time
import psutil
import os

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.query_optimization_service import QueryOptimizationService
from app.services.cache_service import cache_service
from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)
router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get cache statistics"""
    return {
        "cache_size": len(cache_service._cache),
        "ttl_entries": len(cache_service._ttl),
        "memory_usage_mb": psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    }


@router.delete("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Pattern to match for selective clearing"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Clear cache entries"""
    if pattern:
        cache_service.clear_pattern(pattern)
        return {"message": f"Cleared cache entries matching pattern: {pattern}"}
    else:
        cache_service._cache.clear()
        cache_service._ttl.clear()
        return {"message": "All cache entries cleared"}


@router.get("/teams/{team_id}/workload")
async def get_team_workload(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get optimized team workload summary"""
    start_time = time.time()
    
    optimization_service = QueryOptimizationService(db)
    workload = await optimization_service.get_team_workload_summary(team_id)
    
    execution_time = time.time() - start_time
    workload["execution_time_ms"] = round(execution_time * 1000, 2)
    
    return workload


@router.get("/projects/{project_id}/stats")
async def get_project_stats(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get optimized project assignment statistics"""
    start_time = time.time()
    
    optimization_service = QueryOptimizationService(db)
    stats = await optimization_service.get_project_assignment_stats(project_id)
    
    execution_time = time.time() - start_time
    stats["execution_time_ms"] = round(execution_time * 1000, 2)
    
    return stats


@router.get("/system/health")
async def system_health() -> Dict[str, Any]:
    """Get system health metrics"""
    process = psutil.Process(os.getpid())
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_usage_mb": process.memory_info().rss / 1024 / 1024,
        "memory_percent": process.memory_percent(),
        "cache_entries": len(cache_service._cache),
        "uptime_seconds": time.time() - process.create_time()
    }