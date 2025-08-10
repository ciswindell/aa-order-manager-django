"""
Business Object Model Validators

Validators for business object validation including OrderData and OrderItemData.
These validators handle validation of dataclass instances and business logic.
"""

from typing import Tuple
from .protocols import ValidatorBase
from .messages import ValidationMessages, MessageType


class OrderDataValidator(ValidatorBase):
    """
    Validates OrderData business objects.

    This validator handles validation of OrderData instances, replacing the
    current __post_init__ validation with external validation service.
    """

    def validate(self, order_data) -> Tuple[bool, str]:
        """
        Validate OrderData business object.

        Args:
            order_data: OrderData instance to validate

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, technical_error) if invalid
        """
        from datetime import date
        from src.core.models import ReportType, OrderItemData

        # Validate order_number - required, non-empty string with proper format
        is_valid, error = self.validate_required_field(
            order_data.order_number, "order_number", str
        )
        if not is_valid:
            return False, error

        # Validate order number format if not "Unknown" (GUI may set this default)
        if order_data.order_number != "Unknown":
            is_valid, error = self._validate_order_number_format(
                order_data.order_number
            )
            if not is_valid:
                return False, error

        # Validate order_date - required, must be date object
        if not isinstance(order_data.order_date, date):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="order_date",
                expected_type="date",
            )
            return False, error

        # Validate order_type - required, must be ReportType enum
        if not isinstance(order_data.order_type, ReportType):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="order_type",
                expected_type="ReportType enum",
            )
            return False, error

        # Validate order_items - required, must be list
        if not isinstance(order_data.order_items, list):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="order_items",
                expected_type="list",
            )
            return False, error

        # Validate each order item is OrderItemData instance
        for i, item in enumerate(order_data.order_items):
            if not isinstance(item, OrderItemData):
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL,
                    "collection_item_invalid",
                    field="order_items",
                    index=i,
                    expected_type="OrderItemData instance",
                )
                return False, error

        # Validate optional fields have correct types when provided
        if order_data.order_notes is not None and not isinstance(
            order_data.order_notes, str
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="order_notes",
                expected_type="str or None",
            )
            return False, error

        if order_data.delivery_link is not None and not isinstance(
            order_data.delivery_link, str
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="delivery_link",
                expected_type="str or None",
            )
            return False, error

        return True, ""

    def _validate_order_number_format(self, order_number: str) -> Tuple[bool, str]:
        """
        Validate order number format - should contain only letters, numbers, hyphens, and underscores.

        Args:
            order_number: Order number string to validate

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, technical_error) if invalid
        """
        if not order_number or order_number.strip() == "":
            return True, ""  # Empty is handled by required field validation

        # Check if order number contains only letters, numbers, hyphens, and underscores
        cleaned_number = order_number.replace("-", "").replace("_", "")
        if not cleaned_number.isalnum():
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "invalid_format",
                field="order_number",
                requirement="should contain only letters, numbers, hyphens, and underscores",
            )
            return False, error

        return True, ""


class OrderItemDataValidator(ValidatorBase):
    """
    Validates OrderItemData business objects.

    This validator handles validation of OrderItemData instances, replacing the
    current __post_init__ validation with external validation service.

    TODO: Implement validation for the following scenarios:

    1. Agency Validation:
       - Check isinstance(item_data.agency, AgencyType)
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "wrong_type",
         field="agency", expected_type="AgencyType enum")
       - Current logic location: models.py lines 206-208

    2. Lease Number Validation:
       - Check isinstance(item_data.lease_number, str)
       - Check lease_number.strip() is not empty
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "wrong_type",
         field="lease_number", expected_type="str")
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "empty_value",
         field="lease_number")
       - Current logic location: models.py lines 210-213

    3. Legal Description Validation:
       - Check isinstance(item_data.legal_description, str)
       - Check legal_description.strip() is not empty
       - Use ValidationMessages.format_message(MessageType.TECHNICAL, "empty_value",
         field="legal_description")
       - Current logic location: models.py lines 215-219

    4. Date Fields Validation:
       - Check start_date is datetime or None
       - Check end_date is datetime or None
       - Check end_date > start_date if both provided
       - Use appropriate TECHNICAL messages for validation failures
       - Current logic location: models.py lines 221-232

    5. Optional Fields Validation:
       - Validate all optional string fields
       - Validate list fields (documents_links, misc_index_links)
       - Use appropriate TECHNICAL messages
       - Current logic location: models.py lines 234-282

    Integration Notes:
    - Should be called from OrderItemData.__post_init__() method
    - Should replace existing validation logic in models.py
    - Error messages should be technical for business object validation
    - Should work with all OrderItemData fields including workflow-generated ones
    """

    def validate(self, item_data) -> Tuple[bool, str]:
        """
        Validate OrderItemData business object.

        Args:
            item_data: OrderItemData instance to validate

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, technical_error) if invalid
        """
        from datetime import datetime
        from src.core.models import AgencyType

        # 1. Validate agency - required, must be AgencyType enum
        if not isinstance(item_data.agency, AgencyType):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="agency",
                expected_type="AgencyType enum",
            )
            return False, error

        # 2. Validate lease_number - required, non-empty string
        is_valid, error = self.validate_required_field(
            item_data.lease_number, "lease_number", str
        )
        if not is_valid:
            return False, error

        # 3. Validate legal_description - required, non-empty string
        is_valid, error = self.validate_required_field(
            item_data.legal_description, "legal_description", str
        )
        if not is_valid:
            return False, error

        # 4. Validate start_date - optional, must be datetime object if provided
        if item_data.start_date is not None and not isinstance(
            item_data.start_date, datetime
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="start_date",
                expected_type="datetime or None",
            )
            return False, error

        # 4. Validate end_date - optional, must be datetime object if provided
        if item_data.end_date is not None and not isinstance(
            item_data.end_date, datetime
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="end_date",
                expected_type="datetime or None",
            )
            return False, error

        # 4. Validate date range - end_date must be after start_date if both provided
        if (
            item_data.start_date is not None
            and item_data.end_date is not None
            and item_data.end_date <= item_data.start_date
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "date_range_invalid",
                field="end_date",
                requirement="must be after start_date",
            )
            return False, error

        # 5. Validate report_notes - optional, must be string if provided
        if item_data.report_notes is not None and not isinstance(
            item_data.report_notes, str
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="report_notes",
                expected_type="str or None",
            )
            return False, error

        # 5. Validate optional workflow string fields
        if item_data.report_directory_link is not None and not isinstance(
            item_data.report_directory_link, str
        ):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="report_directory_link",
                expected_type="str or None",
            )
            return False, error

        if item_data.report_directory_path is not None:
            if not isinstance(item_data.report_directory_path, str):
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL,
                    "wrong_type",
                    field="report_directory_path",
                    expected_type="a string or None",
                )
                return False, error
            if not item_data.report_directory_path.strip():
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL, "empty_value", field="report_directory_path"
                )
                return False, error

        # 5. Validate optional boolean fields
        boolean_fields = [
            ("previous_report_found", item_data.previous_report_found),
            ("tractstar_needed", item_data.tractstar_needed),
            ("documents_needed", item_data.documents_needed),
            ("misc_index_needed", item_data.misc_index_needed),
        ]

        for field_name, field_value in boolean_fields:
            if field_value is not None and not isinstance(field_value, bool):
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL,
                    "wrong_type",
                    field=field_name,
                    expected_type="bool or None",
                )
                return False, error

        # 5. Validate list fields are lists with string elements
        if not isinstance(item_data.documents_links, list):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="documents_links",
                expected_type="list",
            )
            return False, error
        for i, link in enumerate(item_data.documents_links):
            if not isinstance(link, str):
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL,
                    "collection_item_invalid",
                    field="documents_links",
                    index=i,
                    expected_type="str",
                )
                return False, error

        if not isinstance(item_data.misc_index_links, list):
            error = ValidationMessages.format_message(
                MessageType.TECHNICAL,
                "wrong_type",
                field="misc_index_links",
                expected_type="list",
            )
            return False, error
        for i, link in enumerate(item_data.misc_index_links):
            if not isinstance(link, str):
                error = ValidationMessages.format_message(
                    MessageType.TECHNICAL,
                    "collection_item_invalid",
                    field="misc_index_links",
                    index=i,
                    expected_type="str",
                )
                return False, error

        return True, ""
