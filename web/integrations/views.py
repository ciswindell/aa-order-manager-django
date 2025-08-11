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

from .models import DropboxAccount  # local
from .utils.token_store import save_tokens_for_user, get_tokens_for_user
from .cloud.factory import get_cloud_service


@login_required
@require_GET
def dropbox_connect(request: HttpRequest) -> HttpResponse:
    """Start Dropbox OAuth by redirecting to the consent URL."""
    auth_flow = dropbox.oauth.DropboxOAuth2Flow(
        consumer_key=settings.DROPBOX_APP_KEY,
        consumer_secret=settings.DROPBOX_APP_SECRET,
        redirect_uri=settings.DROPBOX_REDIRECT_URI,
        session=request.session,
        csrf_token_session_key="dropbox-auth-csrf-token",
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
    return HttpResponse("Dropbox connected.")


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


@login_required
@require_GET
def dropbox_list(request: HttpRequest) -> JsonResponse:
    """List directories and files via OAuth-bound service.

    Dev-only: remove this endpoint before production.
    """
    path = request.GET.get("path", "/")
    service = get_cloud_service("dropbox", user=request.user)
    service.authenticate()
    dirs = [d.__dict__ for d in service.list_directories(path)]
    files = [f.__dict__ for f in service.list_files(path)]
    return JsonResponse({"path": path, "directories": dirs, "files": files})


# Create your views here.
