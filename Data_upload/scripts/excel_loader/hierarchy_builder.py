"""
Hierarchy Builder component for managing parent-child relationships and reference resolution.

This module handles the creation and lookup of hierarchical entities (clients, programs, projects, etc.)
and resolves user references during the Excel import process.

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4
"""
import logging
import sys
import os
from typing import Dict, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

# Add workspace root and api directory to path for module imports
workspace_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, workspace_root)
sys.path.insert(0, os.path.join(workspace_root, 'api'))

from logging_utils import get_logger, log_info, log_warning, log_error

logger = get_logger("hierarchy_builder")


class HierarchyBuilder:
    """
    Manages hierarchical relationships and reference resolution during Excel import.
    
    Responsibilities:
    - Create or lookup client records
    - Create default programs for clients
    - Maintain ID mappings from Excel IDs to database UUIDs
    - Resolve user references by name or email
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the HierarchyBuilder.
        
        Args:
            db_session: Async database session for queries and inserts
        """
        self.db = db_session
        
        # ID mappings: entity_type -> {excel_id: db_id}
        self.id_mappings: Dict[str, Dict[str, str]] = {
            'clients': {},
            'programs': {},
            'projects': {},
            'usecases': {},
            'user_stories': {},
            'tasks': {},
            'subtasks': {},
            'users': {},
        }
        
        # Cache for user lookups to avoid repeated queries
        self._user_cache: Dict[str, Optional[str]] = {}
        
        # Cache for client lookups
        self._client_cache: Dict[str, str] = {}
        
        # Cache for program lookups
        self._program_cache: Dict[str, str] = {}
    
    async def get_or_create_client(self, client_name: str = None) -> str:
        """
        Get or create the default client for Excel imports.
        
        All Excel imports use a single default client: "DL_old_projects"
        
        Args:
            client_name: Ignored - kept for compatibility
        
        Returns:
            Client ID (UUID as string)
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        # Use a single default client for all Excel imports
        default_client_name = "DL_old"
        
        # Check cache first
        cache_key = default_client_name.lower()
        if cache_key in self._client_cache:
            log_info(logger, f"Client '{default_client_name}' found in cache")
            return self._client_cache[cache_key]
        
        try:
            from sqlalchemy import text
            from uuid import uuid4
            
            # Try to find existing client (case-insensitive)
            result = await self.db.execute(
                text("SELECT id FROM clients WHERE LOWER(name) = LOWER(:name) AND is_deleted = false"),
                {"name": default_client_name}
            )
            existing_client = result.fetchone()
            
            if existing_client:
                client_id = str(existing_client[0])
                log_info(logger, 
                    f"Found existing client: {default_client_name}",
                    client_name=default_client_name,
                    client_id=client_id,
                    action="reuse_existing"
                )
                self._client_cache[cache_key] = client_id
                return client_id
            
            # Create new client using raw SQL to avoid metadata conflicts
            # Generate a short ID (max 20 chars) - use first 20 chars of UUID without dashes
            new_client_id = str(uuid4()).replace('-', '')[:20]
            await self.db.execute(
                text("""
                    INSERT INTO clients (id, name, short_description, is_active, is_deleted, created_at, updated_at)
                    VALUES (:id, :name, :description, :is_active, :is_deleted, NOW(), NOW())
                """),
                {
                    "id": new_client_id,
                    "name": default_client_name,
                    "description": "Excel imports",
                    "is_active": True,
                    "is_deleted": False
                }
            )
            
            log_info(logger, 
                f"Created new client: {default_client_name}",
                client_name=default_client_name,
                client_id=new_client_id,
                action="create_new"
            )
            self._client_cache[cache_key] = new_client_id
            
            return new_client_id
            
        except SQLAlchemyError as e:
            error_msg = f"Database error while getting/creating client '{default_client_name}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise SQLAlchemyError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error while getting/creating client '{default_client_name}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    async def get_or_create_program(self, client_id: str, client_name: str = None) -> str:
        """
        Get or create the default program for Excel imports.
        
        All Excel imports use a single default program: "Imported Projects"
        
        Args:
            client_id: ID of the client
            client_name: Ignored - kept for compatibility
        
        Returns:
            Program ID (UUID as string)
            
        Raises:
            SQLAlchemyError: If database operation fails
            ValueError: If client_id is invalid
        """
        if not client_id:
            raise ValueError("Client ID cannot be empty")
        
        # Use a single default program name for all Excel imports
        program_name = "Imported Projects"
        
        cache_key = f"{client_id}:{program_name.lower()}"
        
        # Check cache first
        if cache_key in self._program_cache:
            log_info(logger, f"Program for client '{client_id}' found in cache")
            return self._program_cache[cache_key]
        
        try:
            from sqlalchemy import text
            from uuid import uuid4
            
            # Try to find existing program
            result = await self.db.execute(
                text("""
                    SELECT id FROM programs 
                    WHERE client_id = :client_id 
                    AND LOWER(name) = LOWER(:name) 
                    AND is_deleted = false
                """),
                {"client_id": client_id, "name": program_name}
            )
            existing_program = result.fetchone()
            
            if existing_program:
                program_id = str(existing_program[0])
                log_info(logger, 
                    f"Found existing program: {program_name}",
                    program_name=program_name,
                    program_id=program_id,
                    client_id=client_id,
                    action="reuse_existing"
                )
                self._program_cache[cache_key] = program_id
                return program_id
            
            # Create new program using raw SQL to avoid metadata conflicts
            # Generate a short ID (max 20 chars) - use first 20 chars of UUID without dashes
            new_program_id = str(uuid4()).replace('-', '')[:20]
            await self.db.execute(
                text("""
                    INSERT INTO programs (id, client_id, name, short_description, status, is_deleted, created_at, updated_at)
                    VALUES (:id, :client_id, :name, :description, :status, :is_deleted, NOW(), NOW())
                """),
                {
                    "id": new_program_id,
                    "client_id": client_id,
                    "name": program_name,
                    "description": "Excel imports",
                    "status": "Planning",
                    "is_deleted": False
                }
            )
            
            log_info(logger, 
                f"Created new program: {program_name}",
                program_name=program_name,
                program_id=new_program_id,
                client_id=client_id,
                action="create_new"
            )
            self._program_cache[cache_key] = new_program_id
            
            return new_program_id
            
        except SQLAlchemyError as e:
            error_msg = f"Database error while getting/creating program for client '{client_id}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise SQLAlchemyError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error while getting/creating program for client '{client_id}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    async def resolve_user_reference(self, user_identifier: str) -> Optional[str]:
        """
        Find user by name or email (case-insensitive).
        
        Attempts to match the user_identifier against both full_name and email fields.
        Logs a warning if no match is found.
        
        Args:
            user_identifier: User's name or email address
        
        Returns:
            User ID if found, None otherwise
        """
        if not user_identifier or not user_identifier.strip():
            return None
        
        user_identifier = user_identifier.strip()
        
        # Check cache first
        cache_key = user_identifier.lower()
        if cache_key in self._user_cache:
            cached_result = self._user_cache[cache_key]
            if cached_result:
                log_info(logger, f"User '{user_identifier}' found in cache")
            return cached_result
        
        try:
            # Import here to avoid circular imports
            from api.app.models.user import User
            
            # Try to find user by full_name or email (case-insensitive)
            result = await self.db.execute(
                select(User).where(
                    (func.lower(User.full_name) == user_identifier.lower()) |
                    (func.lower(User.email) == user_identifier.lower())
                )
            )
            user = result.scalar_one_or_none()
            
            if user:
                log_info(logger, 
                    f"Resolved user reference '{user_identifier}' to user ID: {user.id}",
                    user_identifier=user_identifier,
                    user_id=user.id,
                    user_name=user.full_name
                )
                self._user_cache[cache_key] = user.id
                return user.id
            else:
                log_warning(logger, 
                    f"User reference not found: '{user_identifier}'",
                    user_identifier=user_identifier,
                    lookup_type="user_resolution"
                )
                self._user_cache[cache_key] = None
                return None
                
        except SQLAlchemyError as e:
            error_msg = f"Database error while resolving user reference '{user_identifier}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            # Cache the failure to avoid repeated queries
            self._user_cache[cache_key] = None
            return None
            
        except Exception as e:
            error_msg = f"Unexpected error while resolving user reference '{user_identifier}': {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            self._user_cache[cache_key] = None
            return None
    
    async def get_or_create_default_phase(self, project_id: str) -> Optional[str]:
        """
        Get or create a default phase for a project.
        
        This is needed because tasks and subtasks require a phase_id.
        Creates a default "Imported" phase if none exists.
        
        Args:
            project_id: ID of the project
        
        Returns:
            Phase ID if successful, None otherwise
        """
        if not project_id:
            return None
        
        # Check cache first
        cache_key = f"phase_{project_id}"
        if cache_key in self._program_cache:  # Reuse program cache for phases
            return self._program_cache[cache_key]
        
        try:
            from sqlalchemy import text
            from uuid import uuid4
            
            # Try to find existing default phase for this project
            result = await self.db.execute(
                text("""
                    SELECT id FROM phases 
                    WHERE project_id = :project_id 
                    AND LOWER(name) = 'imported'
                    AND is_deleted = false
                    LIMIT 1
                """),
                {"project_id": project_id}
            )
            existing_phase = result.fetchone()
            
            if existing_phase:
                phase_id = str(existing_phase[0])
                log_info(logger, f"Found existing default phase for project {project_id}")
                self._program_cache[cache_key] = phase_id
                return phase_id
            
            # Create new default phase
            new_phase_id = str(uuid4()).replace('-', '')[:20]
            await self.db.execute(
                text("""
                    INSERT INTO phases (id, project_id, name, short_description, status, is_deleted, created_at, updated_at)
                    VALUES (:id, :project_id, :name, :description, :status, :is_deleted, NOW(), NOW())
                """),
                {
                    "id": new_phase_id,
                    "project_id": project_id,
                    "name": "Imported",
                    "description": "Default phase",
                    "status": "Active",
                    "is_deleted": False
                }
            )
            
            log_info(logger, f"Created default phase for project {project_id}")
            self._program_cache[cache_key] = new_phase_id
            return new_phase_id
            
        except Exception as e:
            log_error(logger, f"Error getting/creating default phase: {str(e)}", exc_info=True)
            return None
    
    def map_excel_id_to_db_id(self, entity_type: str, excel_id: str, db_id: str) -> None:
        """
        Store mapping from Excel ID to database ID.
        
        This allows child records to reference parent records using Excel IDs,
        which are then resolved to actual database IDs.
        
        Args:
            entity_type: Type of entity (projects, usecases, user_stories, tasks, subtasks)
            excel_id: ID from the Excel file
            db_id: Actual database ID (UUID or string ID)
        """
        if entity_type not in self.id_mappings:
            log_warning(logger, f"Unknown entity type for ID mapping: {entity_type}")
            return
        
        if not excel_id or not db_id:
            log_warning(logger, f"Cannot map empty IDs: excel_id={excel_id}, db_id={db_id}")
            return
        
        excel_id = str(excel_id).strip()
        db_id = str(db_id).strip()
        
        self.id_mappings[entity_type][excel_id] = db_id
        log_info(logger, f"Mapped {entity_type} Excel ID '{excel_id}' to DB ID '{db_id}'")
    
    def get_db_id_from_excel_id(self, entity_type: str, excel_id: str) -> Optional[str]:
        """
        Retrieve database ID from Excel ID.
        
        Args:
            entity_type: Type of entity (projects, usecases, user_stories, tasks, subtasks)
            excel_id: ID from the Excel file
        
        Returns:
            Database ID if mapping exists, None otherwise
        """
        if entity_type not in self.id_mappings:
            log_warning(logger, f"Unknown entity type for ID lookup: {entity_type}")
            return None
        
        if not excel_id:
            return None
        
        excel_id = str(excel_id).strip()
        db_id = self.id_mappings[entity_type].get(excel_id)
        
        if db_id is None:
            log_warning(logger, f"No database ID found for {entity_type} Excel ID: '{excel_id}'")
        
        return db_id
    
    def get_mapping_summary(self) -> Dict[str, int]:
        """
        Get a summary of ID mappings by entity type.
        
        Returns:
            Dictionary of entity type to count of mapped IDs
        """
        return {
            entity_type: len(mappings)
            for entity_type, mappings in self.id_mappings.items()
            if mappings
        }
    
    def clear_caches(self) -> None:
        """Clear all internal caches. Useful for testing or memory management."""
        self._user_cache.clear()
        self._client_cache.clear()
        self._program_cache.clear()
        log_info(logger, "Cleared all hierarchy builder caches")
