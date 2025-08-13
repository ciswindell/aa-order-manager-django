"""
Signal tests for orders app.
"""

from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Lease, AgencyType


class TestLeaseSignals(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="siguser", email="sig@example.com", password="testpass"
        )

    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_enqueue_on_create_with_user(self, mock_get_user_id, mock_delay):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A1")
        mock_delay.assert_called_once_with(lease.id, self.user.id)

    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_skip_on_create_without_user(self, mock_get_user_id, mock_delay):
        mock_get_user_id.return_value = None
        Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A2")
        mock_delay.assert_not_called()

    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_enqueue_on_update_with_user(self, mock_get_user_id, mock_delay):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A3")
        mock_delay.reset_mock()
        lease.misc_index_link = "https://example.com"
        lease.save()  # normal update should enqueue
        mock_delay.assert_called_once_with(lease.id, self.user.id)

    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_skip_on_task_only_field_updates(self, mock_get_user_id, mock_delay):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A4")
        mock_delay.reset_mock()
        # Update only task-managed fields -> should not enqueue
        lease.runsheet_report_found = True
        lease.save(update_fields={"runsheet_report_found"})
        mock_delay.assert_not_called()
