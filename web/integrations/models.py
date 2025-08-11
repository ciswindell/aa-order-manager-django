"""Models for the `integrations` app (Dropbox OAuth storage)."""

from django.db import models
from django.conf import settings


class DropboxAccount(models.Model):
    """Per-user Dropbox OAuth credentials.

    Stores current access token, encrypted refresh token, and metadata for a single
    Dropbox account linked to a Django user.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dropbox_account",
    )
    account_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    refresh_token_encrypted = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)
    scope = models.TextField(blank=True, default="")
    token_type = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "integrations_dropbox_account"
        indexes = [
            models.Index(fields=["account_id"]),
        ]

    def __str__(self) -> str:
        return f"DropboxAccount(user={self.user.pk}, account_id={self.account_id})"


# Create your models here.
