from django.contrib import admin

from .models import DocumentImagesLink, Lease, Order, Report


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "order_date")
    search_fields = ("order_number",)


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ("agency", "lease_number")
    search_fields = ("lease_number",)
    list_filter = ("agency",)

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
