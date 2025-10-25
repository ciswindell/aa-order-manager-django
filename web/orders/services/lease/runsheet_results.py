"""
Result dataclasses for runsheet services.

These dataclasses provide structured return values from service methods,
making the API clear and type-safe.
"""

from dataclasses import dataclass
from typing import List, Optional

from integrations.models import CloudLocation


@dataclass
class ArchiveSearchResult:
    """
    Result of searching for an existing runsheet archive.

    Attributes:
        found: Whether the archive was found in cloud storage
        path: The full path to the archive directory
        share_url: Shareable URL for the archive (if found and link created)
        cloud_location: CloudLocation model instance (if found)
    """

    found: bool
    path: str
    share_url: Optional[str] = None
    cloud_location: Optional[CloudLocation] = None


@dataclass
class ArchiveCreationResult:
    """
    Result of creating a new runsheet archive.

    Attributes:
        success: Whether the archive was successfully created
        path: The full path to the created archive directory
        share_url: Shareable URL for the archive (if link created)
        cloud_location: CloudLocation model instance (if created)
    """

    success: bool
    path: str
    share_url: Optional[str] = None
    cloud_location: Optional[CloudLocation] = None


@dataclass
class ReportDetectionResult:
    """
    Result of detecting previous reports in a directory.

    Attributes:
        found: Whether any matching report files were found
        matching_files: List of filenames that matched the report patterns
        directory_path: The directory that was searched
    """

    found: bool
    matching_files: List[str]
    directory_path: str
