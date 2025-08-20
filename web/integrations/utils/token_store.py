"""Helpers to load/save per-user Dropbox OAuth tokens."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TypedDict
from django.apps import apps

from .crypto import encrypt_text, decrypt_text


class OAuthTokens(TypedDict, total=False):
    """Typed mapping for persisted Dropbox OAuth token fields."""

    access_token: str
    refresh_token: str
    expires_at: Optional[datetime]
    account_id: str
    scope: str
    token_type: str


def _get_dropbox_account_model():
    """Return the `integrations.DropboxAccount` model class lazily."""
    return apps.get_model("integrations", "DropboxAccount")


def get_tokens_for_user(user) -> Optional[OAuthTokens]:
    """Return OAuth tokens for a user or None if not connected."""
    if not user or not getattr(user, "pk", None):
        return None
    acct_model = _get_dropbox_account_model()
    try:
        acct = acct_model.objects.get(user=user)
    except acct_model.DoesNotExist:  # type: ignore[attr-defined]
        return None
    return OAuthTokens(
        access_token=acct.access_token,
        refresh_token=decrypt_text(acct.refresh_token_encrypted),
        expires_at=acct.expires_at,
        account_id=acct.account_id,
        scope=acct.scope,
        token_type=acct.token_type,
    )


def save_tokens_for_user(user, tokens: OAuthTokens):
    """Create/update the user's DropboxAccount with provided tokens."""
    if not user or not getattr(user, "pk", None):
        raise ValueError("user is required")
    acct_model = _get_dropbox_account_model()
    acct, _ = acct_model.objects.get_or_create(
        user=user, defaults={"account_id": tokens.get("account_id", "")}
    )
    if tokens.get("account_id"):
        acct.account_id = tokens["account_id"]
    if tokens.get("access_token"):
        acct.access_token = tokens["access_token"]
    if tokens.get("refresh_token"):
        acct.refresh_token_encrypted = encrypt_text(tokens["refresh_token"])
    acct.expires_at = tokens.get("expires_at")
    acct.scope = tokens.get("scope", "")
    acct.token_type = tokens.get("token_type", "")
    acct.save(
        update_fields=[
            "account_id",
            "access_token",
            "refresh_token_encrypted",
            "expires_at",
            "scope",
            "token_type",
            "updated_at",
        ]
    )
    return acct
