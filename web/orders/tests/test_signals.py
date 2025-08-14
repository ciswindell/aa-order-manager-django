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

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_enqueue_on_create_with_user(
        self, mock_get_user_id, mock_delay, _on_commit
    ):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A1")
        mock_delay.assert_called_once_with(lease.id, self.user.id)

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_skip_on_create_without_user(
        self, mock_get_user_id, mock_delay, _on_commit
    ):
        mock_get_user_id.return_value = None
        Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A2")
        mock_delay.assert_not_called()

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_enqueue_on_update_with_user(
        self, mock_get_user_id, mock_delay, _on_commit
    ):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A3")
        mock_delay.reset_mock()
        lease.misc_index_link = "https://example.com"
        lease.save()  # normal update should enqueue
        mock_delay.assert_called_once_with(lease.id, self.user.id)

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_skip_on_task_only_field_updates(
        self, mock_get_user_id, mock_delay, _on_commit
    ):
        mock_get_user_id.return_value = self.user.id
        lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A4")
        mock_delay.reset_mock()
        # Update only task-managed fields -> should not enqueue
        lease.runsheet_report_found = True
        lease.save(update_fields={"runsheet_report_found"})
        mock_delay.assert_not_called()

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.redis.from_url")
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_dedup_skips_second_enqueue_within_ttl(
        self, mock_get_user_id, mock_delay, mock_redis_from_url, _on_commit
    ):
        mock_get_user_id.return_value = self.user.id

        # Fake Redis client with SETNX behavior
        class FakeRedis:
            def __init__(self):
                self._keys = set()

            def set(self, name, value, nx=False, ex=None):
                if nx:
                    if name in self._keys:
                        return False
                    self._keys.add(name)
                    return True
                return True

        mock_redis_from_url.return_value = FakeRedis()

        with self.settings(CELERY_BROKER_URL="redis://localhost:6379/0"):
            lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A5")
            # First enqueue should call delay
            mock_delay.assert_called_once_with(lease.id, self.user.id)
            mock_delay.reset_mock()

            # Second update within TTL should be skipped by dedup
            lease.order_notes = "update"
            lease.save()
            mock_delay.assert_not_called()

    @patch("orders.signals.transaction.on_commit", side_effect=lambda fn: fn())
    @patch("orders.signals.redis.from_url")
    @patch("orders.signals.full_runsheet_discovery_task.delay")
    @patch("orders.signals.get_current_user_id")
    def test_dedup_is_task_scoped_allows_other_tasks(
        self, mock_get_user_id, mock_delay, mock_redis_from_url, _on_commit
    ):
        mock_get_user_id.return_value = self.user.id

        class FakeRedis:
            def __init__(self):
                self._keys = set()

            def set(self, name, value, nx=False, ex=None):
                if nx:
                    if name in self._keys:
                        return False
                    self._keys.add(name)
                    return True
                return True

        mock_redis_from_url.return_value = FakeRedis()

        with self.settings(CELERY_BROKER_URL="redis://localhost:6379/0"):
            # Avoid setting our task's dedup key during create
            mock_get_user_id.return_value = None
            lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="A6")
            # Simulate dedup key existing for this task+lease
            from orders.signals import full_runsheet_discovery_task

            task_name = getattr(
                full_runsheet_discovery_task, "name", "full_runsheet_discovery_task"
            )
            # create a colliding key for a different task name to ensure our keying is task-scoped
            other_task_name = "some_other_task"
            other_key = f"orders:dedup:task:{other_task_name}:lease:{lease.id}"
            client = mock_redis_from_url.return_value
            client.set(other_key, "1", nx=True, ex=120)

            # Our enqueue should still go through because key is for a different task
            mock_get_user_id.return_value = self.user.id
            mock_delay.reset_mock()
            lease.misc_index_link = "https://example.com/abc"
            lease.save()
            mock_delay.assert_called_once_with(lease.id, self.user.id)
