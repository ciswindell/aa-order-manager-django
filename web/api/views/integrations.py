"""Integration views."""

import dropbox
from api.serializers.integrations import IntegrationStatusSerializer
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from integrations.models import DropboxAccount
from integrations.status.service import IntegrationStatusService


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

    serializer = IntegrationStatusSerializer(integration_statuses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def connect_dropbox(request):
    """Start Dropbox OAuth flow and return authorization URL."""
    try:
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
@permission_classes([IsAdminUser])
def disconnect_dropbox(request):
    """Disconnect Dropbox by removing stored credentials."""
    try:
        deleted_count, _ = DropboxAccount.objects.filter(user=request.user).delete()
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
