"""Admin registrations for the `integrations` app."""

from django.contrib import admin
from .models import DropboxAccount, CloudLocation, AgencyStorageConfig


@admin.register(DropboxAccount)
class DropboxAccountAdmin(admin.ModelAdmin):
    """Admin for Dropbox OAuth accounts."""

    list_display = ("user", "account_id", "expires_at", "updated_at")
    search_fields = ("account_id", "user__username", "user__email")
    readonly_fields = (
        "access_token",
        "refresh_token_encrypted",
        "created_at",
        "updated_at",
    )


@admin.register(CloudLocation)
class CloudLocationAdmin(admin.ModelAdmin):
    """Admin for cloud locations."""

    list_display = (
        "provider",
        "path",
        "name",
        "is_directory",
        "share_url",
        "updated_at",
    )
    search_fields = ("path", "name", "provider")
    readonly_fields = (
        "file_id",
        "size_bytes",
        "modified_at",
        "created_at",
        "updated_at",
    )
    list_filter = ("provider", "is_directory", "is_public")
    ordering = ("-updated_at",)


@admin.register(AgencyStorageConfig)
class AgencyStorageConfigAdmin(admin.ModelAdmin):
    """Admin for agency storage configuration."""

    list_display = (
        "agency",
        "enabled",
        "auto_create_runsheet_archives",
        "runsheet_archive_base_path",
        "updated_at",
    )
    search_fields = ("agency",)
    list_filter = ("enabled", "agency")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("agency",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "agency",
                    "enabled",
                    "auto_create_runsheet_archives",
                )
            },
        ),
        (
            "Base Paths",
            {
                "fields": (
                    "runsheet_archive_base_path",
                    "documents_base_path",
                    "misc_index_base_path",
                )
            },
        ),
        (
            "Runsheet Subfolders",
            {
                "fields": (
                    "runsheet_subfolder_documents_name",
                    "runsheet_subfolder_misc_index_name",
                    "runsheet_subfolder_runsheets_name",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


# Register your models here.
