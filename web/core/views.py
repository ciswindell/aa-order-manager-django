from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
import dropbox

from integrations.utils.token_store import get_tokens_for_user
from integrations.models import DropboxAccount

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
            client = dropbox.Dropbox(oauth2_access_token=dropbox_tokens["access_token"])  # type: ignore[index]
            acct = client.users_get_current_account()
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

    # Check for Dropbox misconfiguration (staff only)
    dropbox_misconfigured = False
    if request.user.is_staff:
        dropbox_misconfigured = not (
            settings.DROPBOX_APP_KEY and settings.DROPBOX_APP_SECRET
        )

    context = {
        "user": request.user,
        "is_staff": request.user.is_staff,
        "dropbox_connected": dropbox_connected,
        "dropbox_misconfigured": dropbox_misconfigured,
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
