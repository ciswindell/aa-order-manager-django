"""
Custom exceptions for runsheet services.

These exceptions provide clear error semantics and indicate whether errors
are transient (retryable) or permanent (non-retryable).
"""


class RunsheetServiceError(Exception):
    """Base exception for all runsheet service errors."""

    def __init__(self, message: str, is_retryable: bool = False):
        """
        Initialize RunsheetServiceError.

        Args:
            message: Human-readable error description
            is_retryable: Whether this error is transient and can be retried
        """
        super().__init__(message)
        self.message = message
        self.is_retryable = is_retryable


class BasePathMissingError(RunsheetServiceError):
    """
    Exception raised when the configured base path doesn't exist in cloud storage.

    This is a non-retryable error that requires administrative action to fix
    (either create the base path or update the configuration).
    """

    def __init__(self, base_path: str):
        """
        Initialize BasePathMissingError.

        Args:
            base_path: The missing base path that was expected to exist
        """
        message = (
            f"Base path '{base_path}' does not exist in cloud storage. "
            "Please create the base path or update the agency storage configuration."
        )
        super().__init__(message, is_retryable=False)
        self.base_path = base_path


class DirectoryCreationError(RunsheetServiceError):
    """
    Exception raised when directory creation fails in cloud storage.

    This is typically a transient error (network issues, API limits) and
    can be retried.
    """

    def __init__(self, directory_path: str, reason: str):
        """
        Initialize DirectoryCreationError.

        Args:
            directory_path: The directory path that failed to create
            reason: The underlying reason for the failure
        """
        message = f"Failed to create directory '{directory_path}': {reason}"
        super().__init__(message, is_retryable=True)
        self.directory_path = directory_path
        self.reason = reason
