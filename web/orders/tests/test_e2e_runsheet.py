"""
End-to-end style tests for runsheet discovery and detection.
"""

from unittest.mock import patch, Mock
from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Lease, AgencyType
from orders.tasks import full_runsheet_discovery_task
from integrations.models import AgencyStorageConfig, CloudLocation


class TestRunsheetE2E(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="e2euser", email="e2e@example.com", password="testpass"
        )
        AgencyStorageConfig.objects.create(
            agency=AgencyType.NMSLO,
            runsheet_archive_base_path="/root/runsheet",
            documents_base_path="/root/docs",
            misc_index_base_path="/root/misc",
            enabled=True,
        )

    @patch("orders.services.previous_report_detection.get_cloud_service")
    @patch("orders.services.runsheet_archive_search.get_cloud_service")
    def test_full_runsheet_discovery(
        self, mock_get_cloud_service_search, mock_get_cloud_service_detect
    ):
        # Mock search service cloud client
        mock_search_client = Mock()
        mock_search_client.is_authenticated.return_value = True
        mock_search_client.list_files.return_value = [Mock()]
        share = Mock()
        share.url = "https://share/link"
        share.expires_at = None
        share.is_public = True
        mock_search_client.create_share_link.return_value = share
        mock_get_cloud_service_search.return_value = mock_search_client

        # Mock detection service cloud client
        mock_detect_client = Mock()
        mock_detect_client.is_authenticated.return_value = True
        file1 = Mock()
        file1.name = "Master Documents.pdf"
        file2 = Mock()
        file2.name = "other.txt"
        mock_detect_client.list_files.return_value = [file1, file2]
        mock_get_cloud_service_detect.return_value = mock_detect_client

        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="XYZ123")

        result = full_runsheet_discovery_task(lease.id, self.user.id)

        # Verify search results
        self.assertTrue(result["search"]["found"])
        self.assertEqual(result["search"]["share_url"], "https://share/link")

        lease.refresh_from_db()
        self.assertIsNotNone(lease.runsheet_archive)
        self.assertEqual(lease.runsheet_archive.path, "/root/runsheet/XYZ123")

        # Verify detection results
        self.assertTrue(result["detection"]["found"])
        self.assertIn("Master Documents.pdf", result["detection"]["matching_files"])
