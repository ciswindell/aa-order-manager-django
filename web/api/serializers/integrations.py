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
