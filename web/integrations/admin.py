"""Admin registrations for the `integrations` app."""

from django.contrib import admin
from .models import DropboxAccount


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


# Register your models here.
