"""
Cache service for team assignment system performance optimization.
"""
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
import json
import hashlib
from functools import wraps

from app.core.logging import StructuredLogger

logger = StructuredLogger(__name__)


class CacheService:
    """In-memory cache service for team and assignment data"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl: Dict[str, datetime] = {}
        self.default_ttl = timedelta(minutes=15)
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = f"{prefix}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._ttl:
            return True
        return datetime.utcnow() > self._ttl[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache or self._is_expired(key):
            if key in self._cache:
                del self._cache[key]
                del self._ttl[key]
            return None
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache"""
        self._cache[key] = value
        self._ttl[key] = datetime.utcnow() + (ttl or self.default_ttl)
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern"""
        keys_to_delete = [key for key in self._cache.keys() if pattern in key]
        for key in keys_to_delete:
            self.delete(key)
    
    def team_membership_key(self, user_id: str, project_id: str) -> str:
        """Generate cache key for team membership"""
        return self._generate_key("team_membership", user_id=user_id, project_id=project_id)
    
    def eligible_users_key(self, entity_type: str, entity_id: str, assignment_type: str) -> str:
        """Generate cache key for eligible users"""
        return self._generate_key("eligible_users", 
                                entity_type=entity_type, 
                                entity_id=entity_id, 
                                assignment_type=assignment_type)
    
    def team_members_key(self, team_id: str) -> str:
        """Generate cache key for team members"""
        return self._generate_key("team_members", team_id=team_id)
    
    def user_assignments_key(self, user_id: str) -> str:
        """Generate cache key for user assignments"""
        return self._generate_key("user_assignments", user_id=user_id)
    
    def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cache entries for a user"""
        self.clear_pattern(f"user_id:{user_id}")
        self.clear_pattern(f"user_assignments")
    
    def invalidate_team_cache(self, team_id: str) -> None:
        """Invalidate all cache entries for a team"""
        self.clear_pattern(f"team_id:{team_id}")
        self.clear_pattern(f"team_members")
        self.clear_pattern(f"team_membership")
    
    def invalidate_project_cache(self, project_id: str) -> None:
        """Invalidate all cache entries for a project"""
        self.clear_pattern(f"project_id:{project_id}")
        self.clear_pattern(f"eligible_users")
    
    # Team-specific cache methods
    def get_team_members(self, team_id: str) -> Optional[List]:
        """Get team members from cache"""
        key = self.team_members_key(team_id)
        return self.get(key)
    
    def set_team_members(self, team_id: str, members: List) -> None:
        """Set team members in cache"""
        key = self.team_members_key(team_id)
        self.set(key, members)
    
    def invalidate_team_members(self, team_id: str) -> None:
        """Invalidate team members cache"""
        key = self.team_members_key(team_id)
        self.delete(key)
    
    def invalidate_user_teams(self, user_id: str) -> None:
        """Invalidate user teams cache"""
        self.clear_pattern(f"user_teams:{user_id}")
    
    def invalidate_project_team(self, project_id: str) -> None:
        """Invalidate project team cache"""
        self.clear_pattern(f"project_team:{project_id}")


# Global cache instance
cache_service = CacheService()


def cached(ttl: Optional[timedelta] = None, key_func: Optional[callable] = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_service._generate_key(
                    f"{func.__module__}.{func.__name__}", 
                    args=str(args), 
                    kwargs=kwargs
                )
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        return wrapper
    return decorator