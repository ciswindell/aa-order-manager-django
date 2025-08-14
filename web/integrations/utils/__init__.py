"""Utility package for the `integrations` app.

Lazily exposes selected utilities to avoid importing Django models during
test discovery when this package is imported under a different module path.
"""

from typing import Any

__all__ = ["get_agency_storage_config", "AgencyStorageConfigError"]


def __getattr__(name: str) -> Any:
    if name in {"get_agency_storage_config", "AgencyStorageConfigError"}:
        from .agency_config import (
            get_agency_storage_config as _get_agency_storage_config,
            AgencyStorageConfigError as _AgencyStorageConfigError,
        )

        globals().update(
            {
                "get_agency_storage_config": _get_agency_storage_config,
                "AgencyStorageConfigError": _AgencyStorageConfigError,
            }
        )
        return globals()[name]
    raise AttributeError(name)
