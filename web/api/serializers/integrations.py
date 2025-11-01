"""Integration serializers for API."""

from rest_framework import serializers


class IntegrationStatusSerializer(serializers.Serializer):
    """Serializer for integration status information."""

    provider = serializers.CharField()
    is_connected = serializers.BooleanField(source="connected")
    is_authenticated = serializers.BooleanField(source="authenticated")
    last_sync = serializers.DateTimeField(source="last_checked")
    blocking_problem = serializers.BooleanField()
    reason = serializers.CharField()
    cta_label = serializers.CharField(allow_null=True)
    cta_url = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        """Convert relative URLs to absolute URLs for frontend consumption."""
        data = super().to_representation(instance)

        # Convert relative cta_url to absolute URL if present
        if data.get("cta_url") and data["cta_url"].startswith("/"):
            request = self.context.get("request")
            if request:
                data["cta_url"] = request.build_absolute_uri(data["cta_url"])

        return data
