"""
Unit tests for orders services.
"""

from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Lease, AgencyType
from orders.services.lease_directory_search import run_lease_directory_search
from orders.services.previous_report_detection import run_previous_report_detection
from integrations.models import CloudLocation, AgencyStorageConfig
from integrations.utils import AgencyStorageConfigError
from integrations.cloud.errors import CloudServiceError


class TestLeaseDirectorySearch(TestCase):
    """Test the lease directory search service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.lease = Lease.objects.create(
            agency=AgencyType.NMSLO,
            lease_number="12345",
        )
        self.agency_config = AgencyStorageConfig.objects.create(
            agency=AgencyType.NMSLO,
            runsheet_archive_base_path="/test/runsheet/archive",
            documents_base_path="/test/documents",
            misc_index_base_path="/test/misc/index",
            enabled=True,
        )

    @patch("orders.services.lease_directory_search.get_cloud_service")
    def test_lease_directory_search_found(self, mock_get_cloud_service):
        """Test successful directory search when directory is found."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = True
        mock_cloud_service.list_files.return_value = [Mock(name="test.txt")]

        mock_share_link = Mock()
        mock_share_link.url = "https://dropbox.com/share/test"
        mock_share_link.expires_at = None
        mock_share_link.is_public = True
        mock_cloud_service.create_share_link.return_value = mock_share_link

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service
        result = run_lease_directory_search(self.lease.id, self.user.id)

        # Verify results
        self.assertTrue(result["found"])
        self.assertEqual(result["path"], "/test/runsheet/archive/12345")
        self.assertEqual(result["share_url"], "https://dropbox.com/share/test")
        self.assertIsNotNone(result["location_id"])

        # Verify lease was updated
        self.lease.refresh_from_db()
        self.assertIsNotNone(self.lease.runsheet_directory)
        self.assertEqual(
            self.lease.runsheet_directory.path, "/test/runsheet/archive/12345"
        )

    @patch("orders.services.lease_directory_search.get_cloud_service")
    def test_lease_directory_search_not_found(self, mock_get_cloud_service):
        """Test directory search when directory is not found."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = True
        mock_cloud_service.list_files.return_value = (
            []
        )  # No files = directory not found

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service
        result = run_lease_directory_search(self.lease.id, self.user.id)

        # Verify results
        self.assertFalse(result["found"])
        self.assertEqual(result["path"], "/test/runsheet/archive/12345")
        self.assertIsNone(result["share_url"])
        self.assertIsNone(result["location_id"])

        # Verify lease was not updated
        self.lease.refresh_from_db()
        self.assertIsNone(self.lease.runsheet_directory)

    @patch("orders.services.lease_directory_search.get_cloud_service")
    def test_lease_directory_search_not_authenticated(self, mock_get_cloud_service):
        """Test directory search when cloud service is not authenticated."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = False

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service and expect error
        with self.assertRaises(CloudServiceError):
            run_lease_directory_search(self.lease.id, self.user.id)

    def test_lease_directory_search_missing_agency_config(self):
        """Test directory search when agency config is missing."""
        # Delete agency config
        self.agency_config.delete()

        # Run service and expect error
        with self.assertRaises(AgencyStorageConfigError):
            run_lease_directory_search(self.lease.id, self.user.id)

    def test_lease_directory_search_disabled_agency_config(self):
        """Test directory search when agency config is disabled."""
        # Disable agency config
        self.agency_config.enabled = False
        self.agency_config.save()

        # Run service and expect error
        with self.assertRaises(AgencyStorageConfigError):
            run_lease_directory_search(self.lease.id, self.user.id)


class TestPreviousReportDetection(TestCase):
    """Test the previous report detection service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.lease = Lease.objects.create(
            agency=AgencyType.NMSLO,
            lease_number="12345",
        )
        self.cloud_location = CloudLocation.objects.create(
            provider="dropbox",
            path="/test/runsheet/archive/12345",
            name="12345",
            is_directory=True,
        )
        self.lease.runsheet_directory = self.cloud_location
        self.lease.save()

    @patch("orders.services.previous_report_detection.get_cloud_service")
    def test_previous_report_detection_found(self, mock_get_cloud_service):
        """Test successful detection when Master Documents files are found."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = True

        # Mock files including one that matches
        mock_file1 = Mock()
        mock_file1.name = "Master Documents Report.pdf"
        mock_file2 = Mock()
        mock_file2.name = "Other File.txt"
        mock_cloud_service.list_files.return_value = [mock_file1, mock_file2]

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service
        result = run_previous_report_detection(self.lease.id, self.user.id)

        # Verify results
        self.assertTrue(result["found"])
        self.assertEqual(len(result["matching_files"]), 1)
        self.assertIn("Master Documents Report.pdf", result["matching_files"])

        # Verify lease was updated
        self.lease.refresh_from_db()
        self.assertTrue(self.lease.runsheet_report_found)

    @patch("orders.services.previous_report_detection.get_cloud_service")
    def test_previous_report_detection_not_found(self, mock_get_cloud_service):
        """Test detection when no Master Documents files are found."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = True

        # Mock files that don't match
        mock_file1 = Mock()
        mock_file1.name = "Other Report.pdf"
        mock_file2 = Mock()
        mock_file2.name = "Another File.txt"
        mock_cloud_service.list_files.return_value = [mock_file1, mock_file2]

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service
        result = run_previous_report_detection(self.lease.id, self.user.id)

        # Verify results
        self.assertFalse(result["found"])
        self.assertEqual(len(result["matching_files"]), 0)

        # Verify lease was updated
        self.lease.refresh_from_db()
        self.assertFalse(self.lease.runsheet_report_found)

    def test_previous_report_detection_no_directory(self):
        """Test detection when no runsheet directory is present."""
        # Remove runsheet directory
        self.lease.runsheet_directory = None
        self.lease.save()

        # Run service
        result = run_previous_report_detection(self.lease.id, self.user.id)

        # Verify results
        self.assertFalse(result["found"])
        self.assertEqual(len(result["matching_files"]), 0)

        # Verify lease was not updated
        self.lease.refresh_from_db()
        self.assertFalse(self.lease.runsheet_report_found)

    @patch("orders.services.previous_report_detection.get_cloud_service")
    def test_previous_report_detection_not_authenticated(self, mock_get_cloud_service):
        """Test detection when cloud service is not authenticated."""
        # Mock cloud service
        mock_cloud_service = Mock()
        mock_cloud_service.is_authenticated.return_value = False

        mock_get_cloud_service.return_value = mock_cloud_service

        # Run service and expect error
        with self.assertRaises(CloudServiceError):
            run_previous_report_detection(self.lease.id, self.user.id)
