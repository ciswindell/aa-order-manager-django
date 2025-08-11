"""
Generic cloud error types and mapping utilities.

This module provides cloud-agnostic error classes that can be mapped from
provider-specific exceptions (e.g., dropbox.exceptions.ApiError).
"""

from typing import Optional, Dict, Type, Any
from datetime import datetime


class CloudServiceError(Exception):
    """Base exception for all cloud service errors."""
    
    def __init__(self, message: str, provider: str = "unknown", original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = f"[{self.provider}] {super().__str__()}"
        if self.original_error:
            base_msg += f" (Original: {type(self.original_error).__name__}: {self.original_error})"
        return base_msg


class CloudAuthError(CloudServiceError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str, provider: str = "unknown", original_error: Optional[Exception] = None):
        super().__init__(f"Authentication error: {message}", provider, original_error)


class CloudNotFoundError(CloudServiceError):
    """Exception raised when a file or directory is not found."""
    
    def __init__(self, path: str, provider: str = "unknown", original_error: Optional[Exception] = None):
        super().__init__(f"Not found: {path}", provider, original_error)
        self.path = path


class CloudPermissionError(CloudServiceError):
    """Exception raised for permission-related errors."""
    
    def __init__(self, message: str, provider: str = "unknown", original_error: Optional[Exception] = None):
        super().__init__(f"Permission error: {message}", provider, original_error)


class CloudRateLimitError(CloudServiceError):
    """Exception raised for rate limiting errors."""
    
    def __init__(self, message: str, provider: str = "unknown", original_error: Optional[Exception] = None):
        super().__init__(f"Rate limit error: {message}", provider, original_error)


# Error mapping utilities
def map_provider_error(error: Exception, provider: str) -> CloudServiceError:
    """Map provider-specific exceptions to generic cloud errors.
    
    Args:
        error: The original provider exception
        provider: The cloud provider name (e.g., "dropbox")
        
    Returns:
        CloudServiceError: Mapped generic cloud error
    """
    error_msg = str(error)
    
    # Map common error patterns
    if "not found" in error_msg.lower() or "doesn't exist" in error_msg.lower():
        # Try to extract path from error message
        path = extract_path_from_error(error_msg)
        return CloudNotFoundError(path or "unknown path", provider, error)
    
    elif "auth" in error_msg.lower() or "token" in error_msg.lower():
        return CloudAuthError(error_msg, provider, error)
    
    elif "permission" in error_msg.lower() or "access" in error_msg.lower():
        return CloudPermissionError(error_msg, provider, error)
    
    elif "rate limit" in error_msg.lower() or "too many requests" in error_msg.lower():
        return CloudRateLimitError(error_msg, provider, error)
    
    else:
        return CloudServiceError(error_msg, provider, error)


def extract_path_from_error(error_msg: str) -> Optional[str]:
    """Extract file path from error message if possible."""
    # Simple extraction - can be enhanced based on provider error formats
    if "path" in error_msg.lower():
        # Look for path-like patterns in the error message
        import re
        path_pattern = r'["\']([^"\']*[/\\][^"\']*)["\']'
        match = re.search(path_pattern, error_msg)
        if match:
            return match.group(1)
    return None


# Provider-specific error mapping functions
def map_dropbox_error(error: Exception) -> CloudServiceError:
    """Map Dropbox-specific exceptions to generic cloud errors."""
    return map_provider_error(error, "dropbox")


def map_google_drive_error(error: Exception) -> CloudServiceError:
    """Map Google Drive-specific exceptions to generic cloud errors."""
    return map_provider_error(error, "google_drive") 