"""
Thread-local storage for the current request user.

Used by signal handlers to discover which user initiated a model save
so background tasks can run under that user's cloud auth context.
"""

from __future__ import annotations

import threading
from typing import Optional


_state = threading.local()


def set_current_user(user) -> None:
    _state.user = user


def get_current_user_id() -> Optional[int]:
    user = getattr(_state, "user", None)
    try:
        return (
            int(user.id) if user and getattr(user, "is_authenticated", False) else None
        )
    except Exception:
        return None


def clear_current_user() -> None:
    if hasattr(_state, "user"):
        delattr(_state, "user")
