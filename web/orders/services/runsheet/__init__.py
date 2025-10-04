"""
Runsheet service layer.

This package contains domain services for runsheet archive operations,
following clean architecture principles with single-responsibility services.
"""

from .archive_creator import RunsheetArchiveCreator
from .archive_finder import RunsheetArchiveFinder
from .discovery_workflow import (
    FullRunsheetDiscoveryWorkflow,
    RunsheetDiscoveryWorkflow,
)
from .exceptions import (
    BasePathMissingError,
    DirectoryCreationError,
    RunsheetServiceError,
)
from .report_detector import PreviousReportDetector
from .results import (
    ArchiveCreationResult,
    ArchiveSearchResult,
    ReportDetectionResult,
)

__all__ = [
    # Services
    "RunsheetArchiveFinder",
    "RunsheetArchiveCreator",
    "PreviousReportDetector",
    # Workflows
    "RunsheetDiscoveryWorkflow",
    "FullRunsheetDiscoveryWorkflow",
    # Exceptions
    "RunsheetServiceError",
    "BasePathMissingError",
    "DirectoryCreationError",
    # Results
    "ArchiveSearchResult",
    "ArchiveCreationResult",
    "ReportDetectionResult",
]
