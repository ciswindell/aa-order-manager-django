"""
Unit Tests for Validation Protocols and Base Classes

Tests for Validator protocol and ValidatorBase ABC including interface
compliance and shared functionality.
"""

import pytest
from typing import Tuple

from src.core.validation.protocols import Validator, ValidatorBase


class TestValidatorProtocol:
    """Test suite for Validator protocol interface."""

    def test_validator_protocol_interface(self):
        """Test that classes implementing Validator protocol have correct interface."""

        class MockValidator:
            """Mock validator implementing the protocol."""

            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        # Test that mock validator satisfies the protocol
        validator = MockValidator()
        assert hasattr(validator, "validate")
        assert callable(validator.validate)

        # Test return type
        result = validator.validate("test_data")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)

    def test_validator_protocol_duck_typing(self):
        """Test that protocol enables duck typing for any class with validate method."""

        class CustomValidator:
            """Custom validator that satisfies protocol without inheritance."""

            def validate(self, data) -> Tuple[bool, str]:
                if data == "valid":
                    return True, ""
                return False, "Invalid data"

        def process_with_validator(validator: Validator, data) -> Tuple[bool, str]:
            """Function that accepts any Validator protocol implementer."""
            return validator.validate(data)

        # Test duck typing works
        custom_validator = CustomValidator()

        # Valid case
        is_valid, error = process_with_validator(custom_validator, "valid")
        assert is_valid is True
        assert error == ""

        # Invalid case
        is_valid, error = process_with_validator(custom_validator, "invalid")
        assert is_valid is False
        assert error == "Invalid data"


class TestValidatorBase:
    """Test suite for ValidatorBase abstract base class."""

    def test_validator_base_is_abstract(self):
        """Test that ValidatorBase cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ValidatorBase()

    def test_validator_base_requires_validate_implementation(self):
        """Test that subclasses must implement validate method."""

        class IncompleteValidator(ValidatorBase):
            """Validator missing validate implementation."""

            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteValidator()

    def test_validator_base_with_complete_implementation(self):
        """Test ValidatorBase with complete validate implementation."""

        class CompleteValidator(ValidatorBase):
            """Complete validator implementation."""

            def validate(self, data) -> Tuple[bool, str]:
                if isinstance(data, str) and data:
                    return True, ""
                return False, "Data must be non-empty string"

        # Should instantiate successfully
        validator = CompleteValidator()
        assert isinstance(validator, ValidatorBase)
        assert isinstance(validator, CompleteValidator)

        # Test validation works
        is_valid, error = validator.validate("test")
        assert is_valid is True
        assert error == ""

        is_valid, error = validator.validate("")
        assert is_valid is False
        assert error == "Data must be non-empty string"

    def test_validate_required_field_helper_with_valid_string(self):
        """Test validate_required_field helper with valid string input."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field(
            "test_value", "test_field", str
        )

        assert is_valid is True
        assert error == ""

    def test_validate_required_field_helper_with_empty_string(self):
        """Test validate_required_field helper with empty string."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field("", "test_field", str)

        assert is_valid is False
        assert error == "test_field cannot be empty"

    def test_validate_required_field_helper_with_whitespace_string(self):
        """Test validate_required_field helper with whitespace-only string."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field("   ", "test_field", str)

        assert is_valid is False
        assert error == "test_field cannot be empty"

    def test_validate_required_field_helper_with_wrong_type(self):
        """Test validate_required_field helper with wrong data type."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field(123, "test_field", str)

        assert is_valid is False
        assert error == "test_field must be a str"

    def test_validate_required_field_helper_with_valid_int(self):
        """Test validate_required_field helper with valid integer."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field(42, "test_field", int)

        assert is_valid is True
        assert error == ""

    def test_validate_required_field_helper_with_none_value(self):
        """Test validate_required_field helper with None value."""

        class TestValidator(ValidatorBase):
            def validate(self, data) -> Tuple[bool, str]:
                return True, ""

        validator = TestValidator()
        is_valid, error = validator.validate_required_field(None, "test_field", str)

        assert is_valid is False
        assert error == "test_field must be a str"


class TestValidatorIntegration:
    """Integration tests for protocol and base class interaction."""

    def test_validator_base_satisfies_protocol(self):
        """Test that ValidatorBase implementations satisfy Validator protocol."""

        class ConcreteValidator(ValidatorBase):
            """Concrete validator for testing."""

            def validate(self, data) -> Tuple[bool, str]:
                return self.validate_required_field(data, "data", str)

        def use_validator(validator: Validator, data) -> Tuple[bool, str]:
            """Function that uses Validator protocol."""
            return validator.validate(data)

        # ValidatorBase subclass should work with protocol
        concrete_validator = ConcreteValidator()

        # Test with valid data
        is_valid, error = use_validator(concrete_validator, "valid_data")
        assert is_valid is True
        assert error == ""

        # Test with invalid data
        is_valid, error = use_validator(concrete_validator, 123)
        assert is_valid is False
        assert error == "data must be a str"  # 123 is int, but we expect str

    def test_multiple_validator_implementations(self):
        """Test multiple different validator implementations working together."""

        class StringValidator(ValidatorBase):
            """Validates string data."""

            def validate(self, data) -> Tuple[bool, str]:
                return self.validate_required_field(data, "string_data", str)

        class NumberValidator(ValidatorBase):
            """Validates numeric data."""

            def validate(self, data) -> Tuple[bool, str]:
                if not isinstance(data, (int, float)):
                    return False, "Must be a number"
                if data < 0:
                    return False, "Must be positive"
                return True, ""

        def validate_multiple(
            validators: list[Validator], data_list: list
        ) -> list[Tuple[bool, str]]:
            """Validate multiple data items with corresponding validators."""
            results = []
            for validator, data in zip(validators, data_list):
                results.append(validator.validate(data))
            return results

        # Test with multiple validators
        validators = [StringValidator(), NumberValidator()]
        test_data = ["test_string", 42]

        results = validate_multiple(validators, test_data)

        # Both should be valid
        assert len(results) == 2
        assert results[0] == (True, "")
        assert results[1] == (True, "")

        # Test with invalid data
        invalid_data = ["", -5]
        invalid_results = validate_multiple(validators, invalid_data)

        assert invalid_results[0][0] is False  # Empty string
        assert invalid_results[1][0] is False  # Negative number
