"""
Configuration Factory

Factory methods and helper utilities for accessing agency configurations.
"""

import logging
from typing import Any, Dict, List

from .exceptions import InvalidAgencyError, ConfigurationError
from .models import AgencyBehaviorConfig, AgencyStaticConfig
from .registry import AGENCY_CONFIGS

# Configure logging
logger = logging.getLogger(__name__)


def get_agency_config(agency_type: str) -> Dict[str, Any]:
    """
    Get complete configuration for a specific agency type.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        Dictionary containing both 'static' and 'behavioral' configurations

    Raises:
        InvalidAgencyError: If agency_type is not supported or invalid
        ConfigurationError: If configuration structure is invalid
    """
    # Validate input type
    if not isinstance(agency_type, str):
        error_msg = f"Expected string for agency_type, got {type(agency_type).__name__}: {agency_type}"
        logger.error(error_msg)
        raise InvalidAgencyError(
            agency_name=str(agency_type), 
            supported_agencies=list(AGENCY_CONFIGS.keys())
        )

    # Validate non-empty string
    agency_type = agency_type.strip()
    if not agency_type:
        error_msg = "Agency type cannot be empty or whitespace-only"
        logger.error(error_msg)
        raise InvalidAgencyError(
            agency_name="<empty>", 
            supported_agencies=list(AGENCY_CONFIGS.keys())
        )

    # Validate agency exists
    if agency_type not in AGENCY_CONFIGS:
        supported_agencies = list(AGENCY_CONFIGS.keys())
        error_msg = f"Agency '{agency_type}' not found. Available agencies: {supported_agencies}"
        logger.error(error_msg)
        raise InvalidAgencyError(
            agency_name=agency_type, 
            supported_agencies=supported_agencies
        )

    # Validate configuration structure
    config = AGENCY_CONFIGS[agency_type]
    _validate_configuration_structure(agency_type, config)

    logger.debug(f"Retrieved complete configuration for agency: {agency_type}")
    return config.copy()


def _validate_configuration_structure(agency_type: str, config: Dict[str, Any]) -> None:
    """
    Validate the structure of an agency configuration.
    
    Args:
        agency_type: Name of the agency being validated
        config: Configuration dictionary to validate
        
    Raises:
        ConfigurationError: If configuration structure is invalid
    """
    if not isinstance(config, dict):
        error_msg = f"Configuration for agency '{agency_type}' must be a dictionary, got {type(config).__name__}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="structure", agency_name=agency_type)
    
    # Check for required sections
    required_sections = ["static", "behavioral"]
    missing_sections = [section for section in required_sections if section not in config]
    
    if missing_sections:
        error_msg = f"Configuration for agency '{agency_type}' missing required sections: {missing_sections}. Found sections: {list(config.keys())}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="structure", agency_name=agency_type)
    
    # Validate static configuration type
    static_config = config.get("static")
    if not isinstance(static_config, AgencyStaticConfig):
        error_msg = f"Static configuration for agency '{agency_type}' must be AgencyStaticConfig instance, got {type(static_config).__name__}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    # Validate behavioral configuration type
    behavioral_config = config.get("behavioral")
    if not isinstance(behavioral_config, AgencyBehaviorConfig):
        error_msg = f"Behavioral configuration for agency '{agency_type}' must be AgencyBehaviorConfig instance, got {type(behavioral_config).__name__}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    logger.debug(f"Configuration structure validated for agency: {agency_type}")


def get_static_config(agency_type: str) -> AgencyStaticConfig:
    """
    Get static configuration for a specific agency type.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        AgencyStaticConfig instance for the specified agency

    Raises:
        InvalidAgencyError: If agency_type is not supported
        ConfigurationError: If static configuration is missing or invalid
    """
    try:
        config = get_agency_config(agency_type)
        static_config = config.get("static")
        
        if static_config is None:
            error_msg = f"Static configuration missing for agency '{agency_type}'. Check AGENCY_CONFIGS registry."
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
        
        # Validate static configuration content
        _validate_static_configuration(agency_type, static_config)
            
        logger.debug(f"Retrieved static configuration for agency: {agency_type}")
        return static_config
        
    except InvalidAgencyError:
        # Re-raise agency errors as-is
        raise
    except Exception as e:
        error_msg = f"Failed to retrieve static configuration for agency '{agency_type}': {str(e)}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)


def _validate_static_configuration(agency_type: str, static_config: AgencyStaticConfig) -> None:
    """
    Validate the content of a static configuration.
    
    Args:
        agency_type: Name of the agency being validated
        static_config: Static configuration to validate
        
    Raises:
        ConfigurationError: If static configuration is invalid
    """
    # Validate column widths
    if not static_config.column_widths:
        error_msg = f"Static configuration for agency '{agency_type}' has empty column_widths"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    # Validate folder structure
    if not static_config.folder_structure:
        error_msg = f"Static configuration for agency '{agency_type}' has empty folder_structure"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    # Validate dropbox agency name
    if not static_config.dropbox_agency_name:
        error_msg = f"Static configuration for agency '{agency_type}' has empty dropbox_agency_name"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    # Validate column widths are positive integers
    for column, width in static_config.column_widths.items():
        if not isinstance(width, int) or width <= 0:
            error_msg = f"Column width for '{column}' in agency '{agency_type}' must be positive integer, got {width} ({type(width).__name__})"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    # Validate folder structure contains strings
    for i, folder in enumerate(static_config.folder_structure):
        if not isinstance(folder, str):
            error_msg = f"Folder structure item {i} in agency '{agency_type}' must be string, got {type(folder).__name__}: {folder}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
    
    logger.debug(f"Static configuration content validated for agency: {agency_type}")


def get_behavioral_config(agency_type: str) -> AgencyBehaviorConfig:
    """
    Get behavioral configuration for a specific agency type.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        AgencyBehaviorConfig instance for the specified agency

    Raises:
        InvalidAgencyError: If agency_type is not supported
        ConfigurationError: If behavioral configuration is missing or invalid
    """
    try:
        config = get_agency_config(agency_type)
        behavioral_config = config.get("behavioral")
        
        if behavioral_config is None:
            error_msg = f"Behavioral configuration missing for agency '{agency_type}'. Check AGENCY_CONFIGS registry."
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
        
        # Validate behavioral configuration content
        _validate_behavioral_configuration(agency_type, behavioral_config)
            
        logger.debug(f"Retrieved behavioral configuration for agency: {agency_type}")
        return behavioral_config
        
    except InvalidAgencyError:
        # Re-raise agency errors as-is
        raise
    except Exception as e:
        error_msg = f"Failed to retrieve behavioral configuration for agency '{agency_type}': {str(e)}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)


def _validate_behavioral_configuration(agency_type: str, behavioral_config: AgencyBehaviorConfig) -> None:
    """
    Validate the content of a behavioral configuration.
    
    Args:
        agency_type: Name of the agency being validated
        behavioral_config: Behavioral configuration to validate
        
    Raises:
        ConfigurationError: If behavioral configuration is invalid
    """
    # Validate search mappings
    if not behavioral_config.search_mappings:
        error_msg = f"Behavioral configuration for agency '{agency_type}' has empty search_mappings"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    # Validate blank columns
    if not behavioral_config.blank_columns:
        error_msg = f"Behavioral configuration for agency '{agency_type}' has empty blank_columns"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    # Validate search mappings contain callable functions
    for search_name, search_func in behavioral_config.search_mappings.items():
        if not callable(search_func):
            error_msg = f"Search mapping '{search_name}' in agency '{agency_type}' must be callable, got {type(search_func).__name__}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    # Validate blank columns contain strings
    for i, column in enumerate(behavioral_config.blank_columns):
        if not isinstance(column, str):
            error_msg = f"Blank column {i} in agency '{agency_type}' must be string, got {type(column).__name__}: {column}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    # Validate search column names are strings
    for search_name in behavioral_config.search_mappings.keys():
        if not isinstance(search_name, str):
            error_msg = f"Search mapping key in agency '{agency_type}' must be string, got {type(search_name).__name__}: {search_name}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)
    
    logger.debug(f"Behavioral configuration content validated for agency: {agency_type}")


def get_supported_agencies() -> List[str]:
    """
    Get list of all supported agency types.

    Returns:
        List of supported agency type names
    """
    return list(AGENCY_CONFIGS.keys())


def validate_agency_type(agency_type: str) -> bool:
    """
    Validate if an agency type is supported.

    Args:
        agency_type: Name of the agency to validate

    Returns:
        True if agency type is supported, False otherwise
    """
    if not isinstance(agency_type, str):
        logger.debug(f"Agency type validation failed: expected string, got {type(agency_type).__name__}")
        return False

    if not agency_type.strip():
        logger.debug("Agency type validation failed: empty or whitespace-only string")
        return False

    is_valid = agency_type.strip() in AGENCY_CONFIGS
    if not is_valid:
        logger.debug(f"Agency type validation failed: '{agency_type}' not in supported agencies {list(AGENCY_CONFIGS.keys())}")
    
    return is_valid


def get_all_columns(agency_type: str) -> List[str]:
    """
    Get all columns that will be added to worksheet for a specific agency.

    Combines metadata columns, search columns, and blank columns in the order
    they will appear in the final worksheet.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        List of all column names in worksheet order

    Raises:
        InvalidAgencyError: If agency_type is not supported
        ConfigurationError: If configuration is missing or invalid
    """
    try:
        config = get_agency_config(agency_type)
        static_config = config.get("static")
        behavioral_config = config.get("behavioral")
        
        if static_config is None:
            error_msg = f"Static configuration missing for agency '{agency_type}' when building column list"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="static", agency_name=agency_type)
            
        if behavioral_config is None:
            error_msg = f"Behavioral configuration missing for agency '{agency_type}' when building column list"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)

        # Base metadata columns (always present)
        metadata_columns = ["Agency", "Order Type", "Order Number", "Order Date"]

        # Data columns from source (always present)
        data_columns = ["Lease", "Requested Legal", "Report Start Date"]

        # Add Notes column for Federal only
        if agency_type == "Federal":
            data_columns.append("Notes")

        # Search columns (agency-specific)
        try:
            search_columns = behavioral_config.get_search_columns()
        except Exception as e:
            error_msg = f"Failed to get search columns for agency '{agency_type}': {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)

        # Blank columns (agency-specific)
        try:
            blank_columns = behavioral_config.get_blank_columns()
        except Exception as e:
            error_msg = f"Failed to get blank columns for agency '{agency_type}': {str(e)}"
            logger.error(error_msg)
            raise ConfigurationError(error_msg, config_type="behavioral", agency_name=agency_type)

        # Combine all columns in order: metadata + data + search + blank
        all_columns = metadata_columns + data_columns + search_columns + blank_columns

        logger.debug(
            f"Retrieved {len(all_columns)} total columns for agency: {agency_type}"
        )
        return all_columns
        
    except (InvalidAgencyError, ConfigurationError):
        # Re-raise configuration errors as-is
        raise
    except Exception as e:
        error_msg = f"Unexpected error building column list for agency '{agency_type}': {str(e)}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg, config_type="integration", agency_name=agency_type)
