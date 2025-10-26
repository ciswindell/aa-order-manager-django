"""Report serializers for API."""

from orders.models import Lease, Order, Report
from rest_framework import serializers


class OrderBasicSerializer(serializers.Serializer):
    """Nested serializer for order reference."""

    id = serializers.IntegerField()
    order_number = serializers.CharField()


class UserBasicSerializer(serializers.Serializer):
    """Nested serializer for user reference."""

    id = serializers.IntegerField()
    username = serializers.CharField()


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for the Report model."""

    order = OrderBasicSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.none(),
        source="order",
        write_only=True,
    )
    lease_ids = serializers.PrimaryKeyRelatedField(
        queryset=Lease.objects.none(),
        source="leases",
        many=True,
        required=True,
    )
    lease_count = serializers.SerializerMethodField()
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "order",
            "order_id",
            "report_type",
            "legal_description",
            "start_date",
            "end_date",
            "report_notes",
            "lease_ids",
            "lease_count",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "lease_count", "created_at", "updated_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set the queryset for relational fields
        if "order_id" in self.fields:
            self.fields["order_id"].queryset = Order.objects.all()
        if "lease_ids" in self.fields:
            self.fields["lease_ids"].child_relation.queryset = Lease.objects.all()

    def get_lease_count(self, obj) -> int:
        """Return the number of leases associated with the report."""
        return obj.leases.count()

    def validate_lease_ids(self, value):
        """Validate that at least one lease is provided."""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "At least one lease must be selected for the report."
            )
        return value

    def validate_report_type(self, value):
        """Validate report_type is from allowed choices."""
        from orders.models import ReportType

        allowed_types = [choice[0] for choice in ReportType.choices]
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid report type. Must be one of: {', '.join(allowed_types)}"
            )
        return value
