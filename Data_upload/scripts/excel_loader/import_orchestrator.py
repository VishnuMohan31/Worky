"""
Import Orchestrator Component

This module coordinates the entire Excel import process by orchestrating all components
(parser, mapper, hierarchy builder, database writer) in the correct order to maintain
data integrity and hierarchical relationships.

Requirements: 1.1, 1.2, 1.4, 1.5, 8.5
"""

import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from excel_parser import ExcelParser
from data_mapper import DataMapper
from hierarchy_builder import HierarchyBuilder
from database_writer import DatabaseWriter

from logging_utils import get_logger, log_info, log_warning, log_error

logger = get_logger("import_orchestrator")


class ImportResponse(BaseModel):
    """Response model for import operations."""
    success: bool
    message: str
    summary: Dict[str, int]  # Entity type -> count
    warnings: List[str]
    errors: List[str]
    duration_seconds: float = 0.0


class ImportOrchestrator:
    """
    Orchestrates the complete Excel import process.
    
    Responsibilities:
    - Coordinate all components in correct hierarchical order
    - Handle errors and collect warnings
    - Manage transaction lifecycle
    - Generate import summary
    - Ensure data integrity through proper ordering
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the ImportOrchestrator.
        
        Args:
            db_session: Async database session for all operations
        """
        self.db = db_session
        self.parser: Optional[ExcelParser] = None
        self.mapper = DataMapper()
        self.hierarchy = HierarchyBuilder(db_session)
        self.writer = DatabaseWriter(db_session)
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    async def import_from_file(self, file_path: str) -> ImportResponse:
        """
        Execute the complete import process from an Excel file.
        
        This is the main entry point that orchestrates all import steps:
        1. Parse Excel file
        2. Process sheets in hierarchical order
        3. Commit transaction
        4. Generate summary
        
        Args:
            file_path: Path to the Excel file to import
        
        Returns:
            ImportResponse with success status, summary, warnings, and errors
        """
        start_time = time.time()
        
        try:
            # Validate file path
            if not file_path:
                error_msg = "File path cannot be empty"
                log_error(logger, error_msg)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=0.0
                )
            
            # Validate file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                error_msg = f"File not found: {file_path}"
                log_error(logger, error_msg)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            
            # Validate file is readable
            if not file_path_obj.is_file():
                error_msg = f"Path is not a file: {file_path}"
                log_error(logger, error_msg)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            
            file_size_bytes = file_path_obj.stat().st_size
            log_info(logger, 
                f"Starting import from file: {file_path}",
                file_path=file_path,
                file_size_kb=file_size_bytes / 1024,
                file_size_mb=file_size_bytes / (1024 * 1024)
            )
            
            # Initialize parser with error handling
            try:
                self.parser = ExcelParser(file_path)
                log_info(logger, "Excel parser initialized successfully")
            except FileNotFoundError as e:
                error_msg = f"File not found: {str(e)}"
                log_error(logger, error_msg, exc_info=True)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            except ValueError as e:
                error_msg = f"Invalid Excel file: {str(e)}"
                log_error(logger, error_msg, exc_info=True)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            except Exception as e:
                error_msg = f"Failed to load Excel file: {str(e)}"
                log_error(logger, error_msg, exc_info=True)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            
            # Log available sheets
            try:
                available_sheets = self.parser.get_available_sheets()
                log_info(logger, 
                    f"Excel file contains {len(available_sheets)} sheets",
                    sheet_count=len(available_sheets),
                    sheet_names=available_sheets
                )
                
                if not available_sheets:
                    error_msg = "Excel file contains no sheets"
                    log_error(logger, error_msg, file_path=file_path)
                    return ImportResponse(
                        success=False,
                        message=error_msg,
                        summary={},
                        warnings=[],
                        errors=[error_msg],
                        duration_seconds=time.time() - start_time
                    )
            except Exception as e:
                error_msg = f"Failed to read Excel sheets: {str(e)}"
                log_error(logger, error_msg, exc_info=True, file_path=file_path)
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary={},
                    warnings=[],
                    errors=[error_msg],
                    duration_seconds=time.time() - start_time
                )
            
            # Import in hierarchical order with error handling for each step
            # Order: clients → programs → projects → usecases → user_stories → tasks → subtasks
            
            try:
                # Projects (creates clients and programs automatically)
                projects_start = time.time()
                log_info(logger, "Starting projects import", entity_type="projects")
                await self._import_projects()
                projects_duration = time.time() - projects_start
                log_info(logger, 
                    f"Projects import completed: {self.writer.counts['projects']} records",
                    entity_type="projects",
                    records_imported=self.writer.counts['projects'],
                    duration_seconds=projects_duration
                )
            except Exception as e:
                error_msg = f"Error importing projects: {str(e)}"
                log_error(logger, error_msg, exc_info=True, entity_type="projects")
                self.errors.append(error_msg)
                # Continue with other imports even if projects fail
            
            try:
                # Usecases (requires projects)
                usecases_start = time.time()
                log_info(logger, "Starting usecases import", entity_type="usecases")
                await self._import_usecases()
                usecases_duration = time.time() - usecases_start
                log_info(logger, 
                    f"Usecases import completed: {self.writer.counts['usecases']} records",
                    entity_type="usecases",
                    records_imported=self.writer.counts['usecases'],
                    duration_seconds=usecases_duration
                )
            except Exception as e:
                error_msg = f"Error importing usecases: {str(e)}"
                log_error(logger, error_msg, exc_info=True, entity_type="usecases")
                self.errors.append(error_msg)
            
            try:
                # User Stories (requires usecases)
                user_stories_start = time.time()
                log_info(logger, "Starting user stories import", entity_type="user_stories")
                await self._import_user_stories()
                user_stories_duration = time.time() - user_stories_start
                log_info(logger, 
                    f"User stories import completed: {self.writer.counts['user_stories']} records",
                    entity_type="user_stories",
                    records_imported=self.writer.counts['user_stories'],
                    duration_seconds=user_stories_duration
                )
            except Exception as e:
                error_msg = f"Error importing user stories: {str(e)}"
                log_error(logger, error_msg, exc_info=True, entity_type="user_stories")
                self.errors.append(error_msg)
            
            try:
                # Tasks (requires user stories)
                tasks_start = time.time()
                log_info(logger, "Starting tasks import", entity_type="tasks")
                await self._import_tasks()
                tasks_duration = time.time() - tasks_start
                log_info(logger, 
                    f"Tasks import completed: {self.writer.counts['tasks']} records",
                    entity_type="tasks",
                    records_imported=self.writer.counts['tasks'],
                    duration_seconds=tasks_duration
                )
            except Exception as e:
                error_msg = f"Error importing tasks: {str(e)}"
                log_error(logger, error_msg, exc_info=True, entity_type="tasks")
                self.errors.append(error_msg)
            
            try:
                # Subtasks (requires tasks)
                subtasks_start = time.time()
                log_info(logger, "Starting subtasks import", entity_type="subtasks")
                await self._import_subtasks()
                subtasks_duration = time.time() - subtasks_start
                log_info(logger, 
                    f"Subtasks import completed: {self.writer.counts['subtasks']} records",
                    entity_type="subtasks",
                    records_imported=self.writer.counts['subtasks'],
                    duration_seconds=subtasks_duration
                )
            except Exception as e:
                error_msg = f"Error importing subtasks: {str(e)}"
                log_error(logger, error_msg, exc_info=True, entity_type="subtasks")
                self.errors.append(error_msg)
            
            # Log unmapped columns
            try:
                self.mapper.log_unmapped_columns()
                unmapped_report = self.mapper.get_unmapped_columns_report()
                for entity_type, columns in unmapped_report.items():
                    if columns:
                        self.warnings.append(
                            f"Unmapped columns in {entity_type}: {', '.join(columns)}"
                        )
            except Exception as e:
                log_warning(logger, f"Error generating unmapped columns report: {str(e)}")
            
            # Check if we have any critical errors that should prevent commit
            if self.errors:
                error_msg = f"Import completed with {len(self.errors)} errors. Rolling back transaction."
                log_error(logger, error_msg)
                try:
                    await self.writer.rollback_transaction()
                except Exception as rollback_error:
                    log_error(logger, f"Rollback failed: {str(rollback_error)}", exc_info=True)
                
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary=self.writer.get_summary(),
                    warnings=self.warnings,
                    errors=self.errors,
                    duration_seconds=time.time() - start_time
                )
            
            # Commit transaction
            try:
                log_info(logger, "Committing transaction...")
                await self.writer.commit_transaction()
                log_info(logger, "Transaction committed successfully")
            except Exception as e:
                error_msg = f"Failed to commit transaction: {str(e)}"
                log_error(logger, error_msg, exc_info=True)
                self.errors.append(error_msg)
                
                # Attempt rollback
                try:
                    await self.writer.rollback_transaction()
                    log_info(logger, "Transaction rolled back after commit failure")
                except Exception as rollback_error:
                    rollback_msg = f"Rollback also failed: {str(rollback_error)}"
                    log_error(logger, rollback_msg, exc_info=True)
                    self.errors.append(rollback_msg)
                
                return ImportResponse(
                    success=False,
                    message=error_msg,
                    summary=self.writer.get_summary(),
                    warnings=self.warnings,
                    errors=self.errors,
                    duration_seconds=time.time() - start_time
                )
            
            # Generate summary
            summary = self.writer.get_summary()
            duration = time.time() - start_time
            total_records = sum(summary.values())
            
            log_info(logger, 
                f"Import completed successfully in {duration:.2f} seconds",
                duration_seconds=duration,
                total_records=total_records,
                summary=summary,
                warnings_count=len(self.warnings),
                errors_count=len(self.errors),
                clients_created=self.writer.counts.get('clients', 0),
                programs_created=self.writer.counts.get('programs', 0),
                projects_imported=self.writer.counts.get('projects', 0),
                usecases_imported=self.writer.counts.get('usecases', 0),
                user_stories_imported=self.writer.counts.get('user_stories', 0),
                tasks_imported=self.writer.counts.get('tasks', 0),
                subtasks_imported=self.writer.counts.get('subtasks', 0)
            )
            
            success_message = f"Import completed successfully. Imported {total_records} total records."
            if self.warnings:
                success_message += f" ({len(self.warnings)} warnings)"
            
            return ImportResponse(
                success=True,
                message=success_message,
                summary=summary,
                warnings=self.warnings,
                errors=self.errors,
                duration_seconds=duration
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during import: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            self.errors.append(error_msg)
            
            # Attempt rollback
            try:
                log_info(logger, "Attempting transaction rollback due to unexpected error...")
                await self.writer.rollback_transaction()
                log_info(logger, "Transaction rolled back successfully")
            except Exception as rollback_error:
                rollback_msg = f"Rollback failed: {str(rollback_error)}"
                log_error(logger, rollback_msg, exc_info=True)
                self.errors.append(rollback_msg)
            
            return ImportResponse(
                success=False,
                message=error_msg,
                summary=self.writer.get_summary(),
                warnings=self.warnings,
                errors=self.errors,
                duration_seconds=time.time() - start_time
            )
        
        finally:
            # Clean up parser
            if self.parser:
                try:
                    self.parser.close()
                    log_info(logger, "Excel parser closed successfully")
                except Exception as e:
                    log_warning(logger, f"Error closing parser: {str(e)}")
    
    async def _import_projects(self) -> None:
        """
        Import projects from the Projects sheet.
        
        For each project:
        1. Get or create client
        2. Get or create program for client
        3. Map project data
        4. Insert project
        5. Store Excel ID to DB ID mapping
        """
        log_info(logger, "Importing projects...")
        
        if not self.parser:
            warning_msg = "Parser not initialized, skipping projects"
            log_warning(logger, warning_msg)
            self.warnings.append(warning_msg)
            return
        
        try:
            # Get sheet data
            sheet_data = self.parser.get_sheet_data('Projects')
            
            if not sheet_data:
                warning_msg = "Projects sheet not found or empty"
                log_warning(logger, warning_msg)
                self.warnings.append(warning_msg)
                return
            
            log_info(logger, 
                f"Found {len(sheet_data)} projects to import",
                entity_type="projects",
                row_count=len(sheet_data)
            )
            
            successful_imports = 0
            failed_imports = 0
            
            for idx, row in enumerate(sheet_data, start=1):
                try:
                    # Validate row
                    if not row:
                        log_warning(logger, f"Skipping empty row {idx}")
                        failed_imports += 1
                        continue
                    
                    # Map row data
                    try:
                        mapped_data = self.mapper.map_row('projects', row)
                    except Exception as map_error:
                        error_msg = f"Error mapping project row {idx}: {str(map_error)}"
                        log_error(logger, error_msg, exc_info=True)
                        self.errors.append(error_msg)
                        failed_imports += 1
                        continue
                    
                    # Extract client name (special field)
                    client_name = mapped_data.pop('_client_name', None) or "Default Client"
                    
                    # Get or create client
                    try:
                        client_id = await self.hierarchy.get_or_create_client(client_name)
                    except Exception as client_error:
                        error_msg = f"Error getting/creating client '{client_name}' for project row {idx}: {str(client_error)}"
                        log_error(logger, error_msg, exc_info=True)
                        self.errors.append(error_msg)
                        failed_imports += 1
                        continue
                    
                    # Get or create program for this client
                    try:
                        program_id = await self.hierarchy.get_or_create_program(client_id, client_name)
                    except Exception as program_error:
                        error_msg = f"Error getting/creating program for client '{client_name}' (project row {idx}): {str(program_error)}"
                        log_error(logger, error_msg, exc_info=True)
                        self.errors.append(error_msg)
                        failed_imports += 1
                        continue
                    
                    # Add program_id to project data
                    mapped_data['program_id'] = program_id
                    
                    # Set default values for required fields
                    if 'is_deleted' not in mapped_data:
                        mapped_data['is_deleted'] = False
                    
                    # Extract Excel ID for mapping
                    excel_id = mapped_data.pop('excel_id', None)
                    
                    # Insert project
                    try:
                        project_id = await self.writer.insert_entity('projects', mapped_data)
                    except Exception as insert_error:
                        error_msg = f"Error inserting project row {idx}: {str(insert_error)}"
                        log_error(logger, error_msg, exc_info=True)
                        self.errors.append(error_msg)
                        failed_imports += 1
                        continue
                    
                    # Store ID mapping if Excel ID exists
                    if excel_id:
                        try:
                            self.hierarchy.map_excel_id_to_db_id('projects', str(excel_id), project_id)
                        except Exception as mapping_error:
                            log_warning(logger, f"Error storing ID mapping for project row {idx}: {str(mapping_error)}")
                            # Not critical, continue
                    
                    successful_imports += 1
                    log_info(logger, f"Imported project {idx}/{len(sheet_data)}: {mapped_data.get('name', 'Unknown')}")
                    
                except Exception as e:
                    error_msg = f"Unexpected error importing project row {idx}: {str(e)}"
                    log_error(logger, error_msg, exc_info=True)
                    self.errors.append(error_msg)
                    failed_imports += 1
            
            log_info(logger, 
                f"Completed importing projects: {successful_imports} successful, {failed_imports} failed",
                entity_type="projects",
                successful_imports=successful_imports,
                failed_imports=failed_imports,
                total_in_database=self.writer.counts['projects']
            )
            
        except Exception as e:
            error_msg = f"Critical error in projects import: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            self.errors.append(error_msg)
            raise
    
    async def _import_usecases(self) -> None:
        """
        Import usecases from the Usecases sheet.
        
        For each usecase:
        1. Map usecase data
        2. Resolve parent project ID from Excel ID
        3. Insert usecase
        4. Store Excel ID to DB ID mapping
        """
        log_info(logger, "Importing usecases...")
        
        if not self.parser:
            self.warnings.append("Parser not initialized, skipping usecases")
            return
        
        # Get sheet data
        sheet_data = self.parser.get_sheet_data('Usecases')
        
        if not sheet_data:
            self.warnings.append("Usecases sheet not found or empty")
            return
        
        log_info(logger, f"Found {len(sheet_data)} usecases to import")
        
        for idx, row in enumerate(sheet_data, start=1):
            try:
                # Map row data
                mapped_data = self.mapper.map_row('usecases', row)
                
                # Extract and resolve parent project ID
                project_excel_id = mapped_data.pop('_project_excel_id', None)
                
                if not project_excel_id:
                    self.warnings.append(f"Usecase row {idx}: Missing project_id, skipping")
                    continue
                
                project_id = self.hierarchy.get_db_id_from_excel_id('projects', str(project_excel_id))
                
                if not project_id:
                    self.warnings.append(
                        f"Usecase row {idx}: Project ID '{project_excel_id}' not found, skipping"
                    )
                    continue
                
                # Add project_id to usecase data
                mapped_data['project_id'] = project_id
                
                # Set default values
                if 'is_deleted' not in mapped_data:
                    mapped_data['is_deleted'] = False
                
                # Extract Excel ID for mapping
                excel_id = mapped_data.pop('excel_id', None)
                
                # Insert usecase
                usecase_id = await self.writer.insert_entity('usecases', mapped_data)
                
                # Store ID mapping
                if excel_id:
                    self.hierarchy.map_excel_id_to_db_id('usecases', str(excel_id), usecase_id)
                
                log_info(logger, f"Imported usecase {idx}/{len(sheet_data)}: {mapped_data.get('name', 'Unknown')}")
                
            except Exception as e:
                error_msg = f"Error importing usecase row {idx}: {str(e)}"
                log_error(logger, error_msg)
                self.errors.append(error_msg)
        
        log_info(logger, f"Completed importing {self.writer.counts['usecases']} usecases")
    
    async def _import_user_stories(self) -> None:
        """
        Import user stories from the Userstories sheet.
        
        For each user story:
        1. Map user story data
        2. Resolve parent usecase ID from Excel ID
        3. Resolve user references (owner, created_by)
        4. Insert user story
        5. Store Excel ID to DB ID mapping
        """
        log_info(logger, "Importing user stories...")
        
        if not self.parser:
            self.warnings.append("Parser not initialized, skipping user stories")
            return
        
        # Try multiple possible sheet names
        sheet_names = ['Userstories', 'UserStories', 'User Stories', 'User_Stories']
        sheet_data = None
        
        for sheet_name in sheet_names:
            sheet_data = self.parser.get_sheet_data(sheet_name)
            if sheet_data:
                log_info(logger, f"Found user stories in sheet: {sheet_name}")
                break
        
        if not sheet_data:
            self.warnings.append(f"User stories sheet not found (tried: {', '.join(sheet_names)})")
            return
        
        log_info(logger, f"Found {len(sheet_data)} user stories to import")
        
        for idx, row in enumerate(sheet_data, start=1):
            try:
                # Map row data
                mapped_data = self.mapper.map_row('user_stories', row)
                
                # Extract and resolve parent usecase ID
                usecase_excel_id = mapped_data.pop('_usecase_excel_id', None)
                
                if not usecase_excel_id:
                    self.warnings.append(f"User story row {idx}: Missing usecase_id, skipping")
                    continue
                
                usecase_id = self.hierarchy.get_db_id_from_excel_id('usecases', str(usecase_excel_id))
                
                if not usecase_id:
                    self.warnings.append(
                        f"User story row {idx}: Usecase ID '{usecase_excel_id}' not found, skipping"
                    )
                    continue
                
                # Add usecase_id to user story data
                mapped_data['usecase_id'] = usecase_id
                
                # Resolve user references
                owner_name = mapped_data.pop('_owner', None)
                if owner_name:
                    owner_id = await self.hierarchy.resolve_user_reference(owner_name)
                    if owner_id:
                        mapped_data['owner_id'] = owner_id
                    else:
                        self.warnings.append(f"User story row {idx}: Owner '{owner_name}' not found")
                
                created_by_name = mapped_data.pop('_created_by', None)
                if created_by_name:
                    created_by_id = await self.hierarchy.resolve_user_reference(created_by_name)
                    if created_by_id:
                        mapped_data['created_by'] = created_by_id
                
                # Set default values
                if 'is_deleted' not in mapped_data:
                    mapped_data['is_deleted'] = False
                
                # Extract Excel ID for mapping
                excel_id = mapped_data.pop('excel_id', None)
                
                # Insert user story
                user_story_id = await self.writer.insert_entity('user_stories', mapped_data)
                
                # Store ID mapping
                if excel_id:
                    self.hierarchy.map_excel_id_to_db_id('user_stories', str(excel_id), user_story_id)
                
                log_info(logger, f"Imported user story {idx}/{len(sheet_data)}: {mapped_data.get('title', 'Unknown')}")
                
            except Exception as e:
                error_msg = f"Error importing user story row {idx}: {str(e)}"
                log_error(logger, error_msg)
                self.errors.append(error_msg)
        
        log_info(logger, f"Completed importing {self.writer.counts['user_stories']} user stories")
    
    async def _import_tasks(self) -> None:
        """
        Import tasks from the Tasks sheet.
        
        For each task:
        1. Map task data
        2. Resolve parent user story ID from Excel ID
        3. Resolve user references (assigned_to)
        4. Insert task
        5. Store Excel ID to DB ID mapping
        """
        log_info(logger, "Importing tasks...")
        
        if not self.parser:
            self.warnings.append("Parser not initialized, skipping tasks")
            return
        
        # Get sheet data
        sheet_data = self.parser.get_sheet_data('Tasks')
        
        if not sheet_data:
            self.warnings.append("Tasks sheet not found or empty")
            return
        
        log_info(logger, f"Found {len(sheet_data)} tasks to import")
        
        for idx, row in enumerate(sheet_data, start=1):
            try:
                # Map row data
                mapped_data = self.mapper.map_row('tasks', row)
                
                # Extract and resolve parent user story ID
                user_story_excel_id = mapped_data.pop('_user_story_excel_id', None)
                
                if not user_story_excel_id:
                    self.warnings.append(f"Task row {idx}: Missing user_story_id, skipping")
                    continue
                
                user_story_id = self.hierarchy.get_db_id_from_excel_id('user_stories', str(user_story_excel_id))
                
                if not user_story_id:
                    self.warnings.append(
                        f"Task row {idx}: User story ID '{user_story_excel_id}' not found, skipping"
                    )
                    continue
                
                # Add user_story_id to task data
                mapped_data['user_story_id'] = user_story_id
                
                # Note: phase_id is now nullable, so we don't need to create phases for Excel imports
                
                # Resolve user references
                assigned_to_name = mapped_data.pop('_assigned_to', None)
                if assigned_to_name:
                    assigned_to_id = await self.hierarchy.resolve_user_reference(assigned_to_name)
                    if assigned_to_id:
                        mapped_data['assigned_to'] = assigned_to_id
                    else:
                        self.warnings.append(f"Task row {idx}: User '{assigned_to_name}' not found")
                
                # Set default values
                if 'is_deleted' not in mapped_data:
                    mapped_data['is_deleted'] = False
                
                # Extract Excel ID for mapping
                excel_id = mapped_data.pop('excel_id', None)
                
                # Insert task
                task_id = await self.writer.insert_entity('tasks', mapped_data)
                
                # Store ID mapping
                if excel_id:
                    self.hierarchy.map_excel_id_to_db_id('tasks', str(excel_id), task_id)
                
                log_info(logger, f"Imported task {idx}/{len(sheet_data)}: {mapped_data.get('title', 'Unknown')}")
                
            except Exception as e:
                error_msg = f"Error importing task row {idx}: {str(e)}"
                log_error(logger, error_msg)
                self.errors.append(error_msg)
        
        log_info(logger, f"Completed importing {self.writer.counts['tasks']} tasks")
    
    async def _import_subtasks(self) -> None:
        """
        Import subtasks from the Subtasks sheet.
        
        For each subtask:
        1. Map subtask data
        2. Resolve parent task ID from Excel ID
        3. Resolve user references (assigned_to)
        4. Insert subtask
        5. Store Excel ID to DB ID mapping
        """
        log_info(logger, "Importing subtasks...")
        
        if not self.parser:
            self.warnings.append("Parser not initialized, skipping subtasks")
            return
        
        # Get sheet data
        sheet_data = self.parser.get_sheet_data('Subtasks')
        
        if not sheet_data:
            self.warnings.append("Subtasks sheet not found or empty")
            return
        
        log_info(logger, f"Found {len(sheet_data)} subtasks to import")
        
        for idx, row in enumerate(sheet_data, start=1):
            try:
                # Map row data
                mapped_data = self.mapper.map_row('subtasks', row)
                
                # Extract and resolve parent task ID
                task_excel_id = mapped_data.pop('_task_excel_id', None)
                
                if not task_excel_id:
                    self.warnings.append(f"Subtask row {idx}: Missing task_id, skipping")
                    continue
                
                task_id = self.hierarchy.get_db_id_from_excel_id('tasks', str(task_excel_id))
                
                if not task_id:
                    self.warnings.append(
                        f"Subtask row {idx}: Task ID '{task_excel_id}' not found, skipping"
                    )
                    continue
                
                # Add task_id to subtask data
                mapped_data['task_id'] = task_id
                
                # Get project_id from task to create/get default phase
                try:
                    from sqlalchemy import text
                    result = await self.db.execute(
                        text("""
                            SELECT p.id 
                            FROM tasks t
                            JOIN user_stories us ON t.user_story_id = us.id
                            JOIN usecases uc ON us.usecase_id = uc.id
                            JOIN projects p ON uc.project_id = p.id
                            WHERE t.id = :task_id
                        """),
                        {"task_id": task_id}
                    )
                    project_row = result.fetchone()
                    if project_row:
                        project_id = str(project_row[0])
                        # Get or create default phase for this project
                        phase_id = await self.hierarchy.get_or_create_default_phase(project_id)
                        if phase_id:
                            mapped_data['phase_id'] = phase_id
                except Exception as phase_error:
                    log_warning(logger, f"Could not get/create phase for subtask row {idx}: {str(phase_error)}")
                
                # Resolve user references
                assigned_to_name = mapped_data.pop('_assigned_to', None)
                if assigned_to_name:
                    assigned_to_id = await self.hierarchy.resolve_user_reference(assigned_to_name)
                    if assigned_to_id:
                        mapped_data['assigned_to'] = assigned_to_id
                    else:
                        self.warnings.append(f"Subtask row {idx}: User '{assigned_to_name}' not found")
                
                # Set default values
                if 'is_deleted' not in mapped_data:
                    mapped_data['is_deleted'] = False
                
                # Extract Excel ID for mapping
                excel_id = mapped_data.pop('excel_id', None)
                
                # Insert subtask
                subtask_id = await self.writer.insert_entity('subtasks', mapped_data)
                
                # Store ID mapping
                if excel_id:
                    self.hierarchy.map_excel_id_to_db_id('subtasks', str(excel_id), subtask_id)
                
                log_info(logger, f"Imported subtask {idx}/{len(sheet_data)}: {mapped_data.get('title', 'Unknown')}")
                
            except Exception as e:
                error_msg = f"Error importing subtask row {idx}: {str(e)}"
                log_error(logger, error_msg)
                self.errors.append(error_msg)
        
        log_info(logger, f"Completed importing {self.writer.counts['subtasks']} subtasks")
