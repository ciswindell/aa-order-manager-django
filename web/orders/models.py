"""Django models for orders, leases, and reports."""

from django.db import models
from django.core.exceptions import ValidationError
from typing import Any, cast


class ReportType(models.TextChoices):
    """Report type options for order items."""

    RUNSHEET = "RUNSHEET", "Runsheet"
    BASE_ABSTRACT = "BASE_ABSTRACT", "Base Abstract"
    SUPPLEMENTAL_ABSTRACT = "SUPPLEMENTAL_ABSTRACT", "Supplemental Abstract"
    DOL_ABSTRACT = "DOL_ABSTRACT", "DOL Abstract"


class AgencyType(models.TextChoices):
    """Agency types for leases."""

    NMSLO = "NMSLO", "NMSLO"
    BLM = "BLM", "BLM"


class Order(models.Model):
    """Customer order containing one or more requested report items."""

    order_number = models.CharField(max_length=64, unique=True)
    order_date = models.DateField()
    order_notes = models.TextField(blank=True, null=True)
    delivery_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Order {self.order_number}"


class Lease(models.Model):
    """Normalized lease record shared across reports and items."""

    agency = models.CharField(max_length=16, choices=AgencyType.choices)
    lease_number = models.CharField(max_length=128)
    misc_index_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model constraints and options."""

        constraints = [
            models.UniqueConstraint(
                fields=["agency", "lease_number"], name="uniq_agency_lease_number"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.agency} {self.lease_number}"


class DocumentImagesLink(models.Model):
    """URL for a document images location associated with a lease."""

    lease = models.ForeignKey(
        Lease, on_delete=models.CASCADE, related_name="document_images_links"
    )
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return self.url


class Report(models.Model):
    """A single requested report within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=32, choices=ReportType.choices)
    leases = models.ManyToManyField(Lease, related_name="reports", blank=True)
    legal_description = models.TextField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    report_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.order} — {self.report_type}"

    def clean(self) -> None:
        """Validate legal description and lease associations by report type."""
        if not str(self.legal_description or "").strip():
            raise ValidationError(
                {"legal_description": "Legal description is required."}
            )

        # Many-to-many validation requires a primary key to query counts reliably
        if not self.pk:
            return

        # Count via class-level through model to satisfy static analysis
        lease_count = Report.leases.through.objects.filter(report_id=self.pk).count()
        if self.report_type == ReportType.RUNSHEET and lease_count != 1:
            raise ValidationError(
                {"leases": "Runsheet reports must reference exactly one lease."}
            )
        if self.report_type != ReportType.RUNSHEET and lease_count < 1:
            raise ValidationError(
                {"leases": "Abstract reports must reference at least one lease."}
            )
