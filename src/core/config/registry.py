"""
Configuration Registry

Central registry containing all agency-specific configurations
and validation logic.
"""

import logging

from src.core.utils.parsing_utils import LeaseNumberParser

from .exceptions import ConfigurationError
from .models import AgencyBehaviorConfig, AgencyStaticConfig

# Configure logging
logger = logging.getLogger(__name__)


# Agency Configuration Registry
# Contains all agency-specific static and behavioral configurations
AGENCY_CONFIGS = {
    "NMSLO": {
        "static": AgencyStaticConfig(
            column_widths={
                "Agency": 15,
                "Order Type": 15,
                "Order Number": 15,
                "Order Date": 15,
                "Lease": 15,
                "Requested Legal": 25,
                "Report Start Date": 20,
                "Full Search": 14,
                "Partial Search": 14,
                "New Format": 12,
                "Tractstar": 12,
                "Old Format": 12,
                "MI Index": 12,
                "Documents": 12,
                "Search Notes": 30,
                "Link": 30,
            },
            folder_structure=["^Document Archive", "^MI Index", "Runsheets"],
            dropbox_agency_name="NMSLO",
        ),
        "behavioral": AgencyBehaviorConfig(
            search_mappings={
                "Full Search": lambda x: LeaseNumberParser(x).search_full(),
                "Partial Search": lambda x: LeaseNumberParser(x).search_partial(),
            },
            blank_columns=[
                "New Format",
                "Tractstar",
                "Old Format",
                "MI Index",
                "Documents",
                "Search Notes",
                "Link",
            ],
        ),
    },
    "Federal": {
        "static": AgencyStaticConfig(
            column_widths={
                "Agency": 15,
                "Order Type": 15,
                "Order Number": 15,
                "Order Date": 15,
                "Lease": 15,
                "Requested Legal": 25,
                "Report Start Date": 20,
                "Notes": 30,
                "Files Search": 14,
                "Tractstar Search": 14,
                "New Format": 12,
                "Tractstar": 12,
                "Documents": 12,
                "Search Notes": 30,
                "Link": 30,
            },
            folder_structure=["^Document Archive", "Runsheets"],
            dropbox_agency_name="Federal",
        ),
        "behavioral": AgencyBehaviorConfig(
            search_mappings={
                "Files Search": lambda x: LeaseNumberParser(x).search_file(),
                "Tractstar Search": lambda x: LeaseNumberParser(x).search_tractstar(),
            },
            blank_columns=[
                "New Format",
                "Tractstar",
                "Documents",
                "Search Notes",
                "Link",
            ],
        ),
    },
}


def _validate_all_configurations():
    """
    Comprehensive validation of all agency configurations at startup.

    Validates both static and behavioral configurations for all agencies,
    tests with appropriate sample data, and ensures all configurations
    work correctly together.

    Called during module initialization to ensure fail-fast behavior.

    Raises:
        ConfigurationError: If any configuration validation fails
    """
    validation_results = {}

    try:
        logger.info("Starting comprehensive configuration validation...")

        for agency_name, agency_config in AGENCY_CONFIGS.items():
            logger.debug(f"Validating {agency_name} configuration...")

            # Track validation results for this agency
            agency_results = {
                "static_validation": False,
                "behavioral_validation": False,
                "sample_data_validation": False,
                "integration_validation": False,
            }

            # Validate static configuration
            try:
                static_config = agency_config["static"]
                static_config.validate_static_configuration()
                agency_results["static_validation"] = True
                logger.debug(f"✓ {agency_name} static configuration validated")
            except Exception as e:
                raise ConfigurationError(
                    f"{agency_name} static configuration failed: {str(e)}"
                )

            # Validate behavioral configuration
            try:
                behavioral_config = agency_config["behavioral"]
                behavioral_config.validate_behavioral_configuration()
                agency_results["behavioral_validation"] = True
                logger.debug(f"✓ {agency_name} behavioral configuration validated")
            except Exception as e:
                raise ConfigurationError(
                    f"{agency_name} behavioral configuration failed: {str(e)}"
                )

            # Validate with agency-specific sample data
            try:
                sample_data = _get_agency_sample_data(agency_name)
                behavioral_config.validate_with_sample_data(sample_data)
                agency_results["sample_data_validation"] = True
                logger.debug(f"✓ {agency_name} sample data validation passed")
            except Exception as e:
                raise ConfigurationError(
                    f"{agency_name} sample data validation failed: {str(e)}"
                )

            # Validate integration between static and behavioral configs
            try:
                _validate_agency_integration(
                    agency_name, static_config, behavioral_config
                )
                agency_results["integration_validation"] = True
                logger.debug(f"✓ {agency_name} integration validation passed")
            except Exception as e:
                raise ConfigurationError(
                    f"{agency_name} integration validation failed: {str(e)}"
                )

            validation_results[agency_name] = agency_results

        # Final validation summary
        total_agencies = len(AGENCY_CONFIGS)
        successful_validations = sum(
            1 for results in validation_results.values() if all(results.values())
        )

        logger.info(
            f"Configuration validation completed: {successful_validations}/{total_agencies} agencies validated successfully"
        )

        if successful_validations != total_agencies:
            raise ConfigurationError("Not all agency configurations passed validation")

    except Exception as e:
        logger.error(f"Startup configuration validation failed: {str(e)}")
        raise ConfigurationError(f"Failed to validate agency configurations: {str(e)}")


def _get_agency_sample_data(agency_name: str) -> str:
    """
    Get appropriate sample lease data for agency-specific testing.

    Args:
        agency_name: Name of the agency

    Returns:
        Sample lease number in the correct format for the agency

    Raises:
        ConfigurationError: If agency is not supported
    """
    sample_data_map = {
        "NMSLO": "B-1234-5",  # NMSLO lease format
        "Federal": "NMNM 12345A",  # Federal lease format
    }

    if agency_name not in sample_data_map:
        raise ConfigurationError(f"No sample data defined for agency: {agency_name}")

    return sample_data_map[agency_name]


def _validate_agency_integration(
    agency_name: str, static_config, behavioral_config
) -> None:
    """
    Validate integration between static and behavioral configurations.

    Ensures that the configurations work together correctly and don't have
    conflicting or incompatible settings.

    Args:
        agency_name: Name of the agency being validated
        static_config: AgencyStaticConfig instance
        behavioral_config: AgencyBehaviorConfig instance

    Raises:
        ConfigurationError: If integration validation fails
    """
    # Check that all search columns have column widths defined
    search_columns = behavioral_config.get_search_columns()
    for search_column in search_columns:
        if search_column not in static_config.column_widths:
            raise ConfigurationError(
                f"{agency_name}: Search column '{search_column}' missing from static column_widths"
            )

    # Check that all blank columns have column widths defined
    blank_columns = behavioral_config.get_blank_columns()
    for blank_column in blank_columns:
        if blank_column not in static_config.column_widths:
            raise ConfigurationError(
                f"{agency_name}: Blank column '{blank_column}' missing from static column_widths"
            )

    # Check that dropbox_agency_name is consistent with agency name expectations
    if not static_config.dropbox_agency_name:
        raise ConfigurationError(f"{agency_name}: dropbox_agency_name cannot be empty")

    # Validate reasonable folder structure for agency type
    if agency_name == "NMSLO" and len(static_config.folder_structure) < 2:
        raise ConfigurationError(
            f"{agency_name}: Expected at least 2 folders in structure, got {len(static_config.folder_structure)}"
        )

    if agency_name == "Federal" and len(static_config.folder_structure) < 1:
        raise ConfigurationError(
            f"{agency_name}: Expected at least 1 folder in structure, got {len(static_config.folder_structure)}"
        )

    logger.debug(f"Integration validation passed for {agency_name}")


# Validate configurations on module import
_validate_all_configurations()
