"""
Cloud-agnostic protocol interfaces for cloud operations.

These protocols define the interface contracts that cloud service implementations
must follow to ensure compatibility across different providers.
"""

from typing import Protocol, Optional
from .models import CloudFile, ShareLink


class CloudAuthentication(Protocol):
    """Protocol for cloud service authentication operations."""
    
    def authenticate(self) -> bool:
        """Authenticate with the cloud service.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        ...
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated with the cloud service.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        ...


class CloudOperations(Protocol):
    """Protocol for all cloud operations (files, directories, sharing)."""
    
    def list_files(self, directory_path: str, recursive: bool = False) -> list[CloudFile]:
        """List files in the specified directory.
        
        Args:
            directory_path: The directory path to list
            recursive: If True, include all subdirectories (not implemented yet)
            
        Returns:
            list[CloudFile]: List of files (not directories)
            
        Raises:
            NotImplementedError: If recursive=True (not yet supported)
        """
        if recursive:
            raise NotImplementedError("Recursive listing not yet implemented")
        ...
    
    def list_directories(self, directory_path: str, recursive: bool = False) -> list[CloudFile]:
        """List directories in the specified directory.
        
        Args:
            directory_path: The directory path to list
            recursive: If True, include all subdirectories (not implemented yet)
            
        Returns:
            list[CloudFile]: List of directories (not files)
            
        Raises:
            NotImplementedError: If recursive=True (not yet supported)
        """
        if recursive:
            raise NotImplementedError("Recursive listing not yet implemented")
        ...
    
    def create_share_link(self, file_path: str, is_public: bool = True) -> Optional[ShareLink]:
        """Create a shareable link for a file or directory.
        
        Args:
            file_path: The path of the file/directory to share
            is_public: Whether the link should be publicly accessible
            
        Returns:
            Optional[ShareLink]: The share link if created successfully, None otherwise
        """
        ...
    
    def create_directory(self, path: str) -> Optional[CloudFile]:
        """Create a new directory at the specified path.
        
        Args:
            path: The path where the directory should be created
            
        Returns:
            Optional[CloudFile]: The created directory if successful, None otherwise
        """
        ... 