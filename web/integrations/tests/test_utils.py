"""
Unit tests for integrations utils.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError

from orders.models import AgencyType
from integrations.models import AgencyStorageConfig
from integrations.utils import get_agency_storage_config, AgencyStorageConfigError


class TestGetAgencyStorageConfig(TestCase):
    """Test the get_agency_storage_config resolver function."""

    def setUp(self):
        """Set up test data."""
        self.agency = AgencyType.NMSLO
        self.config = AgencyStorageConfig.objects.create(
            agency=self.agency,
            runsheet_archive_base_path="/test/runsheet/archive",
            documents_base_path="/test/documents",
            misc_index_base_path="/test/misc/index",
            enabled=True,
        )

    def test_get_agency_storage_config_present(self):
        """Test successful retrieval of enabled configuration."""
        result = get_agency_storage_config(self.agency)

        self.assertEqual(result, self.config)
        self.assertEqual(result.agency, self.agency)
        self.assertTrue(result.enabled)

    def test_get_agency_storage_config_missing(self):
        """Test error when configuration is missing."""
        missing_agency = AgencyType.BLM

        with self.assertRaises(AgencyStorageConfigError) as context:
            get_agency_storage_config(missing_agency)

        self.assertIn(
            "No storage configuration found for agency: BLM", str(context.exception)
        )

    def test_get_agency_storage_config_disabled(self):
        """Test error when configuration is disabled."""
        self.config.enabled = False
        self.config.save()

        with self.assertRaises(AgencyStorageConfigError) as context:
            get_agency_storage_config(self.agency)

        self.assertIn(
            "Storage configuration is disabled for agency: NMSLO",
            str(context.exception),
        )

    def test_get_agency_storage_config_returns_correct_fields(self):
        """Test that returned config has all expected fields."""
        result = get_agency_storage_config(self.agency)

        self.assertEqual(result.runsheet_archive_base_path, "/test/runsheet/archive")
        self.assertEqual(result.documents_base_path, "/test/documents")
        self.assertEqual(result.misc_index_base_path, "/test/misc/index")
        self.assertTrue(result.enabled)
