"""Lease API views."""

from api.serializers.leases import LeaseSerializer
from django_filters.rest_framework import DjangoFilterBackend
from orders.models import Lease
from rest_framework import filters, status, viewsets
from rest_framework.response import Response


class LeaseViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Lease instances.
    Provides CRUD operations for leases with filtering by agency and report.
    """

    serializer_class = LeaseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["agency"]
    ordering_fields = ["created_at", "agency", "lease_number"]

    def get_queryset(self):
        """Get queryset with optional report filtering."""
        queryset = (
            Lease.objects.all()
            .select_related(
                "runsheet_archive",
                "created_by",
                "updated_by",
            )
            .prefetch_related("document_images_links")
            .order_by("-created_at")
        )

        # Filter by report if report parameter is provided
        report_id = self.request.query_params.get("report")
        if report_id:
            queryset = queryset.filter(reports__id=report_id).distinct()

        return queryset

    def perform_create(self, serializer):
        """Set the created_by and updated_by fields on object creation."""
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        """Set the updated_by field on object update."""
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of a lease if it has associated reports.
        Reports require at least one lease, so deleting a lease would leave reports in an invalid state.
        """
        instance = self.get_object()
        report_count = instance.reports.count()
        if report_count > 0:
            return Response(
                {
                    "detail": f"Cannot delete this lease. It is associated with {report_count} report(s). "
                    "Remove the lease from those reports first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)
