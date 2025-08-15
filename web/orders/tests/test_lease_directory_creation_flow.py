from django.test import TestCase
from django.contrib.auth.models import User

from orders.models import Lease, AgencyType
from integrations.models import AgencyStorageConfig, CloudLocation
from integrations.cloud import factory as cloud_factory


class TestLeaseDirectoryCreationFlow(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="u1")
        AgencyStorageConfig.objects.create(
            agency=AgencyType.NMSLO,
            runsheet_archive_base_path="/State Workspace/^Runsheet Workspace/Runsheet Report Archive - New Format",
            runsheet_subfolder_documents_name="^Document Archive",
            runsheet_subfolder_misc_index_name="^MI Index",
            runsheet_subfolder_runsheets_name="Runsheets",
            enabled=True,
            auto_create_runsheet_archives=True,
        )
        self.lease = Lease.objects.create(agency=AgencyType.NMSLO, lease_number="12345")

    def test_missing_directory_triggers_creation_and_updates_lease(self):
        # Build a fake service and inject into the module under test
        from orders.services import runsheet_archive_search as lds

        service = cloud_factory.get_cloud_service(provider="dropbox", user=self.user)
        service._auth_service.is_authenticated = lambda: True  # type: ignore[attr-defined]
        # Satisfy service-level is_authenticated guard which now also requires workspace handler
        service._workspace_handler = object()  # type: ignore[attr-defined]
        # Simulate base exists, but lease directory missing initially
        base = (
            "/State Workspace/^Runsheet Workspace/Runsheet Report Archive - New Format"
        )
        lease_dir = f"{base}/12345"
        # list_files returns empty -> not found
        service.list_files = lambda p: []  # type: ignore[method-assign]
        # list_directories works for base
        service.list_directories = lambda p: []  # type: ignore[method-assign]
        # _get_metadata returns metadata for base path (simulating base exists)
        service._get_metadata = lambda p: type("MD", (), {"path": p, "is_directory": True})() if p == base else None  # type: ignore[method-assign]
        # create_directory returns a CloudFile-like object
        service.create_directory = lambda p, parents=True: type(
            "CF", (), {"path": p, "name": p.rsplit("/", 1)[-1], "is_directory": True}
        )()  # type: ignore[method-assign]
        # create_directory_tree no-op
        service.create_directory_tree = lambda root, subs, exists_ok=True: []  # type: ignore[method-assign]

        # Monkeypatch the symbol used by the service module
        lds.get_cloud_service = lambda provider, user: service  # type: ignore[assignment]

        result = lds.run_runsheet_archive_search(self.lease.id, self.user.id)
        assert result["found"] is False
        assert result["path"].endswith("/12345")

        self.lease.refresh_from_db()
        assert self.lease.runsheet_archive is not None
        assert self.lease.runsheet_report_found is False
        cl = CloudLocation.objects.get(path=lease_dir)
        assert cl.is_directory is True

    def test_rerun_on_existing_directory_is_noop_success(self):
        from orders.services import runsheet_archive_search as lds

        service = cloud_factory.get_cloud_service(provider="dropbox", user=self.user)
        service._auth_service.is_authenticated = lambda: True  # type: ignore[attr-defined]
        service._workspace_handler = object()  # type: ignore[attr-defined]

        base = (
            "/State Workspace/^Runsheet Workspace/Runsheet Report Archive - New Format"
        )
        lease_dir = f"{base}/12345"

        # Directory exists: list_files returns a dummy file name object
        class F:
            def __init__(self, name):
                self.name = name

        service.list_files = lambda p: [F("dummy.txt")]  # type: ignore[method-assign]
        # No-op share link creation
        service.create_share_link = lambda p, is_public=True: None  # type: ignore[method-assign]

        # Patch symbol in module
        lds.get_cloud_service = lambda provider, user: service  # type: ignore[assignment]

        result = lds.run_runsheet_archive_search(self.lease.id, self.user.id)
        assert result["found"] is True
