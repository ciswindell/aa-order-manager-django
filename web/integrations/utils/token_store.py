"""Helpers to load/save per-user Dropbox OAuth tokens."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TypedDict

from django.contrib.auth import get_user_model

from ..models import DropboxAccount
from .crypto import encrypt_text, decrypt_text


class OAuthTokens(TypedDict, total=False):
    access_token: str
    refresh_token: str
    expires_at: Optional[datetime]
    account_id: str
    scope: str
    token_type: str


def get_tokens_for_user(user) -> Optional[OAuthTokens]:
    """Return OAuth tokens for a user or None if not connected."""
    if not user or not getattr(user, "pk", None):
        return None
    try:
        acct = DropboxAccount.objects.get(user=user)
    except DropboxAccount.DoesNotExist:
        return None
    return OAuthTokens(
        access_token=acct.access_token,
        refresh_token=decrypt_text(acct.refresh_token_encrypted),
        expires_at=acct.expires_at,
        account_id=acct.account_id,
        scope=acct.scope,
        token_type=acct.token_type,
    )


def save_tokens_for_user(user, tokens: OAuthTokens) -> DropboxAccount:
    """Create/update the user's DropboxAccount with provided tokens."""
    if not user or not getattr(user, "pk", None):
        raise ValueError("user is required")
    acct, _ = DropboxAccount.objects.get_or_create(
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
