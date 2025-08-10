"""
Cloud-agnostic data models for file and sharing operations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CloudFile:
    """Represents a file or directory in cloud storage."""
    
    path: str
    name: str
    is_directory: bool
    file_id: Optional[str] = None
    size: Optional[int] = None
    modified_date: Optional[datetime] = None
    share_link: Optional['ShareLink'] = None
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.path:
            raise ValueError("Path cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")


@dataclass
class ShareLink:
    """Represents a shareable link for a cloud file."""
    
    url: str
    expires_at: Optional[datetime] = None
    is_public: bool = True
    
    def __post_init__(self):
        """Validate required fields."""
        if not self.url:
            raise ValueError("URL cannot be empty") 