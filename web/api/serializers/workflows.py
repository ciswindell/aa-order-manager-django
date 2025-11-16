"""Serializers for workflow API responses."""

from rest_framework import serializers


class WorkflowResultSerializer(serializers.Serializer):
    """Serializer for WorkflowResult dataclass."""

    success = serializers.BooleanField()
    workflows_created = serializers.ListField(child=serializers.CharField())
    failed_products = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    total_count = serializers.IntegerField()
    message = serializers.CharField()

    def to_representation(self, instance):
        """
        Convert WorkflowResult dataclass to JSON response format.

        Args:
            instance: WorkflowResult dataclass instance

        Returns:
            dict with success, workflows_created, total_count, message,
            and optionally failed_products
        """
        data = {
            "success": instance.success,
            "workflows_created": instance.workflows_created,
            "total_count": instance.total_count,
            "message": self._build_message(instance),
        }

        if instance.failed_products:
            data["failed_products"] = instance.failed_products

        return data

    def _build_message(self, instance):
        """Build user-friendly message based on workflow result."""
        # No applicable products found
        if not instance.success and not instance.failed_products:
            return "No workflows to create for this order"
        
        # All products failed
        if not instance.success and instance.failed_products:
            failed_list = ", ".join(instance.failed_products)
            return f"Workflow creation failed for: {failed_list}"
        
        # Partial success (some succeeded, some failed)
        if instance.success and instance.failed_products:
            failed_count = len(instance.failed_products)
            return (
                f"Workflows created: {', '.join(instance.workflows_created)} "
                f"({failed_count} product(s) failed)"
            )
        
        # Complete success
        return f"Workflows created: {', '.join(instance.workflows_created)}"
