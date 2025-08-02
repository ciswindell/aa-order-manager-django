"""
Configuration Package

Hybrid configuration system for agency-specific order processing.

Public API:
- Configuration Models: AgencyStaticConfig, AgencyBehaviorConfig
- Factory Methods: get_agency_config, get_static_config, get_behavioral_config
- Helper Methods: get_all_columns, validate_agency_type, get_supported_agencies
- Exceptions: ConfigurationError, InvalidAgencyError
"""

# Import exceptions
from .exceptions import (
    ConfigurationError,
    ConfigurationValidationError,
    InvalidAgencyError,
)

# Import factory methods and helpers
from .factory import (
    get_agency_config,
    get_all_columns,
    get_behavioral_config,
    get_static_config,
    get_supported_agencies,
    validate_agency_type,
)

# Import configuration models
from .models import AgencyBehaviorConfig, AgencyStaticConfig

# Import registry (for advanced use cases)
from .registry import AGENCY_CONFIGS

# Public API exports
__all__ = [
    # Configuration Models
    "AgencyStaticConfig",
    "AgencyBehaviorConfig",
    # Factory Methods
    "get_agency_config",
    "get_static_config",
    "get_behavioral_config",
    # Helper Methods
    "get_all_columns",
    "validate_agency_type",
    "get_supported_agencies",
    # Exceptions
    "ConfigurationError",
    "InvalidAgencyError",
    "ConfigurationValidationError",
    # Registry (advanced)
    "AGENCY_CONFIGS",
]
