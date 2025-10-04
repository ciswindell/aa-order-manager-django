"""
Previous Report Detector Service.

This service scans directories for existing Master Documents files
to detect previous reports.
"""

import logging
import re
from typing import Any

from django.conf import settings
from orders.services.runsheet.results import ReportDetectionResult

from integrations.cloud.errors import CloudServiceError

logger = logging.getLogger(__name__)


class PreviousReportDetector:
    """
    Service to detect previous reports in a directory.

    This service scans a directory for files matching known report patterns
    (e.g., "Master Documents") and returns structured detection results.
    Does NOT update lease records.
    """

    def __init__(self, pattern: str = None):
        """
        Initialize PreviousReportDetector.

        Args:
            pattern: Regex pattern to match report files (defaults to settings value)
        """
        self.pattern = pattern or getattr(
            settings, "RUNSHEET_PREVIOUS_REPORT_PATTERN", r".*master documents.*"
        )
        self.regex = re.compile(self.pattern, re.IGNORECASE)
        logger.debug(
            "Initialized PreviousReportDetector with pattern: %s", self.pattern
        )

    def detect_reports(
        self, directory_path: str, cloud_service: Any
    ) -> ReportDetectionResult:
        """
        Scan a directory for previous report files.

        Args:
            directory_path: The directory path to scan
            cloud_service: Authenticated cloud service instance

        Returns:
            ReportDetectionResult with detection results

        Raises:
            CloudServiceError: If cloud operations fail (retryable)
        """
        logger.info("Scanning directory for previous reports: %s", directory_path)

        try:
            # List files in the directory
            files = cloud_service.list_files(directory_path)

            if not files:
                logger.info("No files found in directory: %s", directory_path)
                return ReportDetectionResult(
                    found=False, matching_files=[], directory_path=directory_path
                )

            # Search for matching files
            matching_files = []
            for file in files:
                if self.regex.search(file.name):
                    matching_files.append(file.name)
                    logger.debug("Found matching file: %s", file.name)

            if matching_files:
                logger.info(
                    "Found %d previous report files in %s",
                    len(matching_files),
                    directory_path,
                )
            else:
                logger.info("No previous report files found in %s", directory_path)

            return ReportDetectionResult(
                found=len(matching_files) > 0,
                matching_files=matching_files,
                directory_path=directory_path,
            )

        except CloudServiceError:
            logger.error(
                "Cloud service error while scanning directory: %s", directory_path
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error scanning directory %s: %s", directory_path, str(e)
            )
            raise CloudServiceError(f"Failed to scan directory: {str(e)}", "dropbox")
