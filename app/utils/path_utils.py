"""
Path manipulation utilities.
Handles cleaning and parsing file paths from various sources.
"""

import os
import urllib.parse
from typing import List, Optional


def clean_path(raw_path: str) -> str:
    """
    Clean a path from VS Code or other sources.
    
    Handles:
    - Removing quotes
    - URL decoding (e.g., %20 -> space)
    - Removing file:// prefix
    - Normalizing path separators
    
    Args:
        raw_path: Raw path string that may contain URI encoding
        
    Returns:
        Cleaned, normalized path
    """
    # Remove surrounding quotes
    raw_path = raw_path.strip().strip('"').strip("'")
    
    # URL decode (e.g., %20 -> space, %3A -> :)
    decoded_path = urllib.parse.unquote(raw_path)
    
    # Handle file:// prefix
    if decoded_path.startswith("file:///"):
        # On Windows, file:///C:/path -> C:/path (remove 3 slashes)
        # On Unix, file:///path -> /path (keep leading /)
        from app.utils.platform import is_windows
        if is_windows():
            decoded_path = decoded_path[8:]  # Remove "file:///"
        else:
            decoded_path = decoded_path[7:]  # Remove "file://" keep leading /
    elif decoded_path.startswith("file://"):
        decoded_path = decoded_path[7:]
    
    # Normalize path separators for the current platform
    decoded_path = os.path.normpath(decoded_path)
    
    return decoded_path


def text_to_files(text: str) -> Optional[List[str]]:
    """
    Parse text content and extract valid file paths.
    
    VS Code may copy multiple files, separated by newlines.
    Each line is cleaned and validated.
    
    Args:
        text: Text that may contain file paths (one per line)
        
    Returns:
        List of valid, existing file paths, or None if none found
    """
    if not text:
        return None
    
    # Split by newlines and process each line
    lines = text.splitlines()
    valid_files = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        cleaned = clean_path(line)
        
        # Verify the path exists
        if os.path.exists(cleaned):
            valid_files.append(cleaned)
    
    return valid_files if valid_files else None


def is_absolute_path(path: str) -> bool:
    """
    Check if a path is absolute.
    
    Args:
        path: Path string to check
        
    Returns:
        True if the path is absolute
    """
    return os.path.isabs(path)


def normalize_path_separators(path: str) -> str:
    """
    Normalize path separators to the current platform's style.
    
    Args:
        path: Path with potentially mixed separators
        
    Returns:
        Path with consistent separators
    """
    return os.path.normpath(path)
