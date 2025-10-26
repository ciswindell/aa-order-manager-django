from django.contrib import admin
from django.utils.html import format_html

from .models import DocumentImagesLink, Lease, Order, Report


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "order_date")
    search_fields = ("order_number",)


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ("agency", "lease_number", "runsheet_report_found")
    search_fields = ("lease_number",)
    list_filter = ("agency", "runsheet_report_found")

    # Only agency and lease_number are editable
    readonly_fields = (
        "runsheet_link_display",
        "document_archive_link_display",
        "misc_index_link_display",
        "runsheet_report_found",
        "created_at",
        "updated_at",
    )

    # Hide runsheet_archive, runsheet_link, and misc_index_link (we show them via display methods)
    exclude = ("runsheet_archive", "runsheet_link", "misc_index_link")

    def runsheet_link_display(self, obj):
        """Display runsheet link that opens in a new tab."""
        if obj.runsheet_link:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
                obj.runsheet_link,
                obj.runsheet_link,
            )
        return "-"

    runsheet_link_display.short_description = "Runsheet link"

    def document_archive_link_display(self, obj):
        """Display document archive link that opens in a new tab."""
        doc_link = obj.document_images_links.first()
        if doc_link and doc_link.url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
                doc_link.url,
                doc_link.url,
            )
        return "-"

    document_archive_link_display.short_description = "Document archive link"

    def misc_index_link_display(self, obj):
        """Display misc index link that opens in a new tab."""
        if obj.misc_index_link:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">{}</a>',
                obj.misc_index_link,
                obj.misc_index_link,
            )
        return "-"

    misc_index_link_display.short_description = "Misc index link"

    class DocumentImagesLinkInline(admin.TabularInline):
        model = DocumentImagesLink
        extra = 1

    inlines = [DocumentImagesLinkInline]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("order", "report_type", "legal_description")
    list_filter = ("report_type",)
    search_fields = ("legal_description",)


# Register your models here.
