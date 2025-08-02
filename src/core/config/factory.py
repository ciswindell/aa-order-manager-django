"""
Configuration Factory

Factory methods and helper utilities for accessing agency configurations.
"""

import logging
from typing import Any, Dict, List

from .exceptions import InvalidAgencyError
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
        InvalidAgencyError: If agency_type is not supported
    """
    if not isinstance(agency_type, str):
        raise InvalidAgencyError(
            agency_name=str(agency_type), supported_agencies=list(AGENCY_CONFIGS.keys())
        )

    agency_type = agency_type.strip()
    if not agency_type:
        raise InvalidAgencyError(
            agency_name="<empty>", supported_agencies=list(AGENCY_CONFIGS.keys())
        )

    if agency_type not in AGENCY_CONFIGS:
        supported_agencies = list(AGENCY_CONFIGS.keys())
        raise InvalidAgencyError(
            agency_name=agency_type, supported_agencies=supported_agencies
        )

    logger.debug(f"Retrieved complete configuration for agency: {agency_type}")
    return AGENCY_CONFIGS[agency_type].copy()


def get_static_config(agency_type: str) -> AgencyStaticConfig:
    """
    Get static configuration for a specific agency type.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        AgencyStaticConfig instance for the specified agency

    Raises:
        InvalidAgencyError: If agency_type is not supported
    """
    config = get_agency_config(agency_type)
    logger.debug(f"Retrieved static configuration for agency: {agency_type}")
    return config["static"]


def get_behavioral_config(agency_type: str) -> AgencyBehaviorConfig:
    """
    Get behavioral configuration for a specific agency type.

    Args:
        agency_type: Name of the agency ("NMSLO" or "Federal")

    Returns:
        AgencyBehaviorConfig instance for the specified agency

    Raises:
        InvalidAgencyError: If agency_type is not supported
    """
    config = get_agency_config(agency_type)
    logger.debug(f"Retrieved behavioral configuration for agency: {agency_type}")
    return config["behavioral"]


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
        return False

    return agency_type.strip() in AGENCY_CONFIGS


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
    """
    config = get_agency_config(agency_type)
    static_config = config["static"]
    behavioral_config = config["behavioral"]

    # Base metadata columns (always present)
    metadata_columns = ["Agency", "Order Type", "Order Number", "Order Date"]

    # Data columns from source (always present)
    data_columns = ["Lease", "Requested Legal", "Report Start Date"]

    # Add Notes column for Federal only
    if agency_type == "Federal":
        data_columns.append("Notes")

    # Search columns (agency-specific)
    search_columns = behavioral_config.get_search_columns()

    # Blank columns (agency-specific)
    blank_columns = behavioral_config.get_blank_columns()

    # Combine all columns in order: metadata + data + search + blank
    all_columns = metadata_columns + data_columns + search_columns + blank_columns

    logger.debug(
        f"Retrieved {len(all_columns)} total columns for agency: {agency_type}"
    )
    return all_columns
