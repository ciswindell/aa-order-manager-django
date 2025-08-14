"""
Task tests for orders app.
"""

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Lease, AgencyType
from orders.tasks import (
    lease_directory_search_task,
    previous_report_detection_task,
    full_runsheet_discovery_task,
)


class TestOrdersTasks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="taskuser", email="task@example.com", password="testpass"
        )
        self.lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="T1")

    @patch("orders.tasks.run_lease_directory_search")
    @patch("orders.tasks.logger.info")
    def test_lease_directory_search_task_logs_and_calls_service(
        self, mock_logger_info, mock_service
    ):
        mock_service.return_value = {"ok": True}
        result = lease_directory_search_task.run(self.lease.id, self.user.id)
        self.assertEqual(result, {"ok": True})
        mock_service.assert_called_once_with(self.lease.id, self.user.id)
        mock_logger_info.assert_called()

    @patch("orders.tasks.run_previous_report_detection")
    @patch("orders.tasks.logger.info")
    def test_previous_report_detection_task_logs_and_calls_service(
        self, mock_logger_info, mock_service
    ):
        mock_service.return_value = {"found": False, "matching_files": []}
        result = previous_report_detection_task.run(self.lease.id, self.user.id)
        self.assertEqual(result, {"found": False, "matching_files": []})
        mock_service.assert_called_once_with(self.lease.id, self.user.id)
        mock_logger_info.assert_called()

    @patch("orders.tasks.run_previous_report_detection")
    @patch("orders.tasks.run_lease_directory_search")
    @patch("orders.tasks.logger.info")
    def test_full_runsheet_discovery_calls_detection_when_found(
        self, mock_logger_info, mock_search, mock_detect
    ):
        mock_search.return_value = {"found": True}
        mock_detect.return_value = {"found": True, "matching_files": ["x"]}
        result = full_runsheet_discovery_task.run(self.lease.id, self.user.id)
        self.assertEqual(
            result,
            {
                "search": {"found": True},
                "detection": {"found": True, "matching_files": ["x"]},
            },
        )
        mock_search.assert_called_once_with(self.lease.id, self.user.id)
        mock_detect.assert_called_once_with(self.lease.id, self.user.id)
        mock_logger_info.assert_called()

    @patch("orders.tasks.run_previous_report_detection")
    @patch("orders.tasks.run_lease_directory_search")
    @patch("orders.tasks.logger.info")
    def test_full_runsheet_discovery_skips_detection_when_not_found(
        self, mock_logger_info, mock_search, mock_detect
    ):
        mock_search.return_value = {"found": False}
        result = full_runsheet_discovery_task.run(self.lease.id, self.user.id)
        self.assertEqual(result, {"search": {"found": False}, "detection": None})
        mock_search.assert_called_once_with(self.lease.id, self.user.id)
        mock_detect.assert_not_called()
        mock_logger_info.assert_called()
