from django.shortcuts import render  # pylint: disable=import-error
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import dropbox

from integrations.utils.token_store import (
    get_tokens_for_user,
)  # pylint: disable=import-error
from integrations.models import DropboxAccount  # pylint: disable=import-error

# Create your views here.


@login_required
def dashboard(request):
    """Dashboard view - requires login."""
    # Compute Dropbox connection status
    dropbox_tokens = get_tokens_for_user(request.user)
    dropbox_connected = bool(dropbox_tokens and dropbox_tokens.get("access_token"))
    dropbox_account_name = None
    dropbox_account_id = None
    dropbox_email = None
    dropbox_account_type = None
    dropbox_space_used = None
    dropbox_space_allocated = None
    dropbox_token_expires_at = None
    dropbox_token_expires_in_minutes = None
    dropbox_has_refresh_token = False
    dropbox_scope = None
    dropbox_token_type = None
    dropbox_last_updated = None
    dropbox_authenticated = False
    # CTA/problem indicators for background task reliability
    dropbox_blocking_problem = False
    dropbox_blocking_reason = None
    dropbox_cta_label = None
    dropbox_cta_url = None
    if dropbox_connected:
        dropbox_account_id = dropbox_tokens.get("account_id")
        dropbox_scope = dropbox_tokens.get("scope")
        dropbox_token_type = dropbox_tokens.get("token_type")
        dropbox_has_refresh_token = bool(dropbox_tokens.get("refresh_token"))
        dropbox_token_expires_at = dropbox_tokens.get("expires_at")
        if dropbox_token_expires_at:
            try:
                delta = dropbox_token_expires_at - timezone.now()
                dropbox_token_expires_in_minutes = int(delta.total_seconds() // 60)
            except Exception:  # pragma: no cover
                dropbox_token_expires_in_minutes = None
        # Last updated timestamp from model
        try:
            acct_row = DropboxAccount.objects.get(user=request.user)
            dropbox_last_updated = acct_row.updated_at
        except DropboxAccount.DoesNotExist:
            dropbox_last_updated = None
        # Live account info (best-effort)
        try:
            # Build client with refresh support when available
            kwargs = {"oauth2_access_token": dropbox_tokens["access_token"]}  # type: ignore[index]
            refresh_token = dropbox_tokens.get("refresh_token")
            if (
                refresh_token
                and settings.DROPBOX_APP_KEY
                and settings.DROPBOX_APP_SECRET
            ):
                kwargs.update(
                    {
                        "oauth2_refresh_token": refresh_token,
                        "app_key": settings.DROPBOX_APP_KEY,
                        "app_secret": settings.DROPBOX_APP_SECRET,
                    }
                )
            client = dropbox.Dropbox(**kwargs)
            acct = client.users_get_current_account()
            dropbox_authenticated = True
            dropbox_account_name = getattr(
                getattr(acct, "name", None), "display_name", None
            )
            dropbox_email = getattr(acct, "email", None)
            at = getattr(acct, "account_type", None)
            # Robustly determine human-friendly account type
            if at is not None:
                try:
                    if hasattr(at, "is_basic") and at.is_basic():
                        dropbox_account_type = "basic"
                    elif hasattr(at, "is_business") and at.is_business():
                        dropbox_account_type = "business"
                    elif hasattr(at, "is_pro") and at.is_pro():
                        dropbox_account_type = "pro"
                    else:
                        dropbox_account_type = getattr(at, "tag", None)
                except Exception:  # pragma: no cover
                    dropbox_account_type = getattr(at, "tag", None)
            # Space usage (best-effort; may not be available for all accounts)
            try:
                usage = client.users_get_space_usage()
                dropbox_space_used = getattr(usage, "used", None)
                alloc = getattr(usage, "allocation", None)
                if alloc is not None:
                    # Handle union: individual/team allocations
                    if hasattr(alloc, "is_individual") and alloc.is_individual():
                        ind = alloc.get_individual()
                        dropbox_space_allocated = getattr(ind, "allocated", None)
                    elif hasattr(alloc, "is_team") and alloc.is_team():
                        team = alloc.get_team()
                        dropbox_space_allocated = getattr(team, "allocated", None)
                    else:
                        dropbox_space_allocated = getattr(alloc, "allocated", None)
            except Exception:  # pragma: no cover
                dropbox_space_used = None
                dropbox_space_allocated = None
        except Exception:  # pragma: no cover
            dropbox_account_name = dropbox_account_name or None

        # Determine if background tasks are at risk and require user action
        if not dropbox_authenticated:
            # Immediate failure risk: tokens invalid/expired
            dropbox_blocking_problem = True
            dropbox_blocking_reason = "Dropbox access token is invalid or expired. Background tasks will fail until you reconnect."
            dropbox_cta_label = "Reconnect Dropbox"
            dropbox_cta_url = "/integrations/dropbox/connect/"
        elif not dropbox_has_refresh_token:
            # Future failure risk: token will expire without refresh capability
            dropbox_blocking_problem = True
            dropbox_blocking_reason = "Dropbox refresh token is missing. When the current token expires, background tasks will fail. Reconnect to grant offline access."
            dropbox_cta_label = "Reconnect Dropbox"
            dropbox_cta_url = "/integrations/dropbox/connect/"
    else:
        # Not connected at all ⇒ definite failure
        dropbox_blocking_problem = True
        dropbox_blocking_reason = "Dropbox is not connected. Background tasks cannot access Dropbox until you connect."
        dropbox_cta_label = "Connect Dropbox"
        dropbox_cta_url = "/integrations/dropbox/connect/"

    # Check for Dropbox misconfiguration (staff only)
    dropbox_misconfigured = False
    if request.user.is_staff:
        dropbox_misconfigured = not (
            settings.DROPBOX_APP_KEY and settings.DROPBOX_APP_SECRET
        )
        if dropbox_misconfigured:
            # Environment misconfiguration is a blocking problem for everyone
            dropbox_blocking_problem = True
            dropbox_blocking_reason = "Dropbox app credentials are missing on the server. Background tasks cannot authenticate until this is fixed."
            dropbox_cta_label = "View setup instructions"
            dropbox_cta_url = (
                "https://www.dropbox.com/developers/apps"  # informational only
            )

    context = {
        "user": request.user,
        "is_staff": request.user.is_staff,
        "dropbox_connected": dropbox_connected,
        "dropbox_authenticated": dropbox_authenticated,
        "dropbox_misconfigured": dropbox_misconfigured,
        "dropbox_blocking_problem": dropbox_blocking_problem,
        "dropbox_blocking_reason": dropbox_blocking_reason,
        "dropbox_cta_label": dropbox_cta_label,
        "dropbox_cta_url": dropbox_cta_url,
        "dropbox_account_name": dropbox_account_name,
        "dropbox_account_id": dropbox_account_id,
        "dropbox_email": dropbox_email,
        "dropbox_account_type": dropbox_account_type,
        "dropbox_space_used": dropbox_space_used,
        "dropbox_space_allocated": dropbox_space_allocated,
        "dropbox_token_expires_at": dropbox_token_expires_at,
        "dropbox_token_expires_in_minutes": dropbox_token_expires_in_minutes,
        "dropbox_has_refresh_token": dropbox_has_refresh_token,
        "dropbox_scope": dropbox_scope,
        "dropbox_token_type": dropbox_token_type,
        "dropbox_last_updated": dropbox_last_updated,
    }
    return render(request, "core/dashboard.html", context)
