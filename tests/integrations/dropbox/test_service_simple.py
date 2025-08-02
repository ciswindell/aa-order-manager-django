"""
Simple tests for the simplified DropboxService.
Tests only the functionality actually used by workflows.
"""

import pytest
from unittest.mock import Mock, patch
from src.integrations.dropbox.service import (
    DropboxService,
    DropboxAuthenticationError,
    DropboxSearchError,
    DropboxListError
)


class TestDropboxServiceSimple:
    """Test the simplified DropboxService functionality."""
    
    @pytest.fixture
    def mock_auth_handler(self):
        """Mock authentication handler."""
        mock_handler = Mock()
        mock_handler.is_authenticated.return_value = True
        mock_handler.get_client.return_value = Mock()
        return mock_handler
    
    @pytest.fixture
    def dropbox_service(self, mock_auth_handler):
        """Create DropboxService with mocked authentication."""
        service = DropboxService(auth_handler=mock_auth_handler)
        service._client = Mock()  # Mock the Dropbox client
        return service
    
    def test_list_directory_files_success(self, dropbox_service):
        """Test successful file listing."""
        # Mock Dropbox API response
        mock_file = Mock()
        mock_file.name = "Master Documents.pdf"
        mock_file.size = 1234567
        mock_file.client_modified = None
        
        mock_folder = Mock()
        mock_folder.name = "Subfolder"
        # Folder doesn't have size attribute
        
        mock_result = Mock()
        mock_result.entries = [mock_file, mock_folder]
        mock_result.has_more = False
        
        dropbox_service._client.files_list_folder.return_value = mock_result
        
        # Test the method
        result = dropbox_service.list_directory_files("/Federal/NMNM 0501759")
        
        # Verify API call
        dropbox_service._client.files_list_folder.assert_called_once_with("/Federal/NMNM 0501759")
        
        # Verify results
        assert len(result) == 2
        
        # Check file entry
        file_entry = result[0]
        assert file_entry["name"] == "Master Documents.pdf"
        assert file_entry["path"] == "/Federal/NMNM 0501759/Master Documents.pdf"
        assert file_entry["is_file"] is True
        assert file_entry["size"] == 1234567
        
        # Check folder entry
        folder_entry = result[1]
        assert folder_entry["name"] == "Subfolder"
        assert folder_entry["path"] == "/Federal/NMNM 0501759/Subfolder"
        assert folder_entry["is_file"] is False
        assert "size" not in folder_entry  # Folders don't have size
    
    def test_list_directory_files_not_authenticated(self):
        """Test list_directory_files when not authenticated."""
        service = DropboxService()
        
        with pytest.raises(DropboxAuthenticationError, match="Service not authenticated"):
            service.list_directory_files("/test/path")
    
    def test_search_directory_with_metadata_success(self, dropbox_service):
        """Test successful directory search with metadata."""
        # Mock the internal methods
        dropbox_service._search_exact_directory_path = Mock(return_value="/Federal/NMNM 0501759")
        dropbox_service.get_shareable_link = Mock(return_value="https://dropbox.com/share/test")
        
        result = dropbox_service.search_directory_with_metadata("/Federal/NMNM 0501759")
        
        assert result["path"] == "/Federal/NMNM 0501759"
        assert result["shareable_link"] == "https://dropbox.com/share/test"
    
    def test_search_directory_with_metadata_not_found(self, dropbox_service):
        """Test directory search when directory not found."""
        # Mock the internal method to return None (not found)
        dropbox_service._search_exact_directory_path = Mock(return_value=None)
        
        result = dropbox_service.search_directory_with_metadata("/Federal/NOTFOUND")
        
        assert result["path"] is None
        assert result["shareable_link"] is None