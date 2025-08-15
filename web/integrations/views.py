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
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils.http import url_has_allowed_host_and_scheme

from .models import DropboxAccount  # local
from .utils.token_store import save_tokens_for_user, get_tokens_for_user
from .cloud.factory import get_cloud_service


@login_required
@require_GET
def dropbox_connect(request: HttpRequest) -> HttpResponse:
    """Start Dropbox OAuth by redirecting to the consent URL."""
    # Store optional next URL to redirect back after OAuth
    next_url = request.GET.get("next")
    if next_url:
        request.session["post_oauth_next"] = next_url
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
    next_url = request.session.pop("post_oauth_next", None)
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return HttpResponseRedirect(next_url)
    return HttpResponseRedirect("/")


@login_required
@require_GET
def dropbox_disconnect(request: HttpRequest) -> HttpResponse:
    """Remove the current user's stored Dropbox credentials."""
    DropboxAccount.objects.filter(user=request.user).delete()
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
