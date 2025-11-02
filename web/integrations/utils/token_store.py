"""Helpers to load/save per-user OAuth tokens (Dropbox, Basecamp)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TypedDict

from django.apps import apps

from .crypto import decrypt_text, encrypt_text


class OAuthTokens(TypedDict, total=False):
    """Typed mapping for persisted OAuth token fields."""

    access_token: str
    refresh_token: str
    expires_at: Optional[datetime]
    account_id: str
    account_name: Optional[str]  # Basecamp includes account name
    scope: str
    token_type: str


def _get_dropbox_account_model():
    """Return the `integrations.DropboxAccount` model class lazily."""
    return apps.get_model("integrations", "DropboxAccount")


def _get_basecamp_account_model():
    """Return the `integrations.BasecampAccount` model class lazily."""
    return apps.get_model("integrations", "BasecampAccount")


def _get_account_model(provider: str):
    """Return the appropriate account model based on provider."""
    if provider == "basecamp":
        return _get_basecamp_account_model()
    elif provider == "dropbox":
        return _get_dropbox_account_model()
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_tokens_for_user(user, provider: str = "dropbox") -> Optional[OAuthTokens]:
    """Return OAuth tokens for a user or None if not connected.

    Args:
        user: Django user instance
        provider: Integration provider ('dropbox' or 'basecamp')

    Returns:
        OAuthTokens dict or None if not connected
    """
    if not user or not getattr(user, "pk", None):
        return None
    acct_model = _get_account_model(provider)
    try:
        acct = acct_model.objects.get(user=user)
    except acct_model.DoesNotExist:  # type: ignore[attr-defined]
        return None

    tokens = OAuthTokens(
        access_token=acct.access_token,
        refresh_token=decrypt_text(acct.refresh_token_encrypted),
        expires_at=acct.expires_at,
        account_id=acct.account_id,
        scope=acct.scope,
        token_type=acct.token_type,
    )
    # Basecamp includes account_name
    if provider == "basecamp" and hasattr(acct, "account_name"):
        tokens["account_name"] = acct.account_name
    return tokens


def save_tokens_for_user(user, tokens: OAuthTokens, provider: str = "dropbox"):
    """Create/update the user's account with provided tokens.

    Args:
        user: Django user instance
        tokens: OAuthTokens dict with token data
        provider: Integration provider ('dropbox' or 'basecamp')

    Returns:
        Account model instance (DropboxAccount or BasecampAccount)
    """
    if not user or not getattr(user, "pk", None):
        raise ValueError("user is required")
    acct_model = _get_account_model(provider)
    defaults = {"account_id": tokens.get("account_id", "")}
    # Basecamp requires account_name
    if provider == "basecamp" and tokens.get("account_name"):
        defaults["account_name"] = tokens["account_name"]
    acct, _ = acct_model.objects.get_or_create(user=user, defaults=defaults)

    # Update fields
    if tokens.get("account_id"):
        acct.account_id = tokens["account_id"]
    if tokens.get("access_token"):
        acct.access_token = tokens["access_token"]
    if tokens.get("refresh_token"):
        acct.refresh_token_encrypted = encrypt_text(tokens["refresh_token"])
    acct.expires_at = tokens.get("expires_at")
    acct.scope = tokens.get("scope", "")
    acct.token_type = tokens.get("token_type", "")

    # Basecamp-specific field
    if provider == "basecamp" and tokens.get("account_name"):
        acct.account_name = tokens["account_name"]
    
    # T026-T027: Dropbox-specific fields
    if provider == "dropbox":
        if "display_name" in tokens:
            acct.display_name = tokens["display_name"]
        if "email" in tokens:
            acct.email = tokens["email"]

    # Build update_fields list
    update_fields = [
        "account_id",
        "access_token",
        "refresh_token_encrypted",
        "expires_at",
        "scope",
        "token_type",
        "updated_at",
    ]
    if provider == "basecamp":
        update_fields.append("account_name")
    if provider == "dropbox":
        update_fields.extend(["display_name", "email"])

    acct.save(update_fields=update_fields)

    # Invalidate cached status for this user and provider (must match IntegrationStatusService key format)
    from integrations.status.cache import default_cache

    cache_key = f"integration_status:{provider}:{user.pk}"
    default_cache.delete(cache_key)

    return acct
