"""
Configuration Exception Classes

Custom exception classes for configuration-related errors.
Provides clear, actionable error messages for configuration validation failures.
"""


class ConfigurationError(Exception):
    """
    Base exception for configuration-related errors.

    Raised when configuration validation fails, including type errors,
    missing required fields, invalid values, or logical inconsistencies.

    Attributes:
        message: Human-readable error description
        config_type: Type of configuration that failed (e.g., 'static', 'behavioral')
        agency_name: Name of the agency whose configuration failed (optional)
    """

    def __init__(self, message: str, config_type: str = None, agency_name: str = None):
        """
        Initialize configuration error.

        Args:
            message: Descriptive error message
            config_type: Type of configuration ('static', 'behavioral', 'integration')
            agency_name: Agency name if error is agency-specific
        """
        self.message = message
        self.config_type = config_type
        self.agency_name = agency_name

        # Build full error message with context
        full_message = message
        if agency_name and config_type:
            full_message = f"[{agency_name} {config_type}] {message}"
        elif agency_name:
            full_message = f"[{agency_name}] {message}"
        elif config_type:
            full_message = f"[{config_type}] {message}"

        super().__init__(full_message)


class InvalidAgencyError(ConfigurationError):
    """
    Raised when an invalid or unsupported agency type is requested.

    This typically occurs when trying to access configuration for an agency
    that doesn't exist in the AGENCY_CONFIGS registry.

    Attributes:
        agency_name: The invalid agency name that was requested
        supported_agencies: List of valid agency names
    """

    def __init__(self, agency_name: str, supported_agencies: list = None):
        """
        Initialize invalid agency error.

        Args:
            agency_name: The invalid agency name
            supported_agencies: List of supported agency names
        """
        self.agency_name = agency_name
        self.supported_agencies = supported_agencies or []

        if supported_agencies:
            message = f"Unsupported agency type '{agency_name}'. Supported agencies: {supported_agencies}"
        else:
            message = f"Unsupported agency type '{agency_name}'"

        super().__init__(message, config_type="registry", agency_name=agency_name)


class ConfigurationValidationError(ConfigurationError):
    """
    Raised when configuration validation fails during startup.

    This is a more specific error for validation failures that occur
    during the comprehensive startup validation process.
    """

    def __init__(
        self, message: str, agency_name: str = None, validation_stage: str = None
    ):
        """
        Initialize validation error.

        Args:
            message: Descriptive error message
            agency_name: Agency whose validation failed
            validation_stage: Stage of validation that failed
        """
        self.validation_stage = validation_stage

        config_type = (
            f"validation:{validation_stage}" if validation_stage else "validation"
        )
        super().__init__(message, config_type=config_type, agency_name=agency_name)
