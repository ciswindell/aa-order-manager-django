"""
Runsheet Archive Search Service

Service to find agency-specific runsheet archives in Dropbox and create shareable links.
"""

import logging
from typing import Any, Dict

from django.contrib.auth.models import User
from orders.models import Lease

from integrations.cloud.errors import CloudServiceError
from integrations.cloud.factory import get_cloud_service
from integrations.models import CloudLocation
from integrations.utils import AgencyStorageConfigError, get_agency_storage_config

logger = logging.getLogger(__name__)


def run_runsheet_archive_search(lease_id: int, user_id: int) -> Dict[str, Any]:
    """
    Search for a runsheet archive in Dropbox and create a shareable link if found.

    Args:
        lease_id: ID of the lease to search for
        user_id: ID of the user initiating the search (for Dropbox auth)

    Returns:
        Dict containing search results: {found, path, share_url, location_id}

    Raises:
        Lease.DoesNotExist: If lease not found
        User.DoesNotExist: If user not found
        AgencyStorageConfigError: If agency config missing/disabled
        CloudServiceError: If Dropbox operations fail
    """
    # Load lease and user
    lease = Lease.objects.get(id=lease_id)
    user = User.objects.get(id=user_id)

    logger.info(
        "Starting runsheet archive search for lease %s (agency: %s, lease_number: %s)",
        lease_id,
        lease.agency,
        lease.lease_number,
    )

    try:
        # Resolve agency config
        agency_config = get_agency_storage_config(lease.agency)

        # Build directory path
        directory_path = (
            f"{agency_config.runsheet_archive_base_path}/{lease.lease_number}"
        )

        logger.info("Searching directory path: %s", directory_path)

        # Get Dropbox client for user
        cloud_service = get_cloud_service(provider="dropbox", user=user)

        # Authenticate then verify
        try:
            cloud_service.authenticate()
        except Exception:
            # Fallback to state check even if authenticate() is a no-op
            pass
        if not cloud_service.is_authenticated():
            raise CloudServiceError("Dropbox client is not authenticated", "dropbox")

        # Check directory existence via listing
        files = cloud_service.list_files(directory_path)

        if files:
            # Directory exists, create share link
            logger.info("Directory found, creating share link")
            share_link = cloud_service.create_share_link(directory_path, is_public=True)

            if share_link:
                # Upsert CloudLocation and update Lease
                cloud_location, created = CloudLocation.objects.update_or_create(
                    provider="dropbox",
                    path=directory_path,
                    defaults={
                        "name": lease.lease_number,
                        "is_directory": True,
                        "share_url": share_link.url,
                        "share_expires_at": share_link.expires_at,
                        "is_public": share_link.is_public,
                    },
                )

                # Update lease with the cloud location and share link
                lease.runsheet_archive = cloud_location
                lease.runsheet_link = share_link.url
                lease.save(update_fields=["runsheet_archive", "runsheet_link"])

                action = "created" if created else "updated"
                logger.info(
                    "Successfully %s share link and updated lease. Location ID: %s",
                    action,
                    cloud_location.id,
                )

                return {
                    "found": True,
                    "path": directory_path,
                    "share_url": share_link.url,
                    "location_id": cloud_location.id,
                }

            logger.warning(
                "Failed to create share link for directory: %s", directory_path
            )
            return {
                "found": True,
                "path": directory_path,
                "share_url": None,
                "location_id": None,
            }
        else:
            # Directory doesn't exist
            logger.info("Directory not found: %s", directory_path)

            # Optional: attempt creation of the root runsheet archive if enabled and base exists
            try:
                if getattr(agency_config, "auto_create_runsheet_archives", True):
                    base_path = agency_config.runsheet_archive_base_path
                    # Probe base path existence by metadata; workspace-first inside service
                    base_exists = False
                    try:
                        md = cloud_service._get_metadata(base_path)  # type: ignore[attr-defined]
                        base_exists = md is not None
                    except Exception:
                        base_exists = False

                    if base_exists:
                        logger.info(
                            "Attempting to create runsheet archive at: %s",
                            directory_path,
                        )
                        # Explicit console output for live debugging
                        print(
                            f"[runsheet-archive-create] attempting creation: {directory_path}",
                            flush=True,
                        )
                        try:
                            # Create only if subfolders are configured (safety gate)
                            subfolders = [
                                f
                                for f in [
                                    getattr(
                                        agency_config,
                                        "runsheet_subfolder_documents_name",
                                        None,
                                    ),
                                    getattr(
                                        agency_config,
                                        "runsheet_subfolder_misc_index_name",
                                        None,
                                    ),
                                    getattr(
                                        agency_config,
                                        "runsheet_subfolder_runsheets_name",
                                        None,
                                    ),
                                ]
                                if f
                            ]

                            if subfolders:
                                created_dir = cloud_service.create_directory(
                                    directory_path, parents=True
                                )
                                if created_dir:
                                    cloud_service.create_directory_tree(
                                        directory_path, subfolders, exists_ok=True
                                    )

                                    # Create share link for the runsheet archive
                                    share_link = cloud_service.create_share_link(
                                        directory_path, is_public=True
                                    )

                                    # Upsert cloud location and update lease
                                    defaults = {
                                        "name": lease.lease_number,
                                        "is_directory": True,
                                    }
                                    if share_link:
                                        defaults.update(
                                            {
                                                "share_url": share_link.url,
                                                "share_expires_at": getattr(
                                                    share_link, "expires_at", None
                                                ),
                                                "is_public": share_link.is_public,
                                            }
                                        )

                                    cloud_location, _ = (
                                        CloudLocation.objects.update_or_create(
                                            provider="dropbox",
                                            path=directory_path,
                                            defaults=defaults,
                                        )
                                    )
                                    lease.runsheet_archive = cloud_location
                                    lease.runsheet_report_found = False
                                    # Set runsheet_link if share_link was created
                                    if share_link:
                                        lease.runsheet_link = share_link.url
                                    lease.save(
                                        update_fields=[
                                            "runsheet_archive",
                                            "runsheet_report_found",
                                            "runsheet_link",
                                        ]
                                    )
                                    logger.info(
                                        "Created runsheet archive and subfolders for %s",
                                        lease.lease_number,
                                    )

                                    # Return success so detection task runs
                                    return {
                                        "found": True,
                                        "path": directory_path,
                                        "share_url": share_link.url
                                        if share_link
                                        else None,
                                        "location_id": cloud_location.id,
                                    }
                        except Exception as create_err:
                            logger.warning(
                                "Runsheet archive create skipped/failed at %s: %s",
                                directory_path,
                                str(create_err),
                            )
                    else:
                        logger.warning(
                            "Base path missing, skipping directory creation. base=%s",
                            base_path,
                        )
            except Exception as e:
                logger.warning("Creation attempt error (ignored): %s", str(e))

            return {
                "found": False,
                "path": directory_path,
                "share_url": None,
                "location_id": None,
            }

    except AgencyStorageConfigError as e:
        logger.error("Agency storage config error for lease %s: %s", lease_id, str(e))
        # Agency config errors are not retriable - they require admin action
        raise
    except CloudServiceError as e:
        logger.error("Cloud service error for lease %s: %s", lease_id, str(e))
        # Cloud service errors (auth, network) are retriable
        raise
    except Exception as e:
        logger.error(
            "Unexpected error in runsheet archive search for lease %s: %s",
            lease_id,
            str(e),
        )
        # Let unexpected errors propagate to avoid retrying non-transient bugs
        raise
