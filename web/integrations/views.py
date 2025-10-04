"""Dropbox OAuth views: connect, callback, disconnect."""

# pylint: disable=no-member

import dropbox  # third-party
from django.conf import settings  # third-party
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme  # noqa: F401
from django.views.decorators.http import require_GET

from core.utils.redirects import redirect_back, store_next
from integrations.status.service import IntegrationStatusService

from .models import DropboxAccount  # local
from .utils.token_store import get_tokens_for_user, save_tokens_for_user


@login_required
@require_GET
@store_next()
def dropbox_connect(request: HttpRequest) -> HttpResponse:
    """Start Dropbox OAuth by redirecting to the consent URL."""
    auth_flow = dropbox.oauth.DropboxOAuth2Flow(
        consumer_key=settings.DROPBOX_APP_KEY,
        consumer_secret=settings.DROPBOX_APP_SECRET,
        redirect_uri=settings.DROPBOX_REDIRECT_URI,
        session=request.session,
        csrf_token_session_key="dropbox-auth-csrf-token",
        token_access_type="offline",
    )
    authorize_url = auth_flow.start()
    return HttpResponseRedirect(authorize_url)


@login_required
@require_GET
@redirect_back(default_name="__root__")
def dropbox_callback(request: HttpRequest) -> HttpResponse:
    """Finish OAuth: validate state, exchange code, and persist tokens."""
    auth_flow = dropbox.oauth.DropboxOAuth2Flow(
        consumer_key=settings.DROPBOX_APP_KEY,
        consumer_secret=settings.DROPBOX_APP_SECRET,
        redirect_uri=settings.DROPBOX_REDIRECT_URI,
        session=request.session,
        csrf_token_session_key="dropbox-auth-csrf-token",
        token_access_type="offline",
    )
    try:
        result = auth_flow.finish(request.GET)
    except Exception:
        return HttpResponseBadRequest("Invalid OAuth response")
    tokens = {
        "access_token": result.access_token,
        "refresh_token": getattr(result, "refresh_token", ""),
        "expires_at": getattr(result, "expires_at", None),
        "account_id": getattr(result, "account_id", ""),
        "scope": getattr(result, "scope", ""),
        "token_type": getattr(result, "token_type", ""),
    }
    save_tokens_for_user(request.user, tokens)
    # Safe redirect to next URL or dashboard
    return HttpResponse("Dropbox connected.")


@login_required
@require_GET
@redirect_back()
def dropbox_disconnect(request: HttpRequest) -> HttpResponse:
    """Remove the current user's stored Dropbox credentials."""
    DropboxAccount.objects.filter(user=request.user).delete()
    # Prefer explicit next param; otherwise fall back to safe Referer
    return HttpResponse("Dropbox disconnected.")


@login_required
@require_GET
def index(request: HttpRequest) -> HttpResponse:
    """Simple page with links to connect/disconnect Dropbox."""
    return render(request, "integrations/index.html")


@login_required
@require_GET
def dropbox_me(request: HttpRequest) -> HttpResponse:
    """Optional smoke test: return the connected Dropbox account name."""
    tokens = get_tokens_for_user(request.user)
    if not tokens or not tokens.get("access_token"):
        return HttpResponseBadRequest("Dropbox not connected")
    client = dropbox.Dropbox(oauth2_access_token=tokens["access_token"])  # simple test
    account = client.users_get_current_account()
    return HttpResponse(f"Connected as: {account.name.display_name}")


# Create your views here.


@login_required
@require_GET
def manage(request: HttpRequest) -> HttpResponse:
    """Simple page for users to manage integrations (disconnect Dropbox)."""
    service = IntegrationStatusService()
    statuses = {"dropbox": service.assess(request.user, "dropbox", force_refresh=True)}
    return render(request, "integrations/manage.html", {"statuses": statuses})
