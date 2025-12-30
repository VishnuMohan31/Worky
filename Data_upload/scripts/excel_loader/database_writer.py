"""
Database Writer Component for Excel Data Loader

This module provides the DatabaseWriter class that handles writing mapped data
to the database with transaction management, batch inserts, and error handling.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from datetime import datetime

from logging_utils import get_logger, log_info, log_warning, log_error

logger = get_logger("database_writer")


class DatabaseWriter:
    """
    Handles database write operations with transaction management.
    
    Responsibilities:
    - Execute inserts in correct hierarchical order
    - Use batch inserts for performance
    - Manage database transactions
    - Handle constraint violations
    - Rollback on errors
    - Track inserted record counts
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize DatabaseWriter with a database session.
        
        Args:
            db_session: AsyncSession instance for database operations
        """
        self.db = db_session
        self.counts = {
            'clients': 0,
            'programs': 0,
            'projects': 0,
            'usecases': 0,
            'user_stories': 0,
            'tasks': 0,
            'subtasks': 0
        }
        log_info(logger, "DatabaseWriter initialized")
    
    async def insert_entity(self, entity_type: str, data: Dict[str, Any]) -> str:
        """
        Insert a single entity and return its ID.
        
        Args:
            entity_type: Type of entity (e.g., 'projects', 'tasks')
            data: Dictionary containing entity data
            
        Returns:
            str: The ID of the inserted entity
            
        Raises:
            IntegrityError: If constraint violations occur
            SQLAlchemyError: For other database errors
            ValueError: If entity_type or data is invalid
        """
        if not entity_type:
            raise ValueError("Entity type cannot be empty")
        
        if not data:
            raise ValueError(f"Cannot insert empty data for entity type: {entity_type}")
        
        try:
            # Map entity type to table name
            table_name = self._get_table_name(entity_type)
            
            if not table_name:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            # Create a copy to avoid modifying original
            insert_data = data.copy()
            
            # Add timestamps if not present
            if 'created_at' not in insert_data:
                insert_data['created_at'] = datetime.utcnow()
            if 'updated_at' not in insert_data:
                insert_data['updated_at'] = datetime.utcnow()
            
            # Validate we have data to insert
            if not insert_data:
                raise ValueError(f"No valid data to insert for {entity_type}")
            
            # Build column names and values
            columns = ', '.join(insert_data.keys())
            placeholders = ', '.join([f':{key}' for key in insert_data.keys()])
            
            # Insert query with RETURNING clause to get the generated ID
            query = text(f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                RETURNING id
            """)
            
            result = await self.db.execute(query, insert_data)
            row = result.fetchone()
            
            if row is None:
                raise SQLAlchemyError(f"Failed to insert {entity_type}: no ID returned")
            
            entity_id = row[0]
            
            # Increment count
            if entity_type in self.counts:
                self.counts[entity_type] += 1
            
            log_info(logger, 
                f"Inserted {entity_type} with ID: {entity_id}",
                entity_type=entity_type,
                entity_id=entity_id,
                table_name=table_name
            )
            return entity_id
            
        except IntegrityError as e:
            error_msg = f"Integrity constraint violation inserting {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise IntegrityError(error_msg, params=None, orig=e.orig) from e
            
        except SQLAlchemyError as e:
            error_msg = f"Database error inserting {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise SQLAlchemyError(error_msg) from e
            
        except ValueError as e:
            log_error(logger, f"Validation error inserting {entity_type}: {str(e)}", exc_info=True)
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error inserting {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e

    async def batch_insert_entities(
        self, 
        entity_type: str, 
        data_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Insert multiple entities efficiently using batch insert.
        
        Args:
            entity_type: Type of entity (e.g., 'projects', 'tasks')
            data_list: List of dictionaries containing entity data
            
        Returns:
            List[str]: List of IDs of inserted entities
            
        Raises:
            IntegrityError: If constraint violations occur
            SQLAlchemyError: For other database errors
            ValueError: If entity_type or data_list is invalid
        """
        if not entity_type:
            raise ValueError("Entity type cannot be empty")
        
        if not data_list:
            log_warning(logger, f"Empty data list provided for {entity_type}")
            return []
        
        try:
            table_name = self._get_table_name(entity_type)
            
            if not table_name:
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            inserted_ids = []
            failed_records = []
            
            # Process in batches of 100 for better performance
            batch_size = 100
            total_batches = (len(data_list) + batch_size - 1) // batch_size
            
            for batch_num, i in enumerate(range(0, len(data_list), batch_size), start=1):
                batch = data_list[i:i + batch_size]
                
                log_info(logger, 
                    f"Processing batch {batch_num}/{total_batches} for {entity_type}",
                    entity_type=entity_type,
                    batch_number=batch_num,
                    total_batches=total_batches,
                    batch_size=len(batch)
                )
                
                # Add timestamps to each record if not present
                for idx, data in enumerate(batch):
                    try:
                        if not data:
                            log_warning(logger, f"Skipping empty data record in batch {batch_num}, index {idx}")
                            failed_records.append(idx)
                            continue
                        
                        if 'created_at' not in data:
                            data['created_at'] = datetime.utcnow()
                        if 'updated_at' not in data:
                            data['updated_at'] = datetime.utcnow()
                    except Exception as e:
                        log_error(logger, f"Error preparing record {idx} in batch {batch_num}: {str(e)}")
                        failed_records.append(idx)
                        continue
                
                # Get column names from first valid record
                valid_batch = [d for d in batch if d]
                if not valid_batch:
                    log_warning(logger, f"No valid records in batch {batch_num}")
                    continue
                
                columns = ', '.join(valid_batch[0].keys())
                placeholders = ', '.join([f':{key}' for key in valid_batch[0].keys()])
                
                # Build VALUES clause for batch insert
                query = text(f"""
                    INSERT INTO {table_name} ({columns})
                    VALUES ({placeholders})
                    RETURNING id
                """)
                
                # Execute batch insert
                for record_idx, data in enumerate(valid_batch):
                    try:
                        result = await self.db.execute(query, data)
                        row = result.fetchone()
                        if row:
                            inserted_ids.append(row[0])
                            if entity_type in self.counts:
                                self.counts[entity_type] += 1
                        else:
                            log_warning(logger, f"No ID returned for record {record_idx} in batch {batch_num}")
                            failed_records.append(record_idx)
                    except Exception as record_error:
                        log_error(logger, f"Failed to insert record {record_idx} in batch {batch_num}: {str(record_error)}")
                        failed_records.append(record_idx)
                        # Continue with other records
                        continue
                
                log_info(logger, 
                    f"Batch {batch_num} completed: {len(valid_batch)} records processed",
                    entity_type=entity_type,
                    batch_number=batch_num,
                    records_processed=len(valid_batch)
                )
            
            if failed_records:
                log_warning(logger, 
                    f"Failed to insert {len(failed_records)} records for {entity_type}",
                    entity_type=entity_type,
                    failed_count=len(failed_records)
                )
            
            log_info(logger, 
                f"Total inserted {len(inserted_ids)} {entity_type} records",
                entity_type=entity_type,
                total_inserted=len(inserted_ids),
                total_failed=len(failed_records)
            )
            return inserted_ids
            
        except IntegrityError as e:
            error_msg = f"Integrity constraint violation in batch insert for {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise IntegrityError(error_msg, params=None, orig=e.orig) from e
            
        except SQLAlchemyError as e:
            error_msg = f"Database error in batch insert for {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise SQLAlchemyError(error_msg) from e
            
        except ValueError as e:
            log_error(logger, f"Validation error in batch insert for {entity_type}: {str(e)}", exc_info=True)
            raise
            
        except Exception as e:
            error_msg = f"Unexpected error in batch insert for {entity_type}: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    async def commit_transaction(self) -> None:
        """
        Commit all changes in the current transaction.
        
        Raises:
            SQLAlchemyError: If commit fails
        """
        try:
            log_info(logger, 
                "Committing transaction",
                total_records=sum(self.counts.values()),
                summary=self.counts
            )
            await self.db.commit()
            log_info(logger, 
                "Transaction committed successfully",
                total_records=sum(self.counts.values())
            )
        except SQLAlchemyError as e:
            error_msg = f"Failed to commit transaction: {str(e)}"
            log_error(logger, error_msg, exc_info=True, records_affected=sum(self.counts.values()))
            # Attempt rollback after failed commit
            try:
                await self.db.rollback()
                log_info(logger, "Rolled back after failed commit")
            except Exception as rollback_error:
                log_error(logger, f"Rollback after failed commit also failed: {str(rollback_error)}")
            raise SQLAlchemyError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error committing transaction: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    async def rollback_transaction(self) -> None:
        """
        Rollback all changes in the current transaction.
        
        This is called when errors occur to ensure database consistency.
        
        Raises:
            SQLAlchemyError: If rollback fails
        """
        try:
            log_warning(logger, 
                "Rolling back transaction",
                records_affected=sum(self.counts.values()),
                summary=self.counts
            )
            await self.db.rollback()
            log_warning(logger, "Transaction rolled back successfully")
        except SQLAlchemyError as e:
            error_msg = f"Failed to rollback transaction: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise SQLAlchemyError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error rolling back transaction: {str(e)}"
            log_error(logger, error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def get_summary(self) -> Dict[str, int]:
        """
        Return count of inserted records by entity type.
        
        Returns:
            Dict[str, int]: Dictionary mapping entity type to count
        """
        return self.counts.copy()
    
    def _get_table_name(self, entity_type: str) -> str:
        """
        Map entity type to database table name.
        
        Args:
            entity_type: Entity type (e.g., 'projects', 'user_stories')
            
        Returns:
            str: Database table name
        """
        # Direct mapping for most cases
        table_mapping = {
            'clients': 'clients',
            'programs': 'programs',
            'projects': 'projects',
            'usecases': 'usecases',
            'user_stories': 'user_stories',
            'tasks': 'tasks',
            'subtasks': 'subtasks'
        }
        
        return table_mapping.get(entity_type, entity_type)
    
    def reset_counts(self) -> None:
        """
        Reset all insertion counts to zero.
        
        Useful for starting a new import operation.
        """
        for key in self.counts:
            self.counts[key] = 0
        log_info(logger, "Insertion counts reset")
