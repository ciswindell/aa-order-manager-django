"""Order serializers for API."""

from orders.models import Order
from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model with audit fields and report count."""

    report_count = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(
        source="created_by.username", read_only=True
    )
    updated_by_username = serializers.CharField(
        source="updated_by.username", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "order_date",
            "order_notes",
            "delivery_link",
            "report_count",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_username",
            "updated_by",
            "updated_by_username",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "report_count",
        ]

    def get_report_count(self, obj):
        """Return the number of reports associated with this order."""
        return obj.reports.count()
