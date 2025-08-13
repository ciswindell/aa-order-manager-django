"""
Agency storage configuration utilities.
"""

from ..models import AgencyStorageConfig
from orders.models import AgencyType


class AgencyStorageConfigError(Exception):
    """Raised when agency storage configuration is missing or disabled."""

    pass


def get_agency_storage_config(agency: AgencyType) -> AgencyStorageConfig:
    """
    Get agency storage configuration for the specified agency.

    Args:
        agency: AgencyType enum value (e.g., AgencyType.NMSLO, AgencyType.BLM)

    Returns:
        AgencyStorageConfig: The configuration for the agency

    Raises:
        AgencyStorageConfigError: If configuration is missing or disabled
    """
    try:
        config = AgencyStorageConfig.objects.get(agency=agency)
    except AgencyStorageConfig.DoesNotExist:
        raise AgencyStorageConfigError(
            f"No storage configuration found for agency: {agency}"
        )

    if not config.enabled:
        raise AgencyStorageConfigError(
            f"Storage configuration is disabled for agency: {agency}"
        )

    return config
