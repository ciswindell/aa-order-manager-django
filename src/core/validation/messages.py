"""
Validation Message System

Provides standardized validation message templates with two-tier system:
- USER_FRIENDLY: Clear, actionable messages for GUI display
- TECHNICAL: Precise, structured messages for business logic and debugging
"""

from enum import Enum
from typing import Dict, Any


class MessageType(Enum):
    """Enumeration for validation message categories."""

    USER_FRIENDLY = "user_friendly"
    TECHNICAL = "technical"


class ValidationMessages:
    """
    Centralized validation message templates with parameter substitution.

    Provides consistent message formatting across all validators using
    template-based approach with parameter substitution.

    Example usage:
        # User-friendly message for GUI
        msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "required_selection",
            field="an agency (NMSLO or Federal)"
        )
        # Result: "Please select an agency (NMSLO or Federal)"

        # Technical message for business logic
        msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "wrong_type",
            field="order_number",
            expected_type="string"
        )
        # Result: "order_number must be string"
    """

    # Message templates organized by type
    TEMPLATES = {
        MessageType.USER_FRIENDLY: {
            # Form validation messages
            "required_selection": "Please select {field}",
            "invalid_format": "{field} should {requirement}",
            "invalid_input": "{field} format is invalid: {requirement}",
            # File validation messages
            "file_not_found": "File not found: Please select an existing {file_type} file",
            "file_access_error": "Cannot access file: {reason}",
            "invalid_file_type": "Please select {file_requirement}",
            # Business rule messages
            "feature_unavailable": "{feature} is not yet implemented",
            "operation_not_allowed": "{operation} is not allowed: {reason}",
            # General validation messages
            "validation_failed": "Validation failed: {reason}",
            "missing_required": "Please provide {field}",
            # Application error messages
            "authentication_error": "Failed to authenticate with Dropbox. Please check your access token in the .env file",
            "connection_error": "Unable to connect to Dropbox. Please check your internet connection and authentication",
            "excel_format_error": "Problem with Excel file format: {details}. Please ensure your order form has the required columns",
            "workflow_error": "Error during processing: {details}. Some items may not have been processed completely",
            "processing_error": "An unexpected error occurred: {details}. Please contact support if the problem persists",
        },
        MessageType.TECHNICAL: {
            # Type validation messages
            "wrong_type": "{field} must be {expected_type}",
            "type_mismatch": "{field} must be {expected_type}, got {actual_type}",
            # Value validation messages
            "empty_value": "{field} cannot be empty when provided",
            "invalid_value": "{field} {constraint_description}",
            "out_of_range": "{field} must be between {min_value} and {max_value}",
            # Enum validation messages
            "invalid_enum": "{field} must be one of {valid_options}",
            "unknown_option": "Unknown {field}: {value}",
            # Collection validation messages
            "invalid_collection": "{field} must be a {collection_type}",
            "collection_item_invalid": "{field}[{index}] must be {expected_type}",
            # Business object validation messages
            "constraint_violation": "{field} {constraint_description}",
            "date_range_invalid": "{field} {requirement}",
            "validation_context": "Validation failed in {validator_class}.{method_name}",
            # File validation messages
            "file_not_found_technical": "File not found: {file_path}",
            "file_access_denied": "Permission denied: {file_path}",
            "invalid_file_format": "Invalid file format: expected {expected_format}",
            # Application error messages (technical)
            "authentication_error_technical": "Authentication failed: {error_details}",
            "connection_error_technical": "Connection error: {error_details}",
            "excel_format_error_technical": "Excel parsing failed: {error_details}",
            "workflow_error_technical": "Workflow execution failed: {error_details}",
            "processing_error_technical": "Processing failed: {error_details}",
        },
    }

    @classmethod
    def format_message(
        cls, message_type: MessageType, template_key: str, **kwargs: Any
    ) -> str:
        """
        Format a validation message using standardized templates.

        Args:
            message_type: MessageType enum (USER_FRIENDLY or TECHNICAL)
            template_key: Key for the specific message template
            **kwargs: Parameters for template substitution

        Returns:
            str: Formatted message with parameters substituted

        Raises:
            KeyError: If message_type or template_key is not found

        Example:
            msg = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "required_selection",
                field="an agency"
            )
            # Returns: "Please select an agency"
        """
        if message_type not in cls.TEMPLATES:
            raise KeyError(f"Unknown message type: {message_type}")

        templates = cls.TEMPLATES[message_type]
        if template_key not in templates:
            available_keys = list(templates.keys())
            raise KeyError(
                f"Unknown template key '{template_key}' for {message_type.value}. "
                f"Available keys: {available_keys}"
            )

        template = templates[template_key]

        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise KeyError(
                f"Missing parameter {e} for template '{template_key}'. "
                f"Template: '{template}'"
            ) from e

    @classmethod
    def get_available_templates(cls, message_type: MessageType) -> Dict[str, str]:
        """
        Get all available templates for a specific message type.

        Args:
            message_type: MessageType enum to get templates for

        Returns:
            Dict[str, str]: Dictionary of template_key -> template_string

        Raises:
            KeyError: If message_type is not found
        """
        if message_type not in cls.TEMPLATES:
            raise KeyError(f"Unknown message type: {message_type}")

        return cls.TEMPLATES[message_type].copy()

    @classmethod
    def get_all_template_keys(cls) -> Dict[MessageType, list[str]]:
        """
        Get all available template keys organized by message type.

        Returns:
            Dict[MessageType, list[str]]: All template keys by message type
        """
        return {
            message_type: list(templates.keys())
            for message_type, templates in cls.TEMPLATES.items()
        }
