"""API views for triggering Basecamp workflow creation from orders."""

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.workflows import WorkflowResultSerializer
from integrations.models import BasecampAccount
from orders.models import Order
from orders.services.workflow.executor import WorkflowExecutor

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_workflow(request, order_id):
    """
    Trigger Basecamp workflow creation for an order.

    Args:
        request: Django request with authenticated user
        order_id: Primary key of the Order

    Returns:
        Response with WorkflowResult:
        - 200 OK: Workflows created (full/partial success) or no applicable products
        - 404 Not Found: Order does not exist
        - 422 Unprocessable Entity: Basecamp not connected or configuration error
        - 500 Internal Server Error: Total failure (all products failed)
    """
    # 1. Validate order exists
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response(
            {
                "success": False,
                "error": "Order not found",
                "message": f"Order with ID {order_id} does not exist",
            },
            status=404,
        )

    # 2. Validate Basecamp connection
    if not BasecampAccount.objects.filter(
        user=request.user, access_token__isnull=False
    ).exists():
        return Response(
            {
                "success": False,
                "error": "Basecamp not connected",
                "message": "Basecamp integration is not connected. Please connect your Basecamp account.",
            },
            status=422,
        )

    # 3. Execute workflows
    # Executor catches all errors internally and returns WorkflowResult with details
    executor = WorkflowExecutor()
    result = executor.execute(order_id=order.id, user_id=request.user.id)

    # 4. Serialize and return result
    # Return 200 OK for all cases:
    # - Complete success (all products succeeded)
    # - Partial success (some products succeeded, some failed)
    # - No applicable products (no workflows to create)
    # - Complete failure (all products failed) - still 200 with error details in response
    serializer = WorkflowResultSerializer(result)
    return Response(serializer.data, status=200)
