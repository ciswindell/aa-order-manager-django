"""
Configuration Models

Dataclasses and classes for agency-specific configuration.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .exceptions import ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AgencyStaticConfig:
    """
    Static configuration for agency-specific behavior.

    Contains type-safe static data like column widths, folder structures,
    and Dropbox agency names that don't change at runtime.
    """

    column_widths: Dict[str, int] = field(default_factory=dict)
    folder_structure: List[str] = field(default_factory=list)
    dropbox_agency_name: str = ""

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate_static_configuration()
        logger.debug(f"AgencyStaticConfig initialized for {self.dropbox_agency_name}")

    def validate_static_configuration(self) -> None:
        """
        Comprehensive validation of static configuration.

        Performs type checking, required field validation, and logical consistency checks.

        Raises:
            ConfigurationError: If any validation check fails
        """
        # Validate types
        self._validate_field_types()

        # Validate required fields
        self._validate_required_fields()

        # Validate field values and logical consistency
        self._validate_field_values()

        # Validate column widths specifically
        self._validate_column_widths()

        # Validate folder structure specifically
        self._validate_folder_structure()

    def _validate_field_types(self) -> None:
        """Validate that all fields have correct types."""
        if not isinstance(self.column_widths, dict):
            raise ConfigurationError(
                f"column_widths must be a dictionary, got {type(self.column_widths)}"
            )

        if not isinstance(self.folder_structure, list):
            raise ConfigurationError(
                f"folder_structure must be a list, got {type(self.folder_structure)}"
            )

        if not isinstance(self.dropbox_agency_name, str):
            raise ConfigurationError(
                f"dropbox_agency_name must be a string, got {type(self.dropbox_agency_name)}"
            )

    def _validate_required_fields(self) -> None:
        """Validate that all required fields are present and non-empty."""
        if not self.dropbox_agency_name or not self.dropbox_agency_name.strip():
            raise ConfigurationError(
                "dropbox_agency_name cannot be empty or whitespace"
            )

        if not self.folder_structure:
            raise ConfigurationError("folder_structure cannot be empty")

        if not self.column_widths:
            raise ConfigurationError("column_widths cannot be empty")

    def _validate_field_values(self) -> None:
        """Validate field values and logical consistency."""
        # Validate dropbox_agency_name format
        if len(self.dropbox_agency_name.strip()) < 2:
            raise ConfigurationError(
                f"dropbox_agency_name must be at least 2 characters, got '{self.dropbox_agency_name}'"
            )

        # Check for reasonable limits
        if len(self.folder_structure) > 20:
            raise ConfigurationError(
                f"folder_structure has too many folders ({len(self.folder_structure)}), maximum is 20"
            )

        if len(self.column_widths) > 50:
            raise ConfigurationError(
                f"column_widths has too many columns ({len(self.column_widths)}), maximum is 50"
            )

    def _validate_column_widths(self) -> None:
        """Validate column width specifications."""
        for column, width in self.column_widths.items():
            # Validate column name
            if not isinstance(column, str) or not column.strip():
                raise ConfigurationError(
                    f"Column name must be a non-empty string, got '{column}'"
                )

            # Validate width value
            if not isinstance(width, int):
                raise ConfigurationError(
                    f"Column width for '{column}' must be an integer, got {type(width)}"
                )

            if width <= 0:
                raise ConfigurationError(
                    f"Column width for '{column}' must be positive, got {width}"
                )

            if width > 200:
                raise ConfigurationError(
                    f"Column width for '{column}' is too large ({width}), maximum is 200"
                )

    def _validate_folder_structure(self) -> None:
        """Validate folder structure specifications."""
        for i, folder in enumerate(self.folder_structure):
            if not isinstance(folder, str):
                raise ConfigurationError(
                    f"Folder structure item {i} must be a string, got {type(folder)}"
                )

            if not folder.strip():
                raise ConfigurationError(
                    f"Folder structure item {i} cannot be empty or whitespace"
                )

            # Check for reasonable folder name length
            if len(folder.strip()) > 100:
                raise ConfigurationError(
                    f"Folder name '{folder}' is too long ({len(folder)} chars), maximum is 100"
                )

    def get_column_width(self, column_name: str, default: int = 12) -> int:
        """
        Get column width for a specific column.

        Args:
            column_name: Name of the column
            default: Default width if column not found

        Returns:
            Column width as integer
        """
        return self.column_widths.get(column_name, default)


class AgencyBehaviorConfig:
    """
    Behavioral configuration for agency-specific processing logic.

    Contains callable mappings for search functions and blank column definitions
    that define agency-specific behavior at runtime.
    """

    def __init__(self, search_mappings: Dict[str, Callable], blank_columns: List[str]):
        """
        Initialize behavioral configuration.

        Args:
            search_mappings: Dictionary mapping column names to callable search functions
            blank_columns: List of blank column names to be added to worksheets
        """
        self.search_mappings = search_mappings or {}
        self.blank_columns = blank_columns or []

        # Validate configuration
        self._validate_configuration()

        logger.debug(
            f"AgencyBehaviorConfig initialized with {len(self.search_mappings)} search mappings and {len(self.blank_columns)} blank columns"
        )

    def _validate_configuration(self) -> None:
        """Validate behavioral configuration."""
        self.validate_behavioral_configuration()

    def validate_behavioral_configuration(self) -> None:
        """
        Comprehensive validation of behavioral configuration.

        Performs callable validation, return type checking, and logical consistency checks.

        Raises:
            ConfigurationError: If any validation check fails
        """
        # Validate types and structure
        self._validate_behavioral_types()

        # Validate required fields
        self._validate_behavioral_required_fields()

        # Validate callable functions
        self._validate_search_mappings()

        # Validate blank columns
        self._validate_blank_columns()

        # Validate logical consistency
        self._validate_behavioral_consistency()

    def _validate_behavioral_types(self) -> None:
        """Validate that behavioral configuration fields have correct types."""
        if not isinstance(self.search_mappings, dict):
            raise ConfigurationError(
                f"search_mappings must be a dictionary, got {type(self.search_mappings)}"
            )

        if not isinstance(self.blank_columns, list):
            raise ConfigurationError(
                f"blank_columns must be a list, got {type(self.blank_columns)}"
            )

    def _validate_behavioral_required_fields(self) -> None:
        """Validate that required behavioral fields are present and non-empty."""
        if not self.search_mappings:
            raise ConfigurationError("search_mappings cannot be empty")

        if not self.blank_columns:
            raise ConfigurationError("blank_columns cannot be empty")

    def _validate_search_mappings(self) -> None:
        """Validate search mapping callable functions and their behavior."""
        for column_name, search_func in self.search_mappings.items():
            # Validate column name
            if not isinstance(column_name, str) or not column_name.strip():
                raise ConfigurationError(
                    f"Search mapping column name must be a non-empty string, got '{column_name}'"
                )

            # Validate function is callable
            if not callable(search_func):
                raise ConfigurationError(
                    f"Search mapping for '{column_name}' must be callable, got {type(search_func)}"
                )

            # Validate function behavior with test input
            self._validate_search_function_behavior(column_name, search_func)

    def _validate_search_function_behavior(self, column_name: str, search_func) -> None:
        """
        Validate that a search function behaves correctly with test input.

        Args:
            column_name: Name of the search column
            search_func: The callable function to test

        Raises:
            ConfigurationError: If the function doesn't behave as expected
        """
        test_inputs = ["TEST-123-A", "NMLC 456789", "Sample Lease"]

        for test_input in test_inputs:
            try:
                result = search_func(test_input)

                # Validate return type
                if not isinstance(result, str):
                    raise ConfigurationError(
                        f"Search function for '{column_name}' must return string, got {type(result)} for input '{test_input}'"
                    )

                # Validate return value is not None or empty for normal cases
                if result is None:
                    raise ConfigurationError(
                        f"Search function for '{column_name}' returned None for input '{test_input}'"
                    )

            except Exception as e:
                if isinstance(e, ConfigurationError):
                    raise  # Re-raise our own validation errors
                else:
                    raise ConfigurationError(
                        f"Search function for '{column_name}' failed with test input '{test_input}': {str(e)}"
                    )

    def _validate_blank_columns(self) -> None:
        """Validate blank column specifications."""
        for i, column in enumerate(self.blank_columns):
            if not isinstance(column, str):
                raise ConfigurationError(
                    f"Blank column item {i} must be a string, got {type(column)}"
                )

            if not column.strip():
                raise ConfigurationError(
                    f"Blank column item {i} cannot be empty or whitespace"
                )

            # Check for reasonable column name length
            if len(column.strip()) > 50:
                raise ConfigurationError(
                    f"Blank column name '{column}' is too long ({len(column)} chars), maximum is 50"
                )

    def _validate_behavioral_consistency(self) -> None:
        """Validate logical consistency of behavioral configuration."""
        # Check for reasonable limits
        if len(self.search_mappings) > 20:
            raise ConfigurationError(
                f"search_mappings has too many columns ({len(self.search_mappings)}), maximum is 20"
            )

        if len(self.blank_columns) > 30:
            raise ConfigurationError(
                f"blank_columns has too many columns ({len(self.blank_columns)}), maximum is 30"
            )

        # Check for duplicate column names between search and blank columns
        search_column_names = set(self.search_mappings.keys())
        blank_column_names = set(self.blank_columns)

        duplicates = search_column_names.intersection(blank_column_names)
        if duplicates:
            raise ConfigurationError(
                f"Column names cannot appear in both search_mappings and blank_columns: {duplicates}"
            )

    def get_search_columns(self) -> List[str]:
        """
        Get list of search column names.

        Returns:
            List of search column names from mappings
        """
        return list(self.search_mappings.keys())

    def get_blank_columns(self) -> List[str]:
        """
        Get list of blank column names.

        Returns:
            List of blank column names
        """
        return self.blank_columns.copy()

    def create_search_data(self, lease_data) -> Dict[str, Any]:
        """
        Create search data using configured search function mappings.

        Args:
            lease_data: pandas Series or DataFrame containing lease data

        Returns:
            Dictionary mapping column names to processed search data
        """
        search_data = {}

        for column_name, search_func in self.search_mappings.items():
            try:
                # Apply search function to lease data
                search_data[column_name] = lease_data.apply(search_func)
            except Exception as e:
                logger.error(
                    f"Error applying search function for '{column_name}': {str(e)}"
                )
                raise ConfigurationError(
                    f"Failed to apply search function for '{column_name}': {str(e)}"
                )

        return search_data

    def validate_with_sample_data(self, sample_lease: str) -> bool:
        """
        Validate search mappings with sample data to catch runtime issues.

        IMPORTANT: Use agency-specific lease number formats for realistic testing:
        - Federal lease format: "NMNM 12345A"
        - NMSLO lease format: "B-1234-5"

        Args:
            sample_lease: Agency-specific sample lease number for testing
                         Must match the actual lease number format for the agency

        Returns:
            True if all search functions work correctly

        Raises:
            ConfigurationError: If any search function fails
        """
        if not sample_lease or not isinstance(sample_lease, str):
            raise ConfigurationError("sample_lease must be a non-empty string")
        for column_name, search_func in self.search_mappings.items():
            try:
                result = search_func(sample_lease)
                if not isinstance(result, str):
                    raise ConfigurationError(
                        f"Search function for '{column_name}' must return string, got {type(result)}"
                    )
            except Exception as e:
                raise ConfigurationError(
                    f"Search function for '{column_name}' failed with sample data: {str(e)}"
                )

        logger.debug("All search mappings validated successfully with sample data")
        return True
