"""
Utility functions for the Worky API.
"""
import uuid
import hashlib
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    # Generate a short unique ID using timestamp and random component
    timestamp = int(datetime.now().timestamp() * 1000)  # milliseconds
    random_part = str(uuid.uuid4())[:8]  # first 8 chars of UUID
    
    if prefix:
        return f"{prefix}-{timestamp}-{random_part}".upper()
    else:
        return f"{timestamp}-{random_part}".upper()


def generate_short_id(prefix: str = "", length: int = 8) -> str:
    """Generate a shorter unique ID."""
    # Use MD5 hash of UUID for shorter IDs
    unique_str = str(uuid.uuid4())
    hash_obj = hashlib.md5(unique_str.encode())
    short_hash = hash_obj.hexdigest()[:length]
    
    if prefix:
        return f"{prefix}-{short_hash}".upper()
    else:
        return short_hash.upper()


def validate_entity_type(entity_type: str) -> bool:
    """Validate if entity type is supported."""
    valid_types = ['client', 'program', 'project', 'usecase', 'userstory', 'task', 'subtask']
    return entity_type.lower() in valid_types


def validate_assignment_type(assignment_type: str) -> bool:
    """Validate if assignment type is supported."""
    valid_types = ['owner', 'contact_person', 'developer']
    return assignment_type.lower() in valid_types