"""Admin registrations for the `integrations` app."""

from django.contrib import admin

from .models import (
    AgencyStorageConfig,
    BasecampAccount,
    CloudLocation,
    DropboxAccount,
)


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


@admin.register(BasecampAccount)
class BasecampAccountAdmin(admin.ModelAdmin):
    """Admin for Basecamp OAuth accounts with management actions."""

    list_display = (
        "user",
        "account_id",
        "account_name",
        "token_status",
        "expires_at",
        "updated_at",
    )
    search_fields = ("account_id", "account_name", "user__username", "user__email")
    readonly_fields = (
        "access_token",
        "refresh_token_encrypted",
        "created_at",
        "updated_at",
        "token_status",
    )
    actions = ["disconnect_accounts", "check_token_status"]
    list_filter = ("created_at", "updated_at")

    @admin.display(description="Token Status")
    def token_status(self, obj):
        """Display token expiration status."""
        from datetime import datetime, timezone

        if not obj.expires_at:
            return "No expiration"
        now = datetime.now(timezone.utc)
        if obj.expires_at.tzinfo is None:
            expires_at = obj.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = obj.expires_at
        if expires_at > now:
            return f"Valid until {expires_at}"
        return "Expired"

    @admin.action(description="Disconnect selected Basecamp accounts")
    def disconnect_accounts(self, request, queryset):
        """Manually disconnect Basecamp accounts (delete records)."""
        from integrations.status.cache import default_cache

        count = 0
        for account in queryset:
            user_id = account.user.id
            account.delete()
            # Invalidate cache
            cache_key = f"integration_status:basecamp:{user_id}"
            default_cache.delete(cache_key)
            count += 1
        self.message_user(request, f"Successfully disconnected {count} account(s).")

    @admin.action(description="Check token status for selected accounts")
    def check_token_status(self, request, queryset):
        """Check and display token status for selected accounts."""
        from datetime import datetime, timezone

        messages = []
        for account in queryset:
            if not account.expires_at:
                status = "No expiration"
            else:
                now = datetime.now(timezone.utc)
                expires_at = account.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at > now:
                    status = f"Valid until {expires_at}"
                else:
                    status = "Expired"
            messages.append(
                f"User: {account.user.username} | Account: {account.account_name} | Status: {status}"
            )
        self.message_user(request, "\n".join(messages))


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
        "auto_create_document_archives",
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
                    "auto_create_document_archives",
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
        (
            "Document Subfolders",
            {
                "fields": (
                    "document_subfolder_agency_sourced_documents",
                    "document_subfolder_unknown_sourced_documents",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


# Register your models here.
