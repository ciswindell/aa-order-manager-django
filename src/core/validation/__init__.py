"""
Validation Service Package

Centralized validation service providing protocol-based validation architecture
for the Order Manager application. Eliminates duplicate validation logic and
follows SOLID/DRY principles.

Usage:
    from src.core.validation import Validator, ValidatorBase
    from src.core.validation import FormDataValidator, ExcelFileValidator
"""

from .protocols import Validator, ValidatorBase
from .form_validators import FormDataValidator, BusinessRulesValidator
from .file_validators import ExcelFileValidator, OrderFormStructureValidator
from .model_validators import OrderDataValidator, OrderItemDataValidator
from .workflow_validators import WorkflowInputValidator
from .messages import ValidationMessages, MessageType

__all__ = [
    "Validator",
    "ValidatorBase",
    "FormDataValidator",
    "ExcelFileValidator",
    "OrderFormStructureValidator",
    "OrderDataValidator",
    "OrderItemDataValidator",
    "WorkflowInputValidator",
    "BusinessRulesValidator",
    "ValidationMessages",
    "MessageType",
]
