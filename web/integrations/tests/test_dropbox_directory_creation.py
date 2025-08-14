from types import SimpleNamespace

from django.test import TestCase

from integrations.dropbox.dropbox_service import DropboxCloudService


def make_meta(path: str, name: str):
    return SimpleNamespace(
        path_display=path, name=name, id="id:123", server_modified=None
    )


class TestDropboxDirectoryCreation(TestCase):
    def setUp(self) -> None:
        # Create service without going through real auth; inject fakes
        self.service = DropboxCloudService()
        self.service._client = SimpleNamespace()  # type: ignore[attr-defined]
        self.service._workspace_handler = SimpleNamespace()  # type: ignore[attr-defined]
        # Assume any path exists for parent checks
        self.service._get_metadata = lambda p: make_meta(p, p.rsplit("/", 1)[-1])  # type: ignore[attr-defined]

        # Pretend authenticated for decorator
        self.service._auth_service = SimpleNamespace(is_authenticated=lambda: True)  # type: ignore[attr-defined]

    def test_create_directory_workspace_first(self):
        # Workspace call returns a result with metadata
        fake_meta = make_meta("/WS/Folder", "Folder")
        self.service._workspace_handler.workspace_call = lambda path, func: SimpleNamespace(  # type: ignore[attr-defined]
            metadata=fake_meta
        )

        created = self.service.create_directory("/WS/Folder")
        assert created is not None
        assert created.path == "/WS/Folder"
        assert created.name == "Folder"

    def test_create_directory_fallback_regular(self):
        # Workspace returns None; regular client creates
        self.service._workspace_handler.workspace_call = lambda path, func: None  # type: ignore[attr-defined]
        fake_meta = make_meta("/Root/Folder", "Folder")
        self.service._client.files_create_folder_v2 = lambda path, autorename=False: SimpleNamespace(  # type: ignore[attr-defined]
            metadata=fake_meta
        )

        created = self.service.create_directory("/Root/Folder")
        assert created is not None
        assert created.path == "/Root/Folder"
        assert created.name == "Folder"

    def test_create_directory_tree_mixed(self):
        root = "/Root/Lease123"

        # Root exists
        self.service._get_metadata = lambda p: make_meta(root, "Lease123")  # type: ignore[attr-defined]

        # create_directory returns for Documents, raises for Runsheets (simulate exists)
        def fake_create(path: str, parents: bool = True):
            if path.endswith("Documents"):
                return SimpleNamespace(
                    path="/Root/Lease123/Documents", name="Documents", is_directory=True
                )
            raise Exception("exists")

        self.service.create_directory = fake_create  # type: ignore[method-assign]
        # Metadata for Runsheets present (exists_ok path)
        self.service._get_metadata = lambda p: make_meta(p, p.rsplit("/", 1)[-1])  # type: ignore[attr-defined]

        result = self.service.create_directory_tree(
            root, ["Documents", "Runsheets"], exists_ok=True
        )
        names = sorted([d.name for d in result])
        assert names == ["Documents", "Runsheets"]
