"""Report API views."""

from api.serializers.reports import ReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from orders.models import Report
from rest_framework import filters, status, viewsets
from rest_framework.response import Response


class ReportViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Report instances.
    Provides CRUD operations for reports with filtering by order.
    """

    queryset = (
        Report.objects.all()
        .select_related("order", "created_by", "updated_by")
        .prefetch_related("leases")
        .order_by("-created_at")
    )
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["order", "report_type"]
    ordering_fields = ["created_at", "start_date", "end_date"]

    def perform_create(self, serializer):
        """Set the created_by and updated_by fields on object creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set the updated_by field on object update."""
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of a report if it has associated leases.
        """
        instance = self.get_object()
        if instance.leases.exists():
            return Response(
                {
                    "detail": "Cannot delete a report that has associated leases. Delete the leases first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
