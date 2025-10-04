from django.contrib import admin

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
    readonly_fields = ("runsheet_link", "misc_index_link", "runsheet_report_found", "created_at", "updated_at")
    
    # Hide runsheet_archive (it's just the foreign key to CloudLocation)
    exclude = ("runsheet_archive",)

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
