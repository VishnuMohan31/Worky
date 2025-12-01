"""
Data Mapper component for Excel to Database field mapping.

This module handles the transformation of Excel row data to database-compatible
field mappings, including type conversions, default value application, and
data normalization.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from decimal import Decimal, InvalidOperation

from logging_utils import get_logger, log_info, log_warning, log_error

logger = get_logger("data_mapper")


class DataMapper:
    """
    Maps Excel columns to database fields with intelligent type conversion
    and default value handling.
    """
    
    # Column mappings: Excel column name -> Database field name
    # Special prefix '_' indicates fields that need special handling (not direct DB fields)
    COLUMN_MAPPINGS = {
        'projects': {
            'project_id': 'excel_id',
            'project_name': 'name',
            'description': 'short_description',
            'descriptions': 'short_description',
            'long_description': 'long_description',
            'client_name': '_client_name',  # Special: used for client lookup
            'status': 'status',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'repository_url': 'repository_url',
            'sprint_length_weeks': 'sprint_length_weeks',
            'sprint_starting_day': 'sprint_starting_day',
        },
        'usecases': {
            'usecase_id': 'excel_id',
            'project_id': '_project_excel_id',  # Special: used for parent lookup
            'usecase_name': 'name',
            'name': 'name',
            'description': 'short_description',
            'long_description': 'long_description',
            'priority': 'priority',
            'status': 'status',
        },
        'user_stories': {
            'user_story_id': 'excel_id',
            'userstory_id': 'excel_id',
            'usecase_id': '_usecase_excel_id',  # Special: used for parent lookup
            'title': 'title',
            'name': 'title',
            'user_story_name': 'title',
            'description': 'short_description',
            'long_description': 'long_description',
            'acceptance_criteria': 'acceptance_criteria',
            'story_points': 'story_points',
            'priority': 'priority',
            'status': 'status',
            'owner': '_owner',  # Special: used for user lookup
            'created_by': '_created_by',  # Special: used for user lookup
        },
        'tasks': {
            'task_id': 'excel_id',
            'user_story_id': '_user_story_excel_id',  # Special: used for parent lookup
            'userstory_id': '_user_story_excel_id',
            'title': 'title',
            'name': 'title',
            'task_name': 'title',
            'description': 'short_description',
            'long_description': 'long_description',
            'status': 'status',
            'priority': 'priority',
            'assigned_to': '_assigned_to',  # Special: used for user lookup
            'owner': '_assigned_to',
            'estimated_hours': 'estimated_hours',
            'actual_hours': 'actual_hours',
            'start_date': 'start_date',
            'due_date': 'due_date',
        },
        'subtasks': {
            'subtask_id': 'excel_id',
            'task_id': '_task_excel_id',  # Special: used for parent lookup
            'title': 'title',
            'name': 'title',
            'subtask_name': 'title',
            'description': 'short_description',
            'long_description': 'long_description',
            'status': 'status',
            'assigned_to': '_assigned_to',  # Special: used for user lookup
            'owner': '_assigned_to',
            'estimated_hours': 'estimated_hours',
            'actual_hours': 'actual_hours',
            'duration_days': 'duration_days',
            'scrum_points': 'scrum_points',
        },
    }
    
    # Default values for missing required fields
    DEFAULT_VALUES = {
        'projects': {
            'status': 'Planning',
            'short_description': '',
            'long_description': '',
        },
        'usecases': {
            'status': 'Draft',
            'priority': 'Medium',
            'short_description': '',
            'long_description': '',
        },
        'user_stories': {
            'title': 'Untitled User Story',
            'status': 'Backlog',
            'priority': 'Medium',
            'short_description': '',
            'long_description': '',
            'acceptance_criteria': '',
        },
        'tasks': {
            'status': 'To Do',
            'priority': 'Medium',
            'short_description': '',
            'long_description': '',
        },
        'subtasks': {
            'status': 'To Do',
            'short_description': '',
            'long_description': '',
        },
    }
    
    def __init__(self):
        """Initialize the DataMapper."""
        self.unmapped_columns: Dict[str, Set[str]] = {}
    
    def map_row(self, entity_type: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an Excel row to database field mapping.
        
        Args:
            entity_type: Type of entity (projects, usecases, user_stories, tasks, subtasks)
            row: Dictionary of Excel column names to values
        
        Returns:
            Dictionary of database field names to converted values
            
        Raises:
            ValueError: If entity_type is unknown or row is invalid
        """
        if not entity_type:
            raise ValueError("Entity type cannot be empty")
            
        if entity_type not in self.COLUMN_MAPPINGS:
            raise ValueError(f"Unknown entity type: {entity_type}. Valid types: {', '.join(self.COLUMN_MAPPINGS.keys())}")
        
        if not row:
            log_warning(logger, f"Empty row provided for entity type: {entity_type}")
            return {}
        
        try:
            column_mapping = self.COLUMN_MAPPINGS[entity_type]
            default_values = self.DEFAULT_VALUES.get(entity_type, {})
            mapped_data = {}
            unmapped = set()
            
            # Normalize Excel column names (lowercase, strip whitespace)
            normalized_row = {}
            for k, v in row.items():
                if k is not None:
                    try:
                        normalized_key = str(k).lower().strip()
                        normalized_row[normalized_key] = v
                    except Exception as e:
                        log_warning(logger, f"Failed to normalize column key '{k}': {str(e)}")
                        continue
            
            # Map columns
            for excel_col, db_field in column_mapping.items():
                excel_col_lower = excel_col.lower()
                
                if excel_col_lower in normalized_row:
                    value = normalized_row[excel_col_lower]
                    
                    try:
                        # Convert and normalize the value
                        converted_value = self._convert_value(db_field, value)
                        
                        # Trim whitespace for text fields
                        if isinstance(converted_value, str):
                            converted_value = converted_value.strip()
                        
                        mapped_data[db_field] = converted_value
                        
                    except Exception as e:
                        log_error(logger, f"Error converting value for field '{db_field}' (Excel column '{excel_col}'): {str(e)}")
                        # Set to None on conversion error
                        mapped_data[db_field] = None
                        
                elif not db_field.startswith('_'):  # Skip special fields for default values
                    # Apply default value if available
                    if db_field in default_values:
                        mapped_data[db_field] = default_values[db_field]
            
            # Track unmapped columns
            mapped_excel_cols = {col.lower() for col in column_mapping.keys()}
            for excel_col in normalized_row.keys():
                if excel_col not in mapped_excel_cols and not excel_col.startswith('_'):
                    unmapped.add(excel_col)
            
            if unmapped:
                if entity_type not in self.unmapped_columns:
                    self.unmapped_columns[entity_type] = set()
                self.unmapped_columns[entity_type].update(unmapped)
            
            return mapped_data
            
        except Exception as e:
            log_error(logger, f"Error mapping row for entity type '{entity_type}': {str(e)}", exc_info=True)
            raise
    
    def _convert_value(self, field_name: str, value: Any) -> Any:
        """
        Convert value based on field type inference.
        
        Args:
            field_name: Name of the database field
            value: Raw value from Excel
        
        Returns:
            Converted value
        """
        # Handle None/empty values
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return None
        
        # Date fields
        if 'date' in field_name.lower():
            return self.convert_date(value)
        
        # Numeric fields
        if field_name in ['estimated_hours', 'actual_hours', 'scrum_points']:
            return self.convert_number(value)
        
        if field_name in ['story_points', 'duration_days']:
            converted = self.convert_number(value)
            return int(converted) if converted is not None else None
        
        # Percentage fields (if any)
        if 'percentage' in field_name.lower() or 'percent' in field_name.lower():
            return self.convert_percentage(value)
        
        # Default: return as string
        return str(value) if value is not None else None
    
    def convert_date(self, value: Any) -> Optional[date]:
        """
        Convert various date formats to date object.
        
        Handles:
        - datetime objects
        - date objects
        - ISO format strings (YYYY-MM-DD)
        - Common date formats (MM/DD/YYYY, DD/MM/YYYY, etc.)
        - Excel serial dates (numeric)
        
        Args:
            value: Date value in various formats
        
        Returns:
            date object or None if conversion fails
        """
        if value is None:
            return None
        
        try:
            # datetime object (check before date since datetime is subclass of date)
            if isinstance(value, datetime):
                return value.date()
            
            # Already a date object
            if isinstance(value, date):
                return value
            
            # Excel serial date (numeric)
            if isinstance(value, (int, float)):
                try:
                    # Validate reasonable date range
                    if value < 0 or value > 100000:  # Roughly year 1900-2173
                        log_warning(logger, f"Excel serial date out of reasonable range: {value}")
                        return None
                    
                    # Excel epoch starts at 1900-01-01 (with a bug for 1900 leap year)
                    # Days since 1899-12-30
                    excel_epoch = datetime(1899, 12, 30)
                    return (excel_epoch + timedelta(days=int(value))).date()
                except (ValueError, OverflowError) as e:
                    log_warning(logger, f"Failed to convert Excel serial date {value}: {e}")
                    return None
            
            # String formats
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                
                # Try common date formats
                date_formats = [
                    '%Y-%m-%d',           # ISO format
                    '%m/%d/%Y',           # US format
                    '%d/%m/%Y',           # European format
                    '%Y/%m/%d',           # Alternative ISO
                    '%d-%m-%Y',           # European with dashes
                    '%m-%d-%Y',           # US with dashes
                    '%B %d, %Y',          # January 15, 2024
                    '%b %d, %Y',          # Jan 15, 2024
                    '%d %B %Y',           # 15 January 2024
                    '%d %b %Y',           # 15 Jan 2024
                ]
                
                for fmt in date_formats:
                    try:
                        return datetime.strptime(value, fmt).date()
                    except ValueError:
                        continue
                
                log_warning(logger, f"Failed to parse date string: '{value}'")
                return None
            
            log_warning(logger, f"Unsupported date type: {type(value).__name__} for value: {value}")
            return None
            
        except Exception as e:
            log_error(logger, f"Unexpected error converting date value '{value}': {str(e)}", exc_info=True)
            return None
    
    def convert_number(self, value: Any) -> Optional[float]:
        """
        Convert text or other formats to numeric type.
        
        Handles:
        - Numeric types (int, float, Decimal)
        - String representations of numbers
        - Numbers with commas (1,234.56)
        - Numbers with currency symbols ($1,234.56)
        
        Args:
            value: Value to convert to number
        
        Returns:
            float or None if conversion fails
        """
        if value is None:
            return None
        
        try:
            # Already numeric
            if isinstance(value, (int, float)):
                # Check for NaN or infinity
                if isinstance(value, float):
                    if value != value:  # NaN check
                        log_warning(logger, "Encountered NaN value")
                        return None
                    if value == float('inf') or value == float('-inf'):
                        log_warning(logger, f"Encountered infinity value: {value}")
                        return None
                return float(value)
            
            if isinstance(value, Decimal):
                return float(value)
            
            # String conversion
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                
                # Remove common non-numeric characters
                cleaned = value.replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()
                
                try:
                    return float(cleaned)
                except ValueError:
                    log_warning(logger, f"Failed to convert string to number: {value}")
                    return None
            
            log_warning(logger, f"Unsupported number type: {type(value).__name__} for value: {value}")
            return None
            
        except Exception as e:
            log_error(logger, f"Unexpected error converting number value '{value}': {str(e)}", exc_info=True)
            return None
    
    def convert_percentage(self, value: Any) -> Optional[float]:
        """
        Convert percentage to decimal format.
        
        Handles:
        - Percentage strings ("75%", "75.5%")
        - Decimal values (0.75)
        - Integer values (75) - assumes percentage
        
        Args:
            value: Percentage value
        
        Returns:
            Decimal representation (0.75 for 75%) or None if conversion fails
        """
        if value is None:
            return None
        
        try:
            # String with % symbol
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return None
                
                if '%' in value:
                    # Remove % and convert
                    cleaned = value.replace('%', '').strip()
                    try:
                        number = float(cleaned)
                        return number / 100.0  # Convert to decimal
                    except ValueError:
                        log_warning(logger, f"Failed to convert percentage string: {value}")
                        return None
                else:
                    # Try to convert as regular number
                    try:
                        return float(value) / 100.0
                    except ValueError:
                        log_warning(logger, f"Failed to convert percentage string: {value}")
                        return None
            
            # Already a decimal (0.0 to 1.0)
            if isinstance(value, float) and 0.0 <= value <= 1.0:
                return value
            
            # Integer or float > 1 (assume percentage)
            if isinstance(value, (int, float)):
                if value > 1.0:
                    return value / 100.0
                else:
                    return value
            
            log_warning(logger, f"Unsupported percentage type: {type(value).__name__} for value: {value}")
            return None
            
        except Exception as e:
            log_error(logger, f"Unexpected error converting percentage value '{value}': {str(e)}", exc_info=True)
            return None
    
    def get_unmapped_columns_report(self) -> Dict[str, List[str]]:
        """
        Get a report of all unmapped columns by entity type.
        
        Returns:
            Dictionary of entity type to list of unmapped column names
        """
        return {
            entity_type: sorted(list(columns))
            for entity_type, columns in self.unmapped_columns.items()
        }
    
    def log_unmapped_columns(self) -> None:
        """Log all unmapped columns as warnings."""
        report = self.get_unmapped_columns_report()
        
        for entity_type, columns in report.items():
            if columns:
                log_warning(logger, 
                    f"Unmapped columns in {entity_type} sheet: {', '.join(columns)}",
                    entity_type=entity_type,
                    unmapped_columns=columns,
                    unmapped_count=len(columns)
                )
