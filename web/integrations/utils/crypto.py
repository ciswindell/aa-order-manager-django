"""Minimal symmetric encryption helpers for storing refresh tokens."""

from __future__ import annotations

import base64
import hashlib
from typing import Optional

from django.conf import settings

try:
    from cryptography.fernet import Fernet  # pylint: disable=import-error
except Exception:  # pragma: no cover
    Fernet = None  # type: ignore


def _get_key() -> Optional[bytes]:
    """Return a Fernet key from DROPBOX_CRYPTO_KEY or a SECRET_KEY-derived value."""
    key = getattr(settings, "DROPBOX_CRYPTO_KEY", None)
    if key:
        return key.encode("utf-8")

    # Derive a stable key from SECRET_KEY (dev convenience)
    secret = getattr(settings, "SECRET_KEY", "")
    if not secret:
        return None
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(plain_text: str) -> str:
    """Encrypt and return text; fall back to plaintext if crypto is unavailable."""
    if not Fernet:
        return plain_text
    key = _get_key()
    if not key:
        return plain_text
    return Fernet(key).encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_text(cipher_text: str) -> str:
    """Decrypt and return text; fall back to empty/input if decryption fails."""
    if not cipher_text:
        return ""
    if not Fernet:
        return cipher_text
    key = _get_key()
    if not key:
        return cipher_text
    try:
        return Fernet(key).decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""
