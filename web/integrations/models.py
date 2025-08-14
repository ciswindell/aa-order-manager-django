"""Models for the `integrations` app (Dropbox OAuth storage)."""

from django.db import models
from django.conf import settings
from orders.models import AgencyType


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
        return f"DropboxAccount(user={self.user}, account_id={self.account_id})"


class CloudLocation(models.Model):
    """Generic, reusable cloud location store for files and directories."""

    provider = models.CharField(max_length=32, default="dropbox", db_index=True)
    path = models.CharField(max_length=1024, db_index=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_directory = models.BooleanField(default=True)
    file_id = models.CharField(max_length=256, blank=True, null=True)
    share_url = models.URLField(blank=True, null=True)
    share_expires_at = models.DateTimeField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)
    modified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "integrations_cloud_location"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "path"], name="uniq_provider_path"
            )
        ]
        indexes = [
            models.Index(fields=["provider", "path"]),
        ]

    def __str__(self) -> str:
        return f"CloudLocation(provider={self.provider}, path={self.path})"


class AgencyStorageConfig(models.Model):
    """Per-agency storage configuration for cloud paths."""

    agency = models.CharField(max_length=16, choices=AgencyType.choices, unique=True)
    runsheet_archive_base_path = models.CharField(
        max_length=1024, blank=True, null=True
    )
    documents_base_path = models.CharField(max_length=1024, blank=True, null=True)
    misc_index_base_path = models.CharField(max_length=1024, blank=True, null=True)
    # Runsheet subfolder configuration (optional per agency)
    runsheet_subfolder_documents_name = models.CharField(
        max_length=255, blank=True, null=True
    )
    runsheet_subfolder_misc_index_name = models.CharField(
        max_length=255, blank=True, null=True
    )
    runsheet_subfolder_runsheets_name = models.CharField(
        max_length=255, blank=True, null=True
    )
    # Toggle for automatic lease directory creation
    auto_create_lease_directories = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "integrations_agency_storage_config"
        verbose_name = "Agency Storage Configuration"
        verbose_name_plural = "Agency Storage Configurations"

    def __str__(self) -> str:
        return f"AgencyStorageConfig(agency={self.agency})"

    # Normalization helpers
    @staticmethod
    def _normalize_path(path: str | None) -> str | None:
        if path is None:
            return None
        cleaned = str(path).strip().replace("\\", "/")
        if cleaned == "":
            return None
        # Ensure single leading slash and no trailing slash
        cleaned = "/" + cleaned.lstrip("/")
        cleaned = cleaned.rstrip("/")
        return cleaned

    @staticmethod
    def _normalize_subfolder_name(name: str | None) -> str | None:
        if name is None:
            return None
        cleaned = str(name).strip()
        if cleaned == "":
            return None
        # Subfolder names should not start or end with a slash
        cleaned = cleaned.strip("/\\")
        # Trim again to remove any spaces adjacent to removed slashes
        return cleaned.strip()

    def save(self, *args, **kwargs):  # pragma: no cover
        self.runsheet_archive_base_path = self._normalize_path(
            self.runsheet_archive_base_path
        )
        self.documents_base_path = self._normalize_path(self.documents_base_path)
        self.misc_index_base_path = self._normalize_path(self.misc_index_base_path)
        self.runsheet_subfolder_documents_name = self._normalize_subfolder_name(
            self.runsheet_subfolder_documents_name
        )
        self.runsheet_subfolder_misc_index_name = self._normalize_subfolder_name(
            self.runsheet_subfolder_misc_index_name
        )
        self.runsheet_subfolder_runsheets_name = self._normalize_subfolder_name(
            self.runsheet_subfolder_runsheets_name
        )
        super().save(*args, **kwargs)


# Create your models here.
