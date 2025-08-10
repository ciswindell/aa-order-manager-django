"""
Application Error Handler

Centralized error handling using the existing validation message system.
Converts exceptions to user-friendly and technical messages following SOLID/DRY principles.
"""

from typing import Tuple, Dict, Type
from .messages import ValidationMessages, MessageType


class ApplicationErrorHandler:
    """
    Centralized error handler that leverages the existing validation message system.

    Converts exceptions into standardized user-friendly and technical messages
    using the ValidationMessages infrastructure. Follows the established
    validation system patterns for consistency.
    """

    # Exception mapping to message template keys
    ERROR_MAPPING: Dict[Type[Exception], Tuple[str, str]] = {
        # (user_friendly_template, technical_template)
        FileNotFoundError: ("file_not_found", "file_not_found_technical"),
        PermissionError: ("file_access_error", "file_access_denied"),
        ConnectionError: ("connection_error", "connection_error_technical"),
        ValueError: ("validation_failed", "processing_error_technical"),
    }

    def handle_exception(
        self, exception: Exception, context: str = ""
    ) -> Tuple[str, str]:
        """
        Convert exception to user-friendly and technical messages.

        Args:
            exception: The exception to handle
            context: Additional context about where the error occurred

        Returns:
            Tuple[str, str]: (user_message, technical_message)
        """
        exception_type = type(exception)
        error_message = str(exception)

        # Check for specific exception types first
        if exception_type in self.ERROR_MAPPING:
            user_template, tech_template = self.ERROR_MAPPING[exception_type]
            return self._format_known_error(
                user_template, tech_template, exception, context
            )

        # Check for content-based error categorization
        error_lower = error_message.lower()

        if "authentication" in error_lower or "auth" in error_lower:
            return self._format_authentication_error(exception, context)
        elif "column" in error_lower or "excel" in error_lower:
            return self._format_excel_error(exception, context)
        elif "workflow" in error_lower:
            return self._format_workflow_error(exception, context)
        else:
            return self._format_generic_error(exception, context)

    def _format_known_error(
        self, user_template: str, tech_template: str, exception: Exception, context: str
    ) -> Tuple[str, str]:
        """Format errors with known exception types."""
        error_details = str(exception)

        if isinstance(exception, FileNotFoundError):
            user_msg = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, user_template, file_type="Excel order form"
            )
            tech_msg = ValidationMessages.format_message(
                MessageType.TECHNICAL, tech_template, file_path=error_details
            )
        elif isinstance(exception, PermissionError):
            user_msg = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                user_template,
                reason="Please check file permissions and try again",
            )
            tech_msg = ValidationMessages.format_message(
                MessageType.TECHNICAL, tech_template, file_path=error_details
            )
        elif isinstance(exception, ConnectionError):
            user_msg = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, user_template
            )
            tech_msg = ValidationMessages.format_message(
                MessageType.TECHNICAL, tech_template, error_details=error_details
            )
        else:  # ValueError and others
            user_msg = ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, user_template, reason=error_details
            )
            tech_msg = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                tech_template,
                error_details=(
                    f"{context}: {error_details}" if context else error_details
                ),
            )

        return user_msg, tech_msg

    def _format_authentication_error(
        self, exception: Exception, context: str
    ) -> Tuple[str, str]:
        """Format authentication-related errors."""
        user_msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "authentication_error"
        )
        tech_msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "authentication_error_technical",
            error_details=f"{context}: {str(exception)}" if context else str(exception),
        )
        return user_msg, tech_msg

    def _format_excel_error(
        self, exception: Exception, context: str
    ) -> Tuple[str, str]:
        """Format Excel file format errors."""
        user_msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "excel_format_error", details=str(exception)
        )
        tech_msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "excel_format_error_technical",
            error_details=f"{context}: {str(exception)}" if context else str(exception),
        )
        return user_msg, tech_msg

    def _format_workflow_error(
        self, exception: Exception, context: str
    ) -> Tuple[str, str]:
        """Format workflow execution errors."""
        user_msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "workflow_error", details=str(exception)
        )
        tech_msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "workflow_error_technical",
            error_details=f"{context}: {str(exception)}" if context else str(exception),
        )
        return user_msg, tech_msg

    def _format_generic_error(
        self, exception: Exception, context: str
    ) -> Tuple[str, str]:
        """Format generic/unknown errors."""
        user_msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "processing_error", details=str(exception)
        )
        tech_msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "processing_error_technical",
            error_details=f"{context}: {str(exception)}" if context else str(exception),
        )
        return user_msg, tech_msg
