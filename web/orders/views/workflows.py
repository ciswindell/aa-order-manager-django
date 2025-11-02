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
    executor = WorkflowExecutor()
    try:
        result = executor.execute(order_id=order.id, user_id=request.user.id)
    except ValueError as e:
        # Configuration errors (missing project IDs)
        logger.warning(
            "Workflow execution configuration error | order_id=%s | user_id=%s | error=%s",
            order.id,
            request.user.id,
            str(e),
        )
        return Response(
            {"success": False, "error": "Configuration error", "message": str(e)},
            status=422,
        )
    except Exception as e:
        # Total failure (all products failed)
        logger.error(
            "Workflow execution failed | order_id=%s | user_id=%s | error=%s",
            order.id,
            request.user.id,
            str(e),
            exc_info=True,
        )
        return Response(
            {
                "success": False,
                "error": "Workflow creation failed",
                "message": "Failed to create workflows. Please try again later.",
            },
            status=500,
        )

    # 4. Log and return result
    if result.success:
        logger.info(
            "Workflow creation succeeded | order_id=%s | user_id=%s | products=%s | count=%d",
            order.id,
            request.user.id,
            ", ".join(result.workflows_created),
            result.total_count,
        )
        if result.failed_products:
            logger.warning(
                "Workflow creation partial success | order_id=%s | user_id=%s | succeeded=%s | failed=%s",
                order.id,
                request.user.id,
                ", ".join(result.workflows_created),
                ", ".join(result.failed_products),
            )
    else:
        logger.warning(
            "Workflow creation returned no workflows | order_id=%s | user_id=%s",
            order.id,
            request.user.id,
        )

    serializer = WorkflowResultSerializer(result)
    return Response(serializer.data, status=200)
