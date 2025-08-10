"""
File and Data Structure Validators

Validators for file operations and data structure validation.
These validators handle Excel files and DataFrame structure validation.
"""

from typing import Tuple
import pandas as pd
from .protocols import ValidatorBase
from .messages import ValidationMessages, MessageType


class ExcelFileValidator(ValidatorBase):
    """
    Validates Excel files for order processing.

    This validator handles file-level validation including existence, accessibility,
    file type verification, and basic file integrity checks.

    TODO: Implement validation for the following scenarios:

    1. File Existence Check:
       - Verify file exists using os.path.exists()
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "file_not_found",
         file_type="Excel")
       - Current logic location: app.py lines 69-75

    2. File Type Validation:
       - Check file extension is .xlsx or .xls (case insensitive)
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "invalid_file_type",
         file_requirement="an Excel file (.xlsx or .xls)")
       - Current logic location: app.py lines 77-82

    3. File Accessibility Check:
       - Test if file can be opened for reading
       - Handle PermissionError, OSError, IOError exceptions
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "file_access_error",
         reason="permission denied" or specific error)
       - Current logic location: app.py lines 84-95

    4. Optional: File Content Validation
       - Verify it's actually an Excel file (not just renamed)
       - Check if pandas can read it without errors
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "invalid_file_type",
         file_requirement="a valid Excel file")

    Integration Notes:
    - Should be used by app.py to replace lines 58-95 of file validation
    - Should be usable by OrderFormParser for file validation before parsing
    - Error messages should be suitable for GUI display via messagebox
    """

    def validate(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate Excel file for order processing.

        Args:
            file_path: Path to Excel file to validate

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, user_friendly_error) if invalid
        """
        import os

        # 1. Check file existence
        if not file_path or not file_path.strip():
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, "required_selection", field="a file"
            )
            return False, error

        if not os.path.exists(file_path):
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, "file_not_found", file_type="Excel"
            )
            return False, error

        # 2. Check file type (Excel extensions)
        file_lower = file_path.lower()
        if not (file_lower.endswith(".xlsx") or file_lower.endswith(".xls")):
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "invalid_file_type",
                file_requirement="an Excel file (.xlsx or .xls)",
            )
            return False, error

        # 3. Check file accessibility
        try:
            with open(file_path, "rb") as f:
                # Try to read a small chunk to verify accessibility
                f.read(1024)
        except PermissionError:
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "file_access_error",
                reason="permission denied",
            )
            return False, error
        except (OSError, IOError) as e:
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, "file_access_error", reason=str(e)
            )
            return False, error

        # 4. Optional: Verify it's actually an Excel file pandas can read
        try:
            import pandas as pd

            # Just check that pandas can open it, don't read all data
            pd.ExcelFile(file_path).close()
        except Exception:
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "invalid_file_type",
                file_requirement="a valid Excel file",
            )
            return False, error

        return True, ""


class OrderFormStructureValidator(ValidatorBase):
    """
    Validates Excel DataFrame structure for order form parsing.

    This validator ensures the Excel file contains the required columns and
    basic data structure needed for order processing.

    TODO: Implement validation for the following scenarios:

    1. Required Column Validation:
       - Check DataFrame contains "Lease" column
       - Check DataFrame contains "Requested Legal" column
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "constraint_violation",
         field="Order form", constraint_description="must contain 'Lease' column")
       - Current logic location: order_form_parser.py lines 32-37

    2. Optional: Data Type Validation:
       - Verify columns contain expected data types
       - Check for completely empty columns
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "invalid_value",
         field="Column data", constraint_description="contains invalid data types")

    3. Optional: Data Quality Checks:
       - Check for minimum number of rows
       - Validate lease number formats
       - Check legal description formats
       - Use appropriate TECHNICAL messages for specific issues

    Integration Notes:
    - Should be used by OrderFormParser._validate_columns() method
    - Should replace current column validation in order_form_parser.py
    - Error messages should be technical since this is business logic validation
    - Should work with pandas DataFrame objects
    """

    def validate(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate Excel DataFrame structure for order processing.

        Args:
            data: pandas DataFrame loaded from Excel file

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, technical_error) if invalid
        """
        import pandas as pd

        # Validate input is a DataFrame
        if not isinstance(data, pd.DataFrame):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="data",
                expected_type="pandas DataFrame",
            )
            return False, error

        # Check for required "Lease" column
        if "Lease" not in data.columns:
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "constraint_violation",
                field="Order form",
                constraint_description="must contain 'Lease' column",
            )
            return False, error

        # Check for required "Requested Legal" column
        if "Requested Legal" not in data.columns:
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "constraint_violation",
                field="Order form",
                constraint_description="must contain 'Requested Legal' column",
            )
            return False, error

        return True, ""
