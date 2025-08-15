"""
Previous Report Detection Service

Service to scan lease directories for existing Master Documents files.
"""

import logging
import re
from typing import Dict, Any

from django.contrib.auth.models import User
from django.conf import settings

from orders.models import Lease
from integrations.cloud.factory import get_cloud_service
from integrations.cloud.errors import CloudServiceError

logger = logging.getLogger(__name__)


def run_previous_report_detection(lease_id: int, user_id: int) -> Dict[str, Any]:
    """
    Scan a runsheet archive for existing Master Documents files.

    Args:
        lease_id: ID of the lease to scan
        user_id: ID of the user initiating the scan (for Dropbox auth)

    Returns:
        Dict containing detection results: {found, matching_files}

    Raises:
        Lease.DoesNotExist: If lease not found
        User.DoesNotExist: If user not found
        CloudServiceError: If Dropbox operations fail
    """
    # Load lease and user
    lease = Lease.objects.get(id=lease_id)
    user = User.objects.get(id=user_id)

    logger.info(
        "Starting previous report detection for lease %s (agency: %s, lease_number: %s)",
        lease_id,
        lease.agency,
        lease.lease_number,
    )

    # Require runsheet_archive to be present
    if not lease.runsheet_archive:
        logger.info(
            "No runsheet archive found for lease %s, skipping detection", lease_id
        )
        return {
            "found": False,
            "matching_files": [],
        }

    try:
        # Get the directory path from the cloud location
        directory_path = lease.runsheet_archive.path

        logger.info("Scanning directory for Master Documents: %s", directory_path)

        # Get Dropbox client for user
        cloud_service = get_cloud_service(provider="dropbox", user=user)

        # Authenticate then verify
        try:
            cloud_service.authenticate()
        except Exception:
            pass
        if not cloud_service.is_authenticated():
            raise CloudServiceError("Dropbox client is not authenticated", "dropbox")

        # List files in the directory
        files = cloud_service.list_files(directory_path)

        # Get regex pattern from settings
        pattern = getattr(
            settings, "RUNSHEET_PREVIOUS_REPORT_PATTERN", r".*master documents.*"
        )
        regex = re.compile(pattern, re.IGNORECASE)

        # Search for matching files
        matching_files = []
        for file in files:
            if regex.search(file.name):
                matching_files.append(file.name)
                logger.debug("Found matching file: %s", file.name)

        # Update lease with detection result
        lease.runsheet_report_found = len(matching_files) > 0
        lease.save(update_fields=["runsheet_report_found"])

        if matching_files:
            logger.info(
                "Found %d Master Documents files for lease %s",
                len(matching_files),
                lease_id,
            )
        else:
            logger.info("No Master Documents files found for lease %s", lease_id)

        return {
            "found": len(matching_files) > 0,
            "matching_files": matching_files,
        }

    except CloudServiceError as e:
        logger.error("Cloud service error for lease %s: %s", lease_id, str(e))
        # Cloud service errors (auth, network) are retriable
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in previous report detection for lease %s: %s",
            lease_id,
            str(e),
        )
        # Let unexpected errors propagate to avoid retrying non-transient bugs
        raise
