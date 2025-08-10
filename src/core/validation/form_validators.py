"""
Form and Business Rule Validators

Validators for GUI form data and application-level business rules.
These validators primarily return user-friendly error messages suitable for GUI display.
"""

from typing import Tuple, Dict, Any
from .protocols import ValidatorBase
from .messages import ValidationMessages, MessageType


class FormDataValidator(ValidatorBase):
    """
    Validates GUI form data before processing.

    This validator handles all form-level validation for the main application GUI,
    ensuring user selections are valid before order processing begins.

    TODO: Implement validation for the following scenarios:

    1. Agency Selection Validation:
       - Check form_data["agency"] != "Select Agency"
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "required_selection",
         field="an agency (NMSLO or Federal)")
       - Current logic location: app.py lines 24-30

    2. Order Type Selection Validation:
       - Check form_data["order_type"] != "Select Order Type"
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "required_selection",
         field="an order type (Runsheet or Abstract)")
       - Current logic location: app.py lines 32-38

    3. Order Number Format Validation (Optional):
       - Check if order_number is provided and validate format
       - Should contain only alphanumeric characters, hyphens, and underscores
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "invalid_format",
         field="Order number", requirement="contain only letters, numbers, hyphens, and underscores")
       - Current logic location: app.py lines 47-56

    4. File Path Presence Validation:
       - Check form_data["file_path"] is not empty
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "missing_required",
         field="an Excel order form file")
       - Current logic location: app.py lines 58-67

    Expected form_data structure:
    {
        "agency": str,           # "NMSLO", "Federal", or "Select Agency"
        "order_type": str,       # "Runsheet", "Abstract", or "Select Order Type"
        "order_number": str,     # Optional, user-provided order number
        "file_path": str,        # Path to selected Excel file
        "order_date": date,      # Date object from date picker
    }
    """

    def validate(self, form_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate GUI form data comprehensively.

        Args:
            form_data: Dictionary containing form field values from MainWindow.get_form_data()

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, user_friendly_error) if invalid
        """
        # TODO: Implement comprehensive form validation
        # TODO: Replace the validation logic currently in app.py process_order() function
        # TODO: Use ValidationMessages.format_message() for consistent error messages
        # TODO: Return user-friendly messages suitable for GUI display

        # Placeholder implementation - always returns valid
        # Remove this when implementing actual validation
        return True, ""

    def validate_agency(self, agency_str: str) -> Tuple[bool, str]:
        """
        Validate agency string from GUI form.

        Args:
            agency_str: Agency string from GUI ("NMSLO", "Federal", etc.)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, user_friendly_error) if invalid
        """
        valid_agencies = ["NMSLO", "Federal"]

        if not agency_str or agency_str.strip() == "" or agency_str == "Select Agency":
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "required_selection",
                field="an agency (NMSLO or Federal)",
            )
            return False, error

        if agency_str not in valid_agencies:
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "invalid_input",
                field="Agency",
                requirement=f"must be one of: {', '.join(valid_agencies)}",
            )
            return False, error

        return True, ""

    def validate_order_type(self, order_type_str: str) -> Tuple[bool, str]:
        """
        Validate order type string from GUI form.

        Args:
            order_type_str: Order type string from GUI ("Runsheet", "Abstract", etc.)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, user_friendly_error) if invalid
        """
        valid_order_types = ["Runsheet", "Abstract"]

        if (
            not order_type_str
            or order_type_str.strip() == ""
            or order_type_str == "Select Order Type"
        ):
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "required_selection",
                field="an order type (Runsheet or Abstract)",
            )
            return False, error

        if order_type_str not in valid_order_types:
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "invalid_input",
                field="Order type",
                requirement=f"must be one of: {', '.join(valid_order_types)}",
            )
            return False, error

        return True, ""

    def validate_order_number(self, order_number_str: str) -> Tuple[bool, str]:
        """
        Validate order number format from GUI form.

        Args:
            order_number_str: Order number string from GUI (optional field)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, user_friendly_error) if invalid
        """
        # Order number is optional - empty or None is valid
        if not order_number_str or order_number_str.strip() == "":
            return True, ""

        # Check if order number contains only letters, numbers, hyphens, and underscores
        cleaned_number = order_number_str.replace("-", "").replace("_", "")
        if not cleaned_number.isalnum():
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "invalid_format",
                field="Order number",
                requirement="should contain only letters, numbers, hyphens, and underscores",
            )
            return False, error

        return True, ""


class BusinessRulesValidator(ValidatorBase):
    """
    Validates business logic and application rules.

    This validator handles application-level business rules that don't fit
    into other validator categories, such as feature availability checks.

    TODO: Implement validation for the following scenarios:

    1. Feature Availability Validation:
       - Check if Abstract workflow is implemented
       - Use ValidationMessages.format_message(MessageType.USER_FRIENDLY, "feature_unavailable",
         feature="Abstract workflow")
       - Current logic location: app.py lines 40-45

    2. Business Rule Enforcement:
       - Check order type compatibility with agency
       - Validate date ranges and business constraints
       - Use appropriate USER_FRIENDLY or TECHNICAL messages based on context

    3. Application State Validation:
       - Check if required services are available
       - Validate configuration and environment requirements
       - Use ValidationMessages.format_message() for consistent messaging

    Integration Notes:
    - Should be used by app.py for business rule validation
    - Should replace hardcoded business logic checks
    - Error messages should be user-friendly for GUI display
    - Can be extended for additional business rules as needed
    """

    def validate(self, data: Any) -> Tuple[bool, str]:
        """
        Validate business rules and application logic.

        Args:
            data: Data to validate against business rules (varies by use case)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, appropriate_error) if invalid
        """
        # TODO: Implement business rules validation
        # TODO: Replace hardcoded business logic from app.py
        # TODO: Check feature availability (Abstract workflow)
        # TODO: Use ValidationMessages.format_message() for consistent error messages
        # TODO: Use USER_FRIENDLY messages for GUI-facing validation

        # Placeholder implementation - always returns valid
        # Remove this when implementing actual validation
        return True, ""

    def validate_feature_availability(self, order_type_str: str) -> Tuple[bool, str]:
        """
        Validate that the selected order type has its workflow implemented.

        Args:
            order_type_str: Order type string from GUI ("Runsheet", "Abstract", etc.)

        Returns:
            Tuple[bool, str]: (True, "") if available, (False, user_friendly_error) if not implemented
        """
        if order_type_str == "Abstract":
            error = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "feature_unavailable",
                feature="Abstract workflow",
            )
            return False, error

        return True, ""

    def validate_order_type_support(self, order_type) -> Tuple[bool, str]:
        """
        Validate that order type is supported by the application.

        Args:
            order_type: ReportType enum value

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, technical_error) if invalid
        """
        from src.core.models import ReportType

        supported_types = [ReportType.RUNSHEET]
        unsupported_types = [
            ReportType.BASE_ABSTRACT,
            ReportType.SUPPLEMENTAL_ABSTRACT,
            ReportType.DOL_ABSTRACT,
        ]

        if order_type in unsupported_types:
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "constraint_violation",
                field="Order type",
                constraint_description=f"'{order_type.value}' is not yet supported",
            )
            return False, error

        if order_type not in supported_types:
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "constraint_violation",
                field="Order type",
                constraint_description=f"'{order_type}' is not a valid order type",
            )
            return False, error

        return True, ""
