"""
Unit Tests for Validation Message System

Tests for MessageType enum and ValidationMessages class including
template formatting, parameter substitution, and error handling.
"""

import pytest
from typing import Dict

from src.core.validation.messages import MessageType, ValidationMessages


class TestMessageType:
    """Test suite for MessageType enum."""

    def test_message_type_enum_values(self):
        """Test MessageType enum has correct values."""
        assert MessageType.USER_FRIENDLY.value == "user_friendly"
        assert MessageType.TECHNICAL.value == "technical"

    def test_message_type_enum_members(self):
        """Test MessageType enum has expected members."""
        expected_members = {"USER_FRIENDLY", "TECHNICAL"}
        actual_members = {member.name for member in MessageType}
        assert actual_members == expected_members


class TestValidationMessages:
    """Test suite for ValidationMessages class."""

    def test_format_message_user_friendly_required_selection(self):
        """Test formatting user-friendly required selection message."""
        result = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "required_selection", field="an agency"
        )
        assert result == "Please select an agency"

    def test_format_message_user_friendly_invalid_format(self):
        """Test formatting user-friendly invalid format message."""
        result = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "invalid_format",
            field="Order number",
            requirement="contain only letters and numbers",
        )
        assert result == "Order number should contain only letters and numbers"

    def test_format_message_user_friendly_file_not_found(self):
        """Test formatting user-friendly file not found message."""
        result = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "file_not_found", file_type="Excel"
        )
        assert result == "File not found: Please select an existing Excel file"

    def test_format_message_user_friendly_feature_unavailable(self):
        """Test formatting user-friendly feature unavailable message."""
        result = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "feature_unavailable",
            feature="Abstract workflow",
        )
        assert result == "Abstract workflow is not yet implemented"

    def test_format_message_technical_wrong_type(self):
        """Test formatting technical wrong type message."""
        result = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "wrong_type",
            field="order_number",
            expected_type="string",
        )
        assert result == "order_number must be string"

    def test_format_message_technical_type_mismatch(self):
        """Test formatting technical type mismatch message."""
        result = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "type_mismatch",
            field="order_date",
            expected_type="date",
            actual_type="string",
        )
        assert result == "order_date must be date, got string"

    def test_format_message_technical_empty_value(self):
        """Test formatting technical empty value message."""
        result = ValidationMessages.format_message(
            MessageType.TECHNICAL, "empty_value", field="lease_number"
        )
        assert result == "lease_number cannot be empty"

    def test_format_message_technical_invalid_enum(self):
        """Test formatting technical invalid enum message."""
        result = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "invalid_enum",
            field="agency",
            valid_options="NMSLO, BLM",
        )
        assert result == "agency must be one of NMSLO, BLM"

    def test_format_message_with_multiple_parameters(self):
        """Test formatting message with multiple parameters."""
        result = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "out_of_range",
            field="score",
            min_value="0",
            max_value="100",
        )
        assert result == "score must be between 0 and 100"

    def test_format_message_unknown_message_type(self):
        """Test format_message with unknown message type raises KeyError."""

        # Create a mock enum value that doesn't exist in TEMPLATES
        class MockMessageType:
            value = "unknown_type"

        with pytest.raises(KeyError, match="Unknown message type"):
            ValidationMessages.format_message(
                MockMessageType(), "some_template", field="test"
            )

    def test_format_message_unknown_template_key(self):
        """Test format_message with unknown template key raises KeyError."""
        with pytest.raises(KeyError, match="Unknown template key"):
            ValidationMessages.format_message(
                MessageType.USER_FRIENDLY, "nonexistent_template", field="test"
            )

    def test_format_message_missing_parameter(self):
        """Test format_message with missing parameter raises KeyError."""
        with pytest.raises(KeyError, match="Missing parameter"):
            ValidationMessages.format_message(
                MessageType.USER_FRIENDLY,
                "required_selection",
                # Missing required 'field' parameter
            )

    def test_format_message_extra_parameters_ignored(self):
        """Test format_message ignores extra parameters."""
        result = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "required_selection",
            field="an agency",
            extra_param="ignored",
            another_extra="also_ignored",
        )
        assert result == "Please select an agency"

    def test_get_available_templates_user_friendly(self):
        """Test get_available_templates for USER_FRIENDLY type."""
        templates = ValidationMessages.get_available_templates(
            MessageType.USER_FRIENDLY
        )

        # Check it's a dictionary
        assert isinstance(templates, dict)

        # Check some expected templates exist
        expected_templates = [
            "required_selection",
            "invalid_format",
            "file_not_found",
            "feature_unavailable",
        ]
        for template in expected_templates:
            assert template in templates

        # Check template content
        assert templates["required_selection"] == "Please select {field}"
        assert templates["feature_unavailable"] == "{feature} is not yet implemented"

    def test_get_available_templates_technical(self):
        """Test get_available_templates for TECHNICAL type."""
        templates = ValidationMessages.get_available_templates(MessageType.TECHNICAL)

        # Check it's a dictionary
        assert isinstance(templates, dict)

        # Check some expected templates exist
        expected_templates = [
            "wrong_type",
            "empty_value",
            "invalid_enum",
            "constraint_violation",
        ]
        for template in expected_templates:
            assert template in templates

        # Check template content
        assert templates["wrong_type"] == "{field} must be {expected_type}"
        assert templates["empty_value"] == "{field} cannot be empty"

    def test_get_available_templates_returns_copy(self):
        """Test get_available_templates returns a copy, not original."""
        templates = ValidationMessages.get_available_templates(
            MessageType.USER_FRIENDLY
        )

        # Modify the returned dictionary
        templates["test_key"] = "test_value"

        # Get templates again - should not include our modification
        fresh_templates = ValidationMessages.get_available_templates(
            MessageType.USER_FRIENDLY
        )
        assert "test_key" not in fresh_templates

    def test_get_available_templates_unknown_type(self):
        """Test get_available_templates with unknown type raises KeyError."""

        class MockMessageType:
            value = "unknown_type"

        with pytest.raises(KeyError, match="Unknown message type"):
            ValidationMessages.get_available_templates(MockMessageType())

    def test_get_all_template_keys(self):
        """Test get_all_template_keys returns all template keys by type."""
        all_keys = ValidationMessages.get_all_template_keys()

        # Check structure
        assert isinstance(all_keys, dict)
        assert MessageType.USER_FRIENDLY in all_keys
        assert MessageType.TECHNICAL in all_keys

        # Check USER_FRIENDLY keys
        user_keys = all_keys[MessageType.USER_FRIENDLY]
        assert isinstance(user_keys, list)
        assert "required_selection" in user_keys
        assert "invalid_format" in user_keys
        assert "file_not_found" in user_keys

        # Check TECHNICAL keys
        tech_keys = all_keys[MessageType.TECHNICAL]
        assert isinstance(tech_keys, list)
        assert "wrong_type" in tech_keys
        assert "empty_value" in tech_keys
        assert "invalid_enum" in tech_keys

    def test_template_coverage_user_friendly(self):
        """Test that USER_FRIENDLY templates cover common validation scenarios."""
        templates = ValidationMessages.get_available_templates(
            MessageType.USER_FRIENDLY
        )

        # Form validation coverage
        assert "required_selection" in templates
        assert "invalid_format" in templates
        assert "missing_required" in templates

        # File validation coverage
        assert "file_not_found" in templates
        assert "file_access_error" in templates
        assert "invalid_file_type" in templates

        # Business rule coverage
        assert "feature_unavailable" in templates
        assert "operation_not_allowed" in templates

    def test_template_coverage_technical(self):
        """Test that TECHNICAL templates cover common validation scenarios."""
        templates = ValidationMessages.get_available_templates(MessageType.TECHNICAL)

        # Type validation coverage
        assert "wrong_type" in templates
        assert "type_mismatch" in templates

        # Value validation coverage
        assert "empty_value" in templates
        assert "invalid_value" in templates
        assert "out_of_range" in templates

        # Enum validation coverage
        assert "invalid_enum" in templates
        assert "unknown_option" in templates

        # Collection validation coverage
        assert "invalid_collection" in templates
        assert "collection_item_invalid" in templates

        # File validation coverage
        assert "file_not_found_technical" in templates
        assert "file_access_denied" in templates


class TestValidationMessagesIntegration:
    """Integration tests for message system usage patterns."""

    def test_form_validation_message_flow(self):
        """Test typical form validation message usage."""
        # Simulate form validation failures with user-friendly messages

        # Agency not selected
        msg1 = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "required_selection",
            field="an agency",
        )
        assert "Please select an agency" == msg1

        # Invalid order number format
        msg2 = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "invalid_format",
            field="Order number",
            requirement="contain only letters, numbers, hyphens, and underscores",
        )
        assert (
            "Order number should contain only letters, numbers, hyphens, and underscores"
            == msg2
        )

        # Feature not available
        msg3 = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY,
            "feature_unavailable",
            feature="Abstract workflow",
        )
        assert "Abstract workflow is not yet implemented" == msg3

    def test_business_logic_validation_flow(self):
        """Test typical business logic validation with technical messages."""
        # Type validation
        msg1 = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "wrong_type",
            field="order_number",
            expected_type="str",
        )
        assert "order_number must be str" == msg1

        # Empty value validation
        msg2 = ValidationMessages.format_message(
            MessageType.TECHNICAL, "empty_value", field="lease_number"
        )
        assert "lease_number cannot be empty" == msg2

        # Enum validation
        msg3 = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "invalid_enum",
            field="agency",
            valid_options="AgencyType.NMSLO, AgencyType.BLM",
        )
        assert "agency must be one of AgencyType.NMSLO, AgencyType.BLM" == msg3

    def test_file_validation_messages(self):
        """Test file validation messages for both types."""
        # User-friendly file messages
        user_msg = ValidationMessages.format_message(
            MessageType.USER_FRIENDLY, "file_not_found", file_type="Excel"
        )
        assert "File not found: Please select an existing Excel file" == user_msg

        # Technical file messages
        tech_msg = ValidationMessages.format_message(
            MessageType.TECHNICAL,
            "file_not_found_technical",
            file_path="/path/to/file.xlsx",
        )
        assert "File not found: /path/to/file.xlsx" == tech_msg

    def test_message_consistency_patterns(self):
        """Test that message patterns are consistent within each type."""
        # USER_FRIENDLY messages should be instructional and polite
        user_templates = ValidationMessages.get_available_templates(
            MessageType.USER_FRIENDLY
        )

        # Many should start with "Please" for politeness
        please_templates = [
            template
            for template in user_templates.values()
            if template.startswith("Please")
        ]
        assert len(please_templates) >= 2  # At least some polite messages

        # TECHNICAL messages should be concise and factual
        tech_templates = ValidationMessages.get_available_templates(
            MessageType.TECHNICAL
        )

        # Many should follow "{field} must be/cannot be" pattern
        field_templates = [
            template for template in tech_templates.values() if "{field}" in template
        ]
        assert len(field_templates) >= 5  # Most technical messages reference fields
