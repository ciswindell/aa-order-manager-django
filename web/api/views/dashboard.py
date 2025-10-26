"""Dashboard views."""

from api.serializers.auth import UserSerializer
from api.serializers.integrations import IntegrationStatusSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from integrations.status.service import IntegrationStatusService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """Return dashboard data: user info, integration statuses, and stats."""
    user = request.user
    service = IntegrationStatusService()

    # Get integration statuses
    integration_statuses = []
    for provider in ["dropbox", "basecamp"]:
        try:
            status = service.assess(user, provider)
            integration_statuses.append(status)
        except ValueError:
            # Skip unknown providers
            pass

    # Serialize data
    user_data = UserSerializer(user).data
    statuses_data = IntegrationStatusSerializer(integration_statuses, many=True).data

    return Response(
        {
            "user": user_data,
            "integrations": statuses_data,
            "stats": {
                "total_orders": 0,  # Placeholder for future implementation
                "total_reports": 0,
                "total_leases": 0,
            },
        }
    )
