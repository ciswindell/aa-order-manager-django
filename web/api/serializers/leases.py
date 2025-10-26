"""Lease serializers for API."""

from orders.models import Lease
from rest_framework import serializers


class UserBasicSerializer(serializers.Serializer):
    """Nested serializer for user reference."""

    id = serializers.IntegerField()
    username = serializers.CharField()


class LeaseSerializer(serializers.ModelSerializer):
    """Serializer for the Lease model."""

    runsheet_status = serializers.SerializerMethodField()
    runsheet_archive_link = serializers.SerializerMethodField()
    document_archive_link = serializers.SerializerMethodField()
    created_by = UserBasicSerializer(read_only=True)
    updated_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = Lease
        fields = [
            "id",
            "agency",
            "lease_number",
            "runsheet_link",
            "runsheet_archive_link",
            "runsheet_status",
            "document_archive_link",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "runsheet_link",
            "runsheet_archive_link",
            "runsheet_status",
            "document_archive_link",
            "created_at",
            "updated_at",
        ]

    def get_runsheet_status(self, obj) -> str:
        """
        Return runsheet discovery status based on runsheet_report_found and runsheet_link.
        - "Found": runsheet_report_found=True, runsheet_link present
        - "Not Found": runsheet_report_found=True, runsheet_link=None
        - "Pending": runsheet_report_found=False
        """
        if not obj.runsheet_report_found:
            return "Pending"
        if obj.runsheet_link:
            return "Found"
        return "Not Found"

    def get_runsheet_archive_link(self, obj) -> str | None:
        """Return Dropbox link to runsheet archive directory."""
        if obj.runsheet_archive:
            return obj.runsheet_archive.share_url
        return None

    def get_document_archive_link(self, obj) -> str | None:
        """Return URL to document archive directory."""
        # Get DocumentImagesLink for this lease
        doc_link = obj.document_images_links.first()
        if doc_link:
            return doc_link.url
        return None
