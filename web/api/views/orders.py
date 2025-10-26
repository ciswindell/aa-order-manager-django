"""Order views."""

from api.serializers.orders import OrderSerializer
from orders.models import Order
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order CRUD operations."""

    queryset = Order.objects.all().prefetch_related("reports").order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Set created_by field from request.user."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set updated_by field from request.user."""
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Prevent deletion if order has reports."""
        instance = self.get_object()

        # Check if order has any reports
        if instance.reports.exists():
            return Response(
                {
                    "error": "Cannot delete order with associated reports. Delete the reports first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)
