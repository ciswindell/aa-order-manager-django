"""
File Utilities Module

Contains utility classes for file handling operations including filename generation
and sanitization that are shared across different order processors.
"""

import re
from typing import Optional


class FilenameGenerator:
    """Utility class for generating and sanitizing filenames."""

    @classmethod
    def generate_order_filename(
        cls,
        order_number: Optional[str] = None,
        agency: Optional[str] = None,
        order_type: Optional[str] = None,
    ) -> str:
        """
        Generate descriptive filename for order Excel files.

        This method extracts the filename generation logic from the OrderProcessor
        base class. It creates a standardized filename format and sanitizes it
        for cross-platform compatibility.

        The format is: Order_{OrderNumber}_{Agency}_{OrderType}.xlsx

        Args:
            order_number: Order number value (defaults to "Unknown" if empty)
            agency: Agency name value (defaults to "Unknown" if empty)
            order_type: Order type value (defaults to "Unknown" if empty)

        Returns:
            str: Sanitized filename with .xlsx extension

        Raises:
            ValueError: If invalid character encoding is encountered
        """
        try:
            # Get order number, defaulting to "Unknown" if empty - extracted from existing code
            order_num = order_number.strip() if order_number else "Unknown"

            # Get agency, defaulting to "Unknown" if empty - extracted from existing code
            agency_clean = agency if agency else "Unknown"

            # Get order type, defaulting to "Unknown" if empty - extracted from existing code
            order_type_clean = order_type if order_type else "Unknown"

            # Create filename: Order_{OrderNumber}_{Agency}_{OrderType} - extracted from existing code
            filename = f"Order_{order_num}_{agency_clean}_{order_type_clean}.xlsx"

            # Clean filename of any invalid characters - extracted from existing code
            filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

            return filename

        except UnicodeError as e:
            raise ValueError(
                f"Invalid character encoding in filename parameters: {str(e)}"
            ) from e
        except Exception as e:
            raise ValueError(f"Error generating filename: {str(e)}") from e
