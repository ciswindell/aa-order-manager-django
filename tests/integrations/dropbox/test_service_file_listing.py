"""
Unit Tests for DropboxService File Listing Capabilities

Tests the new list_directory_files method and related functionality including
pagination, team workspace handling, and comprehensive error scenarios.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import List, Dict, Any

from src.integrations.dropbox.service import (
    DropboxService,
    DropboxListError,
    DropboxAuthenticationError
)


class TestDropboxServiceFileListing:
    """Test DropboxService file listing functionality."""
    
    @pytest.fixture
    def mock_auth_handler(self):
        """Create a mock authentication handler."""
        auth_handler = Mock()
        auth_handler.is_authenticated.return_value = True
        auth_handler.get_client.return_value = Mock()
        return auth_handler
    
    @pytest.fixture
    def mock_config_manager(self):
        """Create a mock configuration manager."""
        return Mock()
    
    @pytest.fixture
    def dropbox_service(self, mock_auth_handler, mock_config_manager):
        """Create a DropboxService instance with mocked dependencies."""
        service = DropboxService(
            auth_handler=mock_auth_handler,
            config_manager=mock_config_manager
        )
        service._client = Mock()  # Mock the Dropbox client
        return service
    
    @pytest.fixture
    def sample_file_entries(self):
        """Create sample file entries for testing."""
        # Mock file entry
        file_entry = Mock()
        file_entry.name = "Master Documents.pdf"
        file_entry.path_display = "/Federal/NMNM 0501759/Master Documents.pdf"
        file_entry.id = "file_id_123"
        file_entry.tag = "file"
        file_entry.size = 1234567
        file_entry.server_modified = datetime(2024, 1, 15, 10, 30, 0)
        
        # Mock folder entry
        folder_entry = Mock()
        folder_entry.name = "Subfolder"
        folder_entry.path_display = "/Federal/NMNM 0501759/Subfolder"
        folder_entry.id = "folder_id_456"
        folder_entry.tag = "folder"
        
        return [file_entry, folder_entry]
    
    @pytest.fixture
    def sample_list_folder_result(self, sample_file_entries):
        """Create a sample list_folder API result."""
        result = Mock()
        result.entries = sample_file_entries
        result.has_more = False
        result.cursor = None
        return result

    def test_list_directory_files_not_authenticated(self, dropbox_service):
        """Test list_directory_files when not authenticated."""
        # Mock the service's is_authenticated method directly
        with patch.object(dropbox_service, 'is_authenticated', return_value=False):
            with pytest.raises(DropboxAuthenticationError, match="Service not authenticated"):
                dropbox_service.list_directory_files("/test/path")
    
    def test_list_directory_files_regular_path_success(self, dropbox_service, sample_list_folder_result):
        """Test successful file listing for regular path."""
        dropbox_service._client.files_list_folder.return_value = sample_list_folder_result
        
        result = dropbox_service.list_directory_files("/Regular/Path")
        
        # Verify API call
        dropbox_service._client.files_list_folder.assert_called_once_with("/Regular/Path")
        
        # Verify result structure
        assert len(result) == 2
        
        # Check file entry
        file_entry = result[0]
        assert file_entry["name"] == "Master Documents.pdf"
        assert file_entry["path"] == "/Regular/Path/Master Documents.pdf"
        assert file_entry["id"] == "file_id_123"
        assert file_entry["is_file"] is True
        assert file_entry["file_type"] == "pdf"
        assert file_entry["size"] == 1234567
        assert file_entry["modified"] == datetime(2024, 1, 15, 10, 30, 0)
        
        # Check folder entry
        folder_entry = result[1]
        assert folder_entry["name"] == "Subfolder"
        assert folder_entry["path"] == "/Federal/NMNM 0501759/Subfolder"
        assert folder_entry["id"] == "folder_id_456"
        assert folder_entry["is_file"] is False
        assert folder_entry["file_type"] == "folder"
        assert folder_entry["size"] is None
        assert folder_entry["modified"] is None
    
    def test_list_directory_files_strips_trailing_slash(self, dropbox_service, sample_list_folder_result):
        """Test that trailing slashes are properly stripped."""
        dropbox_service._client.files_list_folder.return_value = sample_list_folder_result
        
        dropbox_service.list_directory_files("/test/path/")
        
        # Verify trailing slash was stripped
        dropbox_service._client.files_list_folder.assert_called_once_with("/test/path")
    
    def test_list_directory_files_with_pagination(self, dropbox_service, sample_file_entries):
        """Test file listing with pagination."""
        # First page result
        first_result = Mock()
        first_result.entries = sample_file_entries[:1]  # First file
        first_result.has_more = True
        first_result.cursor = "cursor_123"
        
        # Second page result
        second_result = Mock()
        second_result.entries = sample_file_entries[1:]  # Second file
        second_result.has_more = False
        second_result.cursor = None
        
        dropbox_service._client.files_list_folder.return_value = first_result
        dropbox_service._client.files_list_folder_continue.return_value = second_result
        
        result = dropbox_service.list_directory_files("/test/path")
        
        # Verify pagination calls
        dropbox_service._client.files_list_folder.assert_called_once_with("/test/path")
        dropbox_service._client.files_list_folder_continue.assert_called_once_with("cursor_123")
        
        # Verify all entries are returned
        assert len(result) == 2
        assert result[0]["name"] == "Master Documents.pdf"
        assert result[1]["name"] == "Subfolder"
    
    def test_list_directory_files_federal_workspace(self, dropbox_service):
        """Test file listing for Federal Workspace path."""
        # Mock workspace namespace resolution
        shared_folders = Mock()
        workspace_folder = Mock()
        workspace_folder.name = "Federal Workspace"
        workspace_folder.shared_folder_id = "workspace_123"
        shared_folders.entries = [workspace_folder]
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        # Mock namespaced client
        namespaced_client = Mock()
        dropbox_service._client.with_path_root.return_value = namespaced_client
        
        # Mock list folder result
        result = Mock()
        result.entries = []
        result.has_more = False
        namespaced_client.files_list_folder.return_value = result
        
        dropbox_service.list_directory_files("/Federal Workspace/NMNM 0501759")
        
        # Verify workspace resolution
        dropbox_service._client.sharing_list_folders.assert_called_once()
        
        # Verify namespaced client creation and call
        dropbox_service._client.with_path_root.assert_called_once()
        namespaced_client.files_list_folder.assert_called_once_with("/NMNM 0501759")
    
    def test_list_directory_files_state_workspace(self, dropbox_service):
        """Test file listing for State Workspace path."""
        # Mock workspace namespace resolution
        shared_folders = Mock()
        workspace_folder = Mock()
        workspace_folder.name = "State Workspace"
        workspace_folder.shared_folder_id = "workspace_456"
        shared_folders.entries = [workspace_folder]
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        # Mock namespaced client
        namespaced_client = Mock()
        dropbox_service._client.with_path_root.return_value = namespaced_client
        
        # Mock list folder result
        result = Mock()
        result.entries = []
        result.has_more = False
        namespaced_client.files_list_folder.return_value = result
        
        dropbox_service.list_directory_files("/State Workspace/NMSLO 12345")
        
        # Verify workspace resolution
        dropbox_service._client.sharing_list_folders.assert_called_once()
        
        # Verify namespaced client creation and call
        dropbox_service._client.with_path_root.assert_called_once()
        namespaced_client.files_list_folder.assert_called_once_with("/NMSLO 12345")
    
    def test_list_directory_files_workspace_not_found(self, dropbox_service):
        """Test file listing when workspace is not found."""
        # Mock workspace namespace resolution with no matching workspace
        shared_folders = Mock()
        shared_folders.entries = [Mock(name="Other Workspace", shared_folder_id="other_123")]
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        with pytest.raises(DropboxListError, match="Could not find namespace for workspace"):
            dropbox_service.list_directory_files("/Federal Workspace/NMNM 0501759")
    
    def test_list_directory_files_workspace_with_pagination(self, dropbox_service, sample_file_entries):
        """Test workspace file listing with pagination."""
        # Mock workspace namespace resolution
        shared_folders = Mock()
        workspace_folder = Mock()
        workspace_folder.name = "Federal Workspace"
        workspace_folder.shared_folder_id = "workspace_123"
        shared_folders.entries = [workspace_folder]
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        # Mock namespaced client
        namespaced_client = Mock()
        dropbox_service._client.with_path_root.return_value = namespaced_client
        
        # First page result
        first_result = Mock()
        first_result.entries = sample_file_entries[:1]
        first_result.has_more = True
        first_result.cursor = "ws_cursor_123"
        
        # Second page result
        second_result = Mock()
        second_result.entries = sample_file_entries[1:]
        second_result.has_more = False
        second_result.cursor = None
        
        namespaced_client.files_list_folder.return_value = first_result
        namespaced_client.files_list_folder_continue.return_value = second_result
        
        result = dropbox_service.list_directory_files("/Federal Workspace/NMNM 0501759")
        
        # Verify pagination calls
        namespaced_client.files_list_folder.assert_called_once_with("/NMNM 0501759")
        namespaced_client.files_list_folder_continue.assert_called_once_with("ws_cursor_123")
        
        # Verify all entries are returned with workspace prefix
        assert len(result) == 2
        assert result[0]["path"] == "/Federal Workspace/Federal/NMNM 0501759/Master Documents.pdf"
        assert result[1]["path"] == "/Federal Workspace/Federal/NMNM 0501759/Subfolder"
    
    def test_list_directory_files_empty_directory(self, dropbox_service):
        """Test file listing for empty directory."""
        # Mock empty result
        result = Mock()
        result.entries = []
        result.has_more = False
        dropbox_service._client.files_list_folder.return_value = result
        
        files = dropbox_service.list_directory_files("/empty/directory")
        
        assert files == []
        dropbox_service._client.files_list_folder.assert_called_once_with("/empty/directory")
    
    def test_list_directory_files_api_error(self, dropbox_service):
        """Test file listing when Dropbox API raises an error."""
        dropbox_service._client.files_list_folder.side_effect = Exception("API Error")
        
        with pytest.raises(DropboxListError, match="Failed to list directory '/test/path': API Error"):
            dropbox_service.list_directory_files("/test/path")
    
    def test_list_directory_files_propagates_authentication_error(self, dropbox_service):
        """Test that DropboxAuthenticationError is properly propagated."""
        dropbox_service._client.files_list_folder.side_effect = DropboxAuthenticationError("Token expired")
        
        with pytest.raises(DropboxAuthenticationError, match="Token expired"):
            dropbox_service.list_directory_files("/test/path")
    
    def test_process_folder_entries_file_without_tag(self, dropbox_service):
        """Test processing entries that don't have a tag attribute."""
        # Mock entry without tag
        entry = Mock()
        entry.name = "document.txt"
        entry.path_display = "/path/document.txt"
        entry.id = "entry_123"
        entry.size = 1000
        entry.server_modified = datetime(2024, 1, 1)
        # Remove tag attribute
        if hasattr(entry, 'tag'):
            delattr(entry, 'tag')
        
        result = dropbox_service._process_folder_entries([entry])
        
        assert len(result) == 1
        assert result[0]["name"] == "document.txt"
        assert result[0]["is_file"] is True  # Should default to file
        assert result[0]["file_type"] == "txt"
    
    def test_process_folder_entries_with_path_prefix(self, dropbox_service, sample_file_entries):
        """Test processing entries with path prefix for workspaces."""
        result = dropbox_service._process_folder_entries(
            sample_file_entries, 
            path_prefix="/Federal Workspace"
        )
        
        assert len(result) == 2
        assert result[0]["path"] == "/Federal Workspace/Federal/NMNM 0501759/Master Documents.pdf"
        assert result[1]["path"] == "/Federal Workspace/Federal/NMNM 0501759/Subfolder"
    
    def test_process_folder_entries_skips_invalid_entries(self, dropbox_service):
        """Test that invalid entries are skipped gracefully."""
        # Mock entry that will cause an exception
        bad_entry = Mock()
        bad_entry.name = "bad_entry"
        # Make path_display property raise an exception
        type(bad_entry).path_display = property(lambda self: (_ for _ in ()).throw(Exception("Bad entry")))
        
        # Good entry
        good_entry = Mock()
        good_entry.name = "good_entry.txt"
        good_entry.path_display = "/path/good_entry.txt"
        good_entry.id = "good_123"
        good_entry.tag = "file"
        good_entry.size = 500
        
        result = dropbox_service._process_folder_entries([bad_entry, good_entry])
        
        # Should only return the good entry
        assert len(result) == 1
        assert result[0]["name"] == "good_entry.txt"
    
    def test_get_file_extension_various_formats(self, dropbox_service):
        """Test file extension extraction for various filename formats."""
        test_cases = [
            ("document.pdf", "pdf"),
            ("image.PNG", "png"),  # Should be lowercase
            ("archive.tar.gz", "gz"),  # Should get last extension
            ("README", "unknown"),  # No extension
            ("file.with.many.dots.txt", "txt"),
            ("", "unknown"),  # Empty filename
            (".hidden", "hidden"),  # Hidden file
            ("name.", ""),  # Ends with dot
        ]
        
        for filename, expected in test_cases:
            result = dropbox_service._get_file_extension(filename)
            assert result == expected, f"Failed for filename: {filename}"
    
    def test_get_workspace_namespace_id_success(self, dropbox_service):
        """Test successful workspace namespace ID retrieval."""
        # Mock shared folders response
        shared_folders = Mock()
        folder1 = Mock()
        folder1.name = "Other Workspace"
        folder1.shared_folder_id = "other_123"
        folder2 = Mock()
        folder2.name = "Federal Workspace"
        folder2.shared_folder_id = "federal_456"
        shared_folders.entries = [folder1, folder2]
        
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        namespace_id = dropbox_service._get_workspace_namespace_id("Federal Workspace")
        
        assert namespace_id == "federal_456"
        dropbox_service._client.sharing_list_folders.assert_called_once()
    
    def test_get_workspace_namespace_id_not_found(self, dropbox_service):
        """Test workspace namespace ID when workspace not found."""
        # Mock shared folders response without target workspace
        shared_folders = Mock()
        other_folder = Mock()
        other_folder.name = "Other Workspace"
        other_folder.shared_folder_id = "other_123"
        shared_folders.entries = [other_folder]
        
        dropbox_service._client.sharing_list_folders.return_value = shared_folders
        
        namespace_id = dropbox_service._get_workspace_namespace_id("Nonexistent Workspace")
        
        assert namespace_id is None
    
    def test_get_workspace_namespace_id_api_error(self, dropbox_service):
        """Test workspace namespace ID when API call fails."""
        dropbox_service._client.sharing_list_folders.side_effect = Exception("API Error")
        
        namespace_id = dropbox_service._get_workspace_namespace_id("Federal Workspace")
        
        assert namespace_id is None


class TestDropboxServiceFileListingIntegration:
    """Integration tests for file listing with multiple components."""
    
    @pytest.fixture
    def dropbox_service_with_auth(self):
        """Create a DropboxService instance that appears authenticated."""
        auth_handler = Mock()
        auth_handler.is_authenticated.return_value = True
        auth_handler.get_client.return_value = Mock()
        
        service = DropboxService(auth_handler=auth_handler)
        service._client = Mock()
        return service
    
    def test_large_directory_pagination_integration(self, dropbox_service_with_auth):
        """Test integration of pagination for large directories."""
        # Create multiple pages of results
        pages = []
        for i in range(3):  # 3 pages
            page_entries = []
            for j in range(10):  # 10 files per page
                entry = Mock()
                entry.name = f"file_{i}_{j}.pdf"
                entry.path_display = f"/test/file_{i}_{j}.pdf"
                entry.id = f"id_{i}_{j}"
                entry.tag = "file"
                entry.size = 1000 * (i + 1) * (j + 1)
                entry.server_modified = datetime(2024, 1, i + 1, j, 0, 0)
                page_entries.append(entry)
            
            page_result = Mock()
            page_result.entries = page_entries
            page_result.has_more = (i < 2)  # Last page has no more
            page_result.cursor = f"cursor_{i + 1}" if i < 2 else None
            pages.append(page_result)
        
        # Mock the API calls
        dropbox_service_with_auth._client.files_list_folder.return_value = pages[0]
        dropbox_service_with_auth._client.files_list_folder_continue.side_effect = pages[1:]
        
        result = dropbox_service_with_auth.list_directory_files("/large/directory")
        
        # Verify all files are returned
        assert len(result) == 30  # 3 pages * 10 files
        
        # Verify pagination was called correctly
        dropbox_service_with_auth._client.files_list_folder.assert_called_once_with("/large/directory")
        assert dropbox_service_with_auth._client.files_list_folder_continue.call_count == 2
        
        # Verify file ordering and data integrity
        for i in range(3):
            for j in range(10):
                file_index = i * 10 + j
                assert result[file_index]["name"] == f"file_{i}_{j}.pdf"
                assert result[file_index]["size"] == 1000 * (i + 1) * (j + 1)
    
    def test_mixed_file_types_processing(self, dropbox_service_with_auth):
        """Test processing directory with mixed file types and folders."""
        # Create diverse entry types
        entries = []
        
        # PDF file
        pdf_entry = Mock()
        pdf_entry.name = "Master Documents.pdf"
        pdf_entry.path_display = "/test/Master Documents.pdf"
        pdf_entry.id = "pdf_123"
        pdf_entry.tag = "file"
        pdf_entry.size = 2000000
        pdf_entry.server_modified = datetime(2024, 1, 15)
        entries.append(pdf_entry)
        
        # Word document
        doc_entry = Mock()
        doc_entry.name = "Report.docx"
        doc_entry.path_display = "/test/Report.docx"
        doc_entry.id = "doc_456"
        doc_entry.tag = "file"
        doc_entry.size = 500000
        doc_entry.server_modified = datetime(2024, 1, 16)
        entries.append(doc_entry)
        
        # Folder
        folder_entry = Mock()
        folder_entry.name = "Archive"
        folder_entry.path_display = "/test/Archive"
        folder_entry.id = "folder_789"
        folder_entry.tag = "folder"
        entries.append(folder_entry)
        
        # File without extension
        no_ext_entry = Mock()
        no_ext_entry.name = "README"
        no_ext_entry.path_display = "/test/README"
        no_ext_entry.id = "readme_101"
        no_ext_entry.tag = "file"
        no_ext_entry.size = 1500
        no_ext_entry.server_modified = datetime(2024, 1, 17)
        entries.append(no_ext_entry)
        
        # Mock result
        result = Mock()
        result.entries = entries
        result.has_more = False
        dropbox_service_with_auth._client.files_list_folder.return_value = result
        
        files = dropbox_service_with_auth.list_directory_files("/test")
        
        assert len(files) == 4
        
        # Verify PDF file
        pdf_file = next(f for f in files if f["name"] == "Master Documents.pdf")
        assert pdf_file["is_file"] is True
        assert pdf_file["file_type"] == "pdf"
        assert pdf_file["size"] == 2000000
        
        # Verify Word document
        doc_file = next(f for f in files if f["name"] == "Report.docx")
        assert doc_file["is_file"] is True
        assert doc_file["file_type"] == "docx"
        assert doc_file["size"] == 500000
        
        # Verify folder
        folder = next(f for f in files if f["name"] == "Archive")
        assert folder["is_file"] is False
        assert folder["file_type"] == "folder"
        assert folder["size"] is None
        
        # Verify file without extension
        readme_file = next(f for f in files if f["name"] == "README")
        assert readme_file["is_file"] is True
        assert readme_file["file_type"] == "unknown"
        assert readme_file["size"] == 1500


if __name__ == "__main__":
    pytest.main([__file__])