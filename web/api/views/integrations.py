"""Integration views."""

import base64
import hashlib
import hmac
import json
import logging
import secrets

import dropbox
from api.serializers.integrations import IntegrationStatusSerializer
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from integrations.basecamp.config import get_basecamp_app_key, get_redirect_uri
from integrations.models import BasecampAccount, DropboxAccount
from integrations.status.service import IntegrationStatusService

logger = logging.getLogger(__name__)


def _sign_state(user_id: int, nonce: str) -> str:
    """Create a signed state parameter containing user ID and nonce."""
    payload = json.dumps({"user_id": user_id, "nonce": nonce})
    signature = hmac.new(
        settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).digest()
    signed = base64.urlsafe_b64encode(signature + payload.encode()).decode()
    return signed


def _verify_state(state: str) -> int | None:
    """Verify and extract user ID from signed state parameter."""
    try:
        decoded = base64.urlsafe_b64decode(state.encode())
        signature = decoded[:32]  # SHA256 is 32 bytes
        payload = decoded[32:]

        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(), payload, hashlib.sha256
        ).digest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        data = json.loads(payload.decode())
        return data.get("user_id")
    except Exception:
        return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_integration_status(request):
    """Get status for all configured integrations."""
    user = request.user
    service = IntegrationStatusService()

    integration_statuses = []
    for provider in ["dropbox", "basecamp"]:
        try:
            integration_status = service.assess(user, provider)
            integration_statuses.append(integration_status)
        except ValueError:
            # Skip unknown providers
            pass

    serializer = IntegrationStatusSerializer(
        integration_statuses, many=True, context={"request": request}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def connect_dropbox(request):
    """Start Dropbox OAuth flow and return authorization URL."""
    try:
        # Store user ID in session (separate from Dropbox SDK's state)
        request.session["dropbox_oauth_user_id"] = request.user.id

        auth_flow = dropbox.oauth.DropboxOAuth2Flow(
            consumer_key=settings.DROPBOX_APP_KEY,
            consumer_secret=settings.DROPBOX_APP_SECRET,
            redirect_uri=settings.DROPBOX_REDIRECT_URI,
            session=request.session,
            csrf_token_session_key="dropbox-auth-csrf-token",
            token_access_type="offline",
        )
        authorize_url = auth_flow.start()
        return Response({"authorize_url": authorize_url}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"Failed to initiate Dropbox OAuth: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def disconnect_dropbox(request):
    """Disconnect Dropbox by removing stored credentials."""
    from integrations.status.cache import default_cache

    try:
        deleted_count, _ = DropboxAccount.objects.filter(user=request.user).delete()

        # Invalidate cached status (must match IntegrationStatusService key format)
        cache_key = f"integration_status:dropbox:{request.user.pk}"
        default_cache.delete(cache_key)

        if deleted_count > 0:
            return Response(
                {"message": "Dropbox account disconnected successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "No Dropbox account was connected"},
                status=status.HTTP_200_OK,
            )
    except Exception as e:
        return Response(
            {"error": f"Failed to disconnect Dropbox: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def dropbox_callback(request):
    """Handle Dropbox OAuth callback - exchange code for tokens and store account."""
    from django.contrib.auth import get_user_model
    from django.shortcuts import redirect

    from integrations.utils.token_store import save_tokens_for_user

    try:
        # Use Dropbox SDK to finish OAuth and validate state
        auth_flow = dropbox.oauth.DropboxOAuth2Flow(
            consumer_key=settings.DROPBOX_APP_KEY,
            consumer_secret=settings.DROPBOX_APP_SECRET,
            redirect_uri=settings.DROPBOX_REDIRECT_URI,
            session=request.session,
            csrf_token_session_key="dropbox-auth-csrf-token",
            token_access_type="offline",
        )
        result = auth_flow.finish(request.GET)

        # Retrieve user ID from session
        user_id = request.session.get("dropbox_oauth_user_id")

        if not user_id:
            return redirect("http://localhost:3000/dashboard?error=session_expired")

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect("http://localhost:3000/dashboard?error=user_not_found")

        tokens = {
            "access_token": result.access_token,
            "refresh_token": getattr(result, "refresh_token", ""),
            "expires_at": getattr(result, "expires_at", None),
            "account_id": getattr(result, "account_id", ""),
            "scope": getattr(result, "scope", ""),
            "token_type": getattr(result, "token_type", ""),
        }
        save_tokens_for_user(user, tokens, provider="dropbox")

        # Clear the user ID from session
        if "dropbox_oauth_user_id" in request.session:
            del request.session["dropbox_oauth_user_id"]

        # Redirect to frontend dashboard
        return redirect("http://localhost:3000/dashboard?dropbox=connected")

    except Exception as e:
        logger.error(f"Dropbox callback exception: {e}", exc_info=True)
        return redirect("http://localhost:3000/dashboard?error=dropbox_failed")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def connect_basecamp(request):
    """Start Basecamp OAuth flow and return authorization URL."""
    user_id = request.user.id
    logger.info("Basecamp OAuth connect initiated | user_id=%s", user_id)

    try:
        # Check for existing account
        existing_account = BasecampAccount.objects.filter(user=request.user).first()
        if existing_account:
            logger.warning(
                "Basecamp OAuth connect blocked - account exists | user_id=%s | account_id=%s",
                user_id,
                existing_account.account_id,
            )
            return Response(
                {
                    "error": "account_already_connected",
                    "message": f"You already have a Basecamp account connected: {existing_account.account_name}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)
        request.session["basecamp_oauth_state"] = state
        # Store user ID separately in session
        request.session["basecamp_oauth_user_id"] = request.user.id

        # Build authorization URL
        authorization_url = (
            f"https://launchpad.37signals.com/authorization/new"
            f"?type=web_server"
            f"&client_id={get_basecamp_app_key()}"
            f"&redirect_uri={get_redirect_uri()}"
            f"&state={state}"
        )

        logger.info("Basecamp OAuth authorization URL generated | user_id=%s", user_id)
        return Response({"authorize_url": authorization_url}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(
            "Basecamp OAuth connect failed | user_id=%s | error=%s",
            user_id,
            str(e),
            exc_info=True,
        )
        return Response(
            {"error": f"Failed to initiate Basecamp OAuth: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def disconnect_basecamp(request):
    """Disconnect Basecamp by removing stored credentials."""
    from integrations.status.cache import default_cache

    user_id = request.user.id
    logger.info("Basecamp disconnect initiated | user_id=%s", user_id)

    try:
        deleted_count, _ = BasecampAccount.objects.filter(user=request.user).delete()

        # Invalidate cached status (must match IntegrationStatusService key format)
        cache_key = f"integration_status:basecamp:{request.user.pk}"
        default_cache.delete(cache_key)

        if deleted_count > 0:
            logger.info("Basecamp account disconnected | user_id=%s", user_id)
            return Response(
                {"message": "Basecamp account disconnected successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            logger.warning(
                "Basecamp disconnect - no account found | user_id=%s", user_id
            )
            return Response(
                {"message": "No Basecamp account was connected"},
                status=status.HTTP_200_OK,
            )
    except Exception as e:
        logger.error(
            "Basecamp disconnect failed | user_id=%s | error=%s",
            user_id,
            str(e),
            exc_info=True,
        )
        return Response(
            {"error": f"Failed to disconnect Basecamp: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def basecamp_callback(request):
    """Handle Basecamp OAuth callback - exchange code for tokens and store account."""
    from django.contrib.auth import get_user_model
    from django.shortcuts import redirect

    from integrations.basecamp.auth import BasecampOAuthAuth
    from integrations.utils.token_store import save_tokens_for_user

    code = request.GET.get("code")
    state = request.GET.get("state")
    error = request.GET.get("error")

    # Log callback attempt
    logger.info(
        "Basecamp OAuth callback received | has_code=%s | has_state=%s | has_error=%s",
        bool(code),
        bool(state),
        bool(error),
    )

    # OAuth error from Basecamp
    if error:
        error_description = request.GET.get("error_description", "Unknown error")
        logger.error(
            "Basecamp OAuth error | error=%s | description=%s", error, error_description
        )
        return redirect(
            "http://localhost:3000/dashboard?error=basecamp_authorization_failed"
        )

    # Validate required parameters (T036)
    if not code or not state:
        logger.error(
            "Basecamp OAuth callback missing parameters | code=%s | state=%s",
            bool(code),
            bool(state),
        )
        return redirect("http://localhost:3000/dashboard?error=invalid_callback")

    # Validate code format (alphanumeric, reasonable length)
    # Note: Basecamp codes are typically 8 characters
    if not code.isalnum() or len(code) < 6 or len(code) > 200:
        logger.error(
            "Basecamp OAuth callback invalid code format | code_length=%d", len(code)
        )
        return redirect("http://localhost:3000/dashboard?error=invalid_callback")

    # Validate state format (alphanumeric, reasonable length)
    if len(state) < 20 or len(state) > 200:
        logger.error(
            "Basecamp OAuth callback invalid state format | state_length=%d", len(state)
        )
        return redirect("http://localhost:3000/dashboard?error=invalid_state")

    # Validate state (CSRF protection)
    stored_state = request.session.get("basecamp_oauth_state")
    if not stored_state or stored_state != state:
        logger.error(
            "Basecamp OAuth state mismatch | stored=%s | received=%s",
            bool(stored_state),
            bool(state),
        )
        return redirect("http://localhost:3000/dashboard?error=invalid_state")

    # Retrieve user ID from session
    user_id = request.session.get("basecamp_oauth_user_id")
    if not user_id:
        logger.error("Basecamp OAuth callback session expired | no user_id")
        return redirect("http://localhost:3000/dashboard?error=session_expired")

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error("Basecamp OAuth callback user not found | user_id=%s", user_id)
        return redirect("http://localhost:3000/dashboard?error=user_not_found")

    # Clear session data
    if "basecamp_oauth_state" in request.session:
        del request.session["basecamp_oauth_state"]
    if "basecamp_oauth_user_id" in request.session:
        del request.session["basecamp_oauth_user_id"]

    try:
        # Exchange code for tokens
        logger.info("Basecamp OAuth token exchange starting | user_id=%s", user_id)
        token_response = BasecampOAuthAuth.exchange_code_for_tokens(
            code, get_redirect_uri()
        )
        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token", "")

        # Get account details
        logger.info("Basecamp OAuth fetching account details | user_id=%s", user_id)
        auth_details = BasecampOAuthAuth.get_authorization_details(access_token)
        accounts = auth_details.get("accounts", [])

        # T008: Detect multiple accounts
        if len(accounts) == 0:
            logger.error("Basecamp OAuth no accounts found | user_id=%s", user_id)
            return Response(
                {"error": "No Basecamp accounts found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif len(accounts) == 1:
            # T036-T037: Auto-select single account (existing behavior)
            account = accounts[0]
            account_id = str(account.get("id"))
            # T046: Truncate account name to 255 chars
            account_name = account.get("name", "Unknown")[:255]

            # Save tokens
            logger.info(
                "Basecamp OAuth saving tokens | user_id=%s | account_id=%s | account_name=%s",
                user_id,
                account_id,
                account_name,
            )
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "account_id": account_id,
                "account_name": account_name,
                "expires_at": None,
                "scope": "",
                "token_type": "Bearer",
            }

            save_tokens_for_user(user, tokens, provider="basecamp")

            # T038: Log auto-connected single account
            logger.info(
                "Basecamp auto-connected | user_id=%s | account_id=%s | account_name=%s",
                user_id,
                account_id,
                account_name,
            )
            # Redirect to frontend dashboard
            return redirect("http://localhost:3000/dashboard?basecamp=connected")

        else:  # len(accounts) > 1
            # T013: Truncate to 20 accounts if needed
            if len(accounts) > 20:
                logger.warning(
                    "User has %d Basecamp accounts, truncating to 20 | user_id=%s",
                    len(accounts),
                    user_id,
                )
                accounts = accounts[:20]

            # T009: Store pending accounts in session (T046: truncate names to 255 chars)
            request.session["basecamp_pending_accounts"] = [
                {"id": str(acc["id"]), "name": acc["name"][:255]} for acc in accounts
            ]

            # T010: Store pending tokens in session
            request.session["basecamp_pending_tokens"] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

            # T011: Set 15-minute session expiry
            request.session.set_expiry(900)  # 15 minutes

            # T014: Log selection flow initiated
            logger.info(
                "Basecamp account selection initiated | user_id=%s | accounts_count=%d",
                user_id,
                len(accounts),
            )

            # T012: Redirect to selection page
            return redirect("http://localhost:3000/basecamp/select-account")

    except Exception as e:
        logger.error(
            "Basecamp OAuth callback exception | user_id=%s | error=%s",
            user_id,
            str(e),
            exc_info=True,
        )
        return redirect("http://localhost:3000/dashboard?error=basecamp_failed")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_accounts(request):
    """Retrieve pending Basecamp accounts from session for account selection."""
    # T016: Check session expiry
    pending_accounts = request.session.get("basecamp_pending_accounts")

    if not pending_accounts:
        # T017: Log session expiry
        logger.warning(
            "Basecamp pending accounts session expired | user_id=%s", request.user.id
        )
        return Response(
            {
                "error": "Session expired or invalid",
                "action": "restart_oauth",
                "message": "Your session has expired. Please connect again.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # T017: Log successful retrieval
    logger.info(
        "Basecamp pending accounts retrieved | user_id=%s | accounts_count=%d",
        request.user.id,
        len(pending_accounts),
    )

    return Response({"accounts": pending_accounts})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def select_basecamp_account(request):
    """Complete Basecamp OAuth with user-selected account."""
    from integrations.utils.token_store import save_tokens_for_user

    # T019: Validate account_id is required
    account_id = request.data.get("account_id")

    if not account_id:
        return Response(
            {"error": "Missing required field", "detail": "account_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # T020: Retrieve and validate session data
    pending_accounts = request.session.get("basecamp_pending_accounts", [])
    pending_tokens = request.session.get("basecamp_pending_tokens", {})

    if not pending_accounts or not pending_tokens:
        # T024: Log session expiry
        logger.warning(
            "Basecamp account selection failed - session expired | user_id=%s",
            request.user.id,
        )
        return Response(
            {
                "error": "Session expired or invalid",
                "action": "restart_oauth",
                "message": "Your session has expired. Please connect again.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # T021: Validate selected account against pending list
    selected = next((acc for acc in pending_accounts if acc["id"] == account_id), None)

    if not selected:
        # T024: Log invalid selection
        logger.error(
            "Basecamp account selection failed - invalid account | user_id=%s | selected_id=%s | pending_count=%d",
            request.user.id,
            account_id,
            len(pending_accounts),
        )
        return Response(
            {
                "error": "Invalid account selection",
                "action": "choose_again",
                "message": "The selected account is not in your authorized list",
                "detail": f"Account ID '{account_id}' not found in pending accounts",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # T022: Save tokens with selected account
    tokens = {
        "access_token": pending_tokens["access_token"],
        "refresh_token": pending_tokens["refresh_token"],
        "account_id": str(selected["id"]),
        "account_name": selected["name"],
        "expires_at": None,
        "scope": "",
        "token_type": "Bearer",
    }

    save_tokens_for_user(request.user, tokens, provider="basecamp")

    # T023: Clear session data
    del request.session["basecamp_pending_accounts"]
    del request.session["basecamp_pending_tokens"]

    # T024: Log successful selection
    logger.info(
        "Basecamp account selected and connected | user_id=%s | account_id=%s | account_name=%s",
        request.user.id,
        selected["id"],
        selected["name"],
    )

    return Response({"message": "Account connected successfully", "account": selected})
