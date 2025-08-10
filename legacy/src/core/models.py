"""
Order Data Models

Data structures for order and order item information in the Order Data Collection Platform.

This module provides comprehensive data models that support the transformation from
manual worksheet generation to automated data collection workflows. The models handle
order-level tracking, detailed order item metadata, workflow-generated data, and
collection status across multiple agencies (NMSLO and BLM).

Key Features:
- Comprehensive order and order item data structures
- Excel worksheet conversion for backward compatibility
- Agency-specific field handling (NMSLO lease index requirements)
- Data validation and error handling

Example:
    # Create an order with order items
    order = OrderData(
        order_number="2024-001",
        order_date=datetime.now().date(),
        order_type=ReportType.BASE_ABSTRACT,
        order_items=[
            OrderItemData(
                agency=AgencyType.NMSLO,
                lease_number="12345",
                legal_description="Section 1, Township 2N, Range 3E",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31)
            )
        ]
    )
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import List, Optional


class ReportType(Enum):
    """
    Enumeration of available report types.

    This enum defines the specific types of reports that can be requested
    in the Order Data Collection Platform.
    """

    RUNSHEET = "Runsheet"
    BASE_ABSTRACT = "Base Abstract"
    SUPPLEMENTAL_ABSTRACT = "Supplemental Abstract"
    DOL_ABSTRACT = "DOL Abstract"


class AgencyType(Enum):
    """
    Enumeration of supported agencies.

    This enum defines the agencies that the Order Data Collection Platform
    can process orders for, each with their own specific workflows and requirements.
    """

    NMSLO = "NMSLO"
    BLM = "BLM"


@dataclass
class OrderData:
    """
    Order-level data structure for tracking multiple order items together.

    This class represents a complete order that may contain multiple order items.
    It provides order-level metadata and aggregates individual order item data
    for comprehensive tracking and reporting.

    Attributes:
        order_number: Unique identifier for the order
        order_date: Date the order was created
        order_type: Type of report requested (ReportType enum value)
        order_notes: Optional additional order-level notes
        delivery_link: Optional link for order delivery
        order_items: List of OrderItemData objects belonging to this order
    """

    order_number: str
    order_date: date
    order_type: ReportType
    order_items: List["OrderItemData"] = field(default_factory=list)
    order_notes: Optional[str] = None
    delivery_link: Optional[str] = None

    def __post_init__(self):
        """
        Validate OrderData fields after initialization.

        Uses the centralized validation service to ensure data integrity.
        Called automatically by dataclass after __init__.

        Raises:
            ValueError: If any field validation fails
        """
        from src.core.validation import OrderDataValidator

        validator = OrderDataValidator()
        is_valid, error = validator.validate(self)
        if not is_valid:
            raise ValueError(error)


@dataclass
class OrderItemData:
    """
    Individual order item data structure with comprehensive workflow tracking.

    This class represents a single order item within an order, containing user input
    data, workflow-generated results, and collection metadata. It supports both
    NMSLO and BLM agency workflows with agency-specific field handling.

    Attributes:
        # User Input Fields
        agency: Agency type (AgencyType enum value)
        lease_number: Lease identifier number
        legal_description: Legal description of the lease area
        start_date: Start date for the order item processing
        end_date: End date for the order item processing

        # Workflow-Generated Fields
        report_directory_link: Link to main lease directory (populated by workflow)
        report_directory_path: Direct report directory path for programmatic access (populated by workflow)
        previous_report_found: Whether existing reports were detected (populated by workflow)
        tractstar_needed: Whether Tractstar data is needed (populated by workflow)
        documents_needed: Whether documents are needed (populated by workflow)
        misc_index_needed: Whether misc index is needed - NMSLO only (populated by workflow)
        documents_links: List of links to documents subdirectories (populated by workflow)
        misc_index_links: List of links to misc index directories - NMSLO only (populated by workflow)

    Example:
        # Create order item with user input
        order_item = OrderItemData(
            agency=AgencyType.BLM,
            lease_number="NMNM 0501759",
            legal_description="Section 5, Township 2N, Range 3E",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31)
        )

        # After LeaseDirectorySearchWorkflow execution
        order_item.report_directory_link = "https://dropbox.com/share/nmnm0501759"
        order_item.report_directory_path = "/Federal/NMNM 0501759"

        # After PreviousReportDetectionWorkflow execution
        order_item.previous_report_found = True  # Master Documents found
    """

    # User Input Fields
    agency: AgencyType
    lease_number: str
    legal_description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    report_notes: Optional[str] = None

    # Workflow-Generated Fields
    report_directory_link: Optional[str] = None
    report_directory_path: Optional[str] = None
    previous_report_found: Optional[bool] = None
    tractstar_needed: Optional[bool] = None
    documents_needed: Optional[bool] = None
    misc_index_needed: Optional[bool] = None  # NMSLO only
    documents_links: List[str] = field(default_factory=list)
    misc_index_links: List[str] = field(default_factory=list)  # NMSLO only

    def __post_init__(self):
        """
        Validate OrderItemData fields after initialization.
        Uses the centralized validation service to ensure data integrity.
        """
        from src.core.validation import OrderItemDataValidator

        validator = OrderItemDataValidator()
        is_valid, error = validator.validate(self)
        if not is_valid:
            raise ValueError(error)
