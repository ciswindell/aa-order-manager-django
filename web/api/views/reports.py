"""Report API views."""

from api.serializers.reports import ReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from orders.models import Report
from rest_framework import filters, viewsets


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
