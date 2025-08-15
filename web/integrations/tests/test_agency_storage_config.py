from django.test import TestCase

from integrations.models import AgencyStorageConfig


class TestAgencyStorageConfig(TestCase):
    def test_subfolder_name_normalization_strips_slashes_and_blanks(self):
        cfg = AgencyStorageConfig.objects.create(
            agency="NMSLO",
            runsheet_archive_base_path="/State Workspace/Archive/",
            runsheet_subfolder_documents_name="/ ^Document Archive /",
            runsheet_subfolder_misc_index_name="",
            runsheet_subfolder_runsheets_name="Runsheets/",
        )

        cfg.refresh_from_db()
        # Base path normalized: leading slash, no trailing
        assert cfg.runsheet_archive_base_path == "/State Workspace/Archive"
        # Subfolders normalized: stripped and empty -> None
        assert cfg.runsheet_subfolder_documents_name == "^Document Archive"
        assert cfg.runsheet_subfolder_misc_index_name is None
        assert cfg.runsheet_subfolder_runsheets_name == "Runsheets"

    def test_auto_create_toggle_defaults_true(self):
        cfg = AgencyStorageConfig.objects.create(
            agency="BLM",
            runsheet_archive_base_path="/Federal Workspace/Runsheet Archive",
        )
        cfg.refresh_from_db()
        assert cfg.auto_create_runsheet_archives is True
