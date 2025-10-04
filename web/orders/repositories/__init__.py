"""
Repository layer for data access operations.

This package contains repository classes that handle all database operations,
following the repository pattern to separate data access from business logic.
"""

from .lease_repository import LeaseRepository

__all__ = ["LeaseRepository"]
