"""
Validation Protocols and Base Classes

Defines the core validation interfaces and abstract base classes for the
centralized validation service architecture.
"""

from typing import Protocol, Tuple
from abc import ABC, abstractmethod


class Validator(Protocol):
    """Protocol for all validators - enables duck typing and extension."""

    def validate(self, data) -> Tuple[bool, str]:
        """
        Validate data and return (is_valid, error_message).

        Args:
            data: The data to validate (type varies by validator)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, error_msg) if invalid
        """
        ...


class ValidatorBase(ABC):
    """
    Optional abstract base class for validators that need shared functionality.

    Provides common patterns and utilities for validator implementations.
    Validators can implement the Validator protocol directly or extend this base.
    """

    @abstractmethod
    def validate(self, data) -> Tuple[bool, str]:
        """
        Validate data and return (is_valid, error_message).

        Args:
            data: The data to validate (type varies by validator)

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, error_msg) if invalid
        """
        raise NotImplementedError("Subclasses must implement validate method")

    def validate_required_field(
        self, value, field_name: str, expected_type: type
    ) -> Tuple[bool, str]:
        """
        Helper method for common field validation patterns.

        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            expected_type: Expected type for the value

        Returns:
            Tuple[bool, str]: (True, "") if valid, (False, error_msg) if invalid
        """
        if not isinstance(value, expected_type):
            return False, f"{field_name} must be a {expected_type.__name__}"

        # Check for empty strings if it's a string type
        if hasattr(value, "strip") and not value.strip():
            return False, f"{field_name} cannot be empty"

        return True, ""
