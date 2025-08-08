"""
Order Data Models

Data structures for order and order item information in the Order Data Collection Platform.

This module provides comprehensive data models that support the transformation from
manual worksheet generation to automated data collection workflows. The models handle
order-level tracking, detailed order item metadata, workflow-generated data, and
collection status across multiple agencies (NMSLO and BLM).

Key Features:
- Comprehensive order and order item data structures
- JSON serialization for API integration and data persistence
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
    
    # Serialize to JSON
    json_data = order.to_json()
    
    # Convert order item to worksheet format  
    worksheet_data = order.order_items[0].to_worksheet_data()
    print(worksheet_data)  # Shows dictionary with worksheet column mappings
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import json


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


class OrderDataJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for OrderData and OrderItemData objects.

    Handles serialization of:
    - datetime objects (converted to ISO format strings)
    - date objects (converted to ISO format strings)
    - Enum objects (converted to their string values)
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


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
        notes: Optional additional order-level notes
        delivery_link: Optional link for order delivery
        order_items: List of OrderItemData objects belonging to this order
    """

    order_number: str
    order_date: date
    order_type: ReportType
    order_items: List["OrderItemData"] = field(default_factory=list)
    notes: Optional[str] = None
    delivery_link: Optional[str] = None

    def __post_init__(self):
        """
        Validate OrderData fields after initialization.

        Performs validation on required fields and data types to ensure
        data integrity. Called automatically by dataclass after __init__.

        Raises:
            ValueError: If any field validation fails
        """
        # Validate order_number - required, non-empty string
        if not isinstance(self.order_number, str):
            raise ValueError("order_number must be a string")
        if not self.order_number.strip():
            raise ValueError("order_number cannot be empty")

        # Validate order_date - required, must be date object
        if not isinstance(self.order_date, date):
            raise ValueError("order_date must be a date object")

        # Validate order_type - required, must be ReportType enum
        if not isinstance(self.order_type, ReportType):
            raise ValueError("order_type must be a ReportType enum value")

        # Validate order_items - required, must be list
        if not isinstance(self.order_items, list):
            raise ValueError("order_items must be a list")

        # Validate each order item is OrderItemData instance
        for i, item in enumerate(self.order_items):
            if not isinstance(item, OrderItemData):
                raise ValueError(f"order_items[{i}] must be an OrderItemData instance")

        # Validate optional fields have correct types when provided
        if self.notes is not None and not isinstance(self.notes, str):
            raise ValueError("notes must be a string or None")

        if self.delivery_link is not None and not isinstance(self.delivery_link, str):
            raise ValueError("delivery_link must be a string or None")

    def to_json(self) -> str:
        """
        Serialize OrderData object to JSON string.

        Handles datetime objects, enums, and nested OrderItemData objects
        using the custom OrderDataJSONEncoder.

        Returns:
            str: JSON representation of the OrderData object
        """
        return json.dumps(asdict(self), cls=OrderDataJSONEncoder, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "OrderData":
        """
        Deserialize OrderData object from JSON string.

        Handles conversion of ISO datetime strings back to datetime objects
        and enum string values back to enum instances.

        Args:
            json_str: JSON string representation of OrderData

        Returns:
            OrderData: Reconstructed OrderData object

        Raises:
            ValueError: If JSON is malformed or contains invalid data
        """
        try:
            data = json.loads(json_str)

            # Convert order_date string back to date object
            if "order_date" in data and isinstance(data["order_date"], str):
                data["order_date"] = datetime.fromisoformat(data["order_date"]).date()

            # Convert order_type string back to ReportType enum
            if "order_type" in data and isinstance(data["order_type"], str):
                data["order_type"] = ReportType(data["order_type"])

            # Convert order_items list back to OrderItemData objects
            if "order_items" in data and isinstance(data["order_items"], list):
                order_items = []
                for item_data in data["order_items"]:
                    # Convert datetime strings back to datetime objects
                    if "start_date" in item_data and isinstance(
                        item_data["start_date"], str
                    ):
                        item_data["start_date"] = datetime.fromisoformat(
                            item_data["start_date"]
                        )
                    if "end_date" in item_data and isinstance(
                        item_data["end_date"], str
                    ):
                        item_data["end_date"] = datetime.fromisoformat(
                            item_data["end_date"]
                        )

                    # Convert agency string back to AgencyType enum
                    if "agency" in item_data and isinstance(item_data["agency"], str):
                        item_data["agency"] = AgencyType(item_data["agency"])

                    order_items.append(OrderItemData(**item_data))
                data["order_items"] = order_items

            return cls(**data)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to deserialize OrderData from JSON: {e}")


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
        documents_links: List of links to documents subdirectories (populated by workflow)
        lease_index_links: List of links to lease index directories - NMSLO only (populated by workflow)

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

        # Serialize with workflow data
        json_data = order_item.to_json()
    """

    # User Input Fields
    agency: AgencyType
    lease_number: str
    legal_description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None

    # Workflow-Generated Fields
    report_directory_link: Optional[str] = None
    report_directory_path: Optional[str] = None
    previous_report_found: Optional[bool] = None
    documents_links: List[str] = field(default_factory=list)
    lease_index_links: List[str] = field(default_factory=list)  # NMSLO only

    def __post_init__(self):
        """
        Validate OrderItemData fields after initialization.

        Performs validation on required fields, data types, and business rules
        to ensure data integrity. Called automatically by dataclass after __init__.

        Raises:
            ValueError: If any field validation fails
        """
        # Validate agency - required, must be AgencyType enum
        if not isinstance(self.agency, AgencyType):
            raise ValueError("agency must be an AgencyType enum value")

        # Validate lease_number - required, non-empty string
        if not isinstance(self.lease_number, str):
            raise ValueError("lease_number must be a string")
        if not self.lease_number.strip():
            raise ValueError("lease_number cannot be empty")

        # Validate legal_description - required, non-empty string
        if not isinstance(self.legal_description, str):
            raise ValueError("legal_description must be a string")
        if not self.legal_description.strip():
            raise ValueError("legal_description cannot be empty")

        # Validate start_date - optional, must be datetime object if provided
        if self.start_date is not None and not isinstance(self.start_date, datetime):
            raise ValueError("start_date must be a datetime object or None")

        # Validate end_date - optional, must be datetime object if provided
        if self.end_date is not None and not isinstance(self.end_date, datetime):
            raise ValueError("end_date must be a datetime object or None")

        # Validate date range - end_date must be after start_date if both provided
        if self.start_date is not None and self.end_date is not None:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")

        # Validate notes - optional, must be string if provided
        if self.notes is not None and not isinstance(self.notes, str):
            raise ValueError("notes must be a string or None")

        # Validate optional workflow fields have correct types when provided
        if self.report_directory_link is not None and not isinstance(
            self.report_directory_link, str
        ):
            raise ValueError("report_directory_link must be a string or None")

        if self.report_directory_path is not None:
            if not isinstance(self.report_directory_path, str):
                raise ValueError("report_directory_path must be a string or None")
            if not self.report_directory_path.strip():
                raise ValueError("report_directory_path cannot be empty when provided")

        if self.previous_report_found is not None and not isinstance(
            self.previous_report_found, bool
        ):
            raise ValueError("previous_report_found must be a boolean or None")

        # Validate list fields are lists with string elements
        if not isinstance(self.documents_links, list):
            raise ValueError("documents_links must be a list")
        for i, link in enumerate(self.documents_links):
            if not isinstance(link, str):
                raise ValueError(f"documents_links[{i}] must be a string")

        if not isinstance(self.lease_index_links, list):
            raise ValueError("lease_index_links must be a list")
        for i, link in enumerate(self.lease_index_links):
            if not isinstance(link, str):
                raise ValueError(f"lease_index_links[{i}] must be a string")

    def to_json(self) -> str:
        """
        Serialize OrderItemData object to JSON string.

        Handles datetime objects and enums using the custom OrderDataJSONEncoder.

        Returns:
            str: JSON representation of the OrderItemData object
        """
        return json.dumps(asdict(self), cls=OrderDataJSONEncoder, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "OrderItemData":
        """
        Deserialize OrderItemData object from JSON string.

        Handles conversion of ISO datetime strings back to datetime objects
        and enum string values back to enum instances.

        Args:
            json_str: JSON string representation of OrderItemData

        Returns:
            OrderItemData: Reconstructed OrderItemData object

        Raises:
            ValueError: If JSON is malformed or contains invalid data
        """
        try:
            data = json.loads(json_str)

            # Convert datetime strings back to datetime objects
            if "start_date" in data and isinstance(data["start_date"], str):
                data["start_date"] = datetime.fromisoformat(data["start_date"])
            if "end_date" in data and isinstance(data["end_date"], str):
                data["end_date"] = datetime.fromisoformat(data["end_date"])

            # Convert agency string back to AgencyType enum
            if "agency" in data and isinstance(data["agency"], str):
                data["agency"] = AgencyType(data["agency"])

            return cls(**data)
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to deserialize OrderItemData from JSON: {e}")

    def to_worksheet_data(self) -> Dict[str, Any]:
        """
        Convert OrderItemData to worksheet-compatible dictionary format.

        Maps OrderItemData fields to standard Excel worksheet column names
        used by the existing processor workflow. Handles agency-specific fields
        and provides appropriate defaults for optional values.

        Returns:
            Dict[str, Any]: Dictionary mapping worksheet column names to values
        """
        # Start with basic required fields
        worksheet_data = {
            "Agency": self.agency.value,  # Convert enum to string
            "Lease": self.lease_number,
            "Legal Description": self.legal_description,
            "Report Start Date": self.start_date,
            "Report End Date": self.end_date,
        }

        # Add workflow-generated fields
        if self.report_directory_link:
            worksheet_data["Link"] = self.report_directory_link
        else:
            worksheet_data["Link"] = ""

        # Handle previous report detection
        if self.previous_report_found is not None:
            worksheet_data["Previous Report Found"] = (
                "Yes" if self.previous_report_found else "No"
            )
        else:
            worksheet_data["Previous Report Found"] = ""

        # Handle multiple document links - concatenate with newlines for Excel display
        if self.documents_links:
            worksheet_data["Documents Links"] = "\n".join(self.documents_links)
        else:
            worksheet_data["Documents Links"] = ""

        # Handle NMSLO-specific lease index links
        if self.agency == AgencyType.NMSLO and self.lease_index_links:
            worksheet_data["Lease Index Links"] = "\n".join(self.lease_index_links)
        elif self.agency == AgencyType.NMSLO:
            worksheet_data["Lease Index Links"] = ""
        # BLM doesn't get this column

        return worksheet_data
