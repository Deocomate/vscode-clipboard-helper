"""
Abstract base class for clipboard operations.
Defines the interface that platform-specific implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ClipboardHandlerBase(ABC):
    """
    Abstract base class defining the interface for clipboard operations.
    Each platform (Windows, macOS) must provide its own implementation.
    """

    # Common clipboard format names used by Electron apps (VS Code, Atom, etc.)
    ELECTRON_URI_LIST = "text/uri-list"
    VSCODE_EDITOR_DROP = "vscode-editor-drop"
    VSCODE_FILE_LIST = "code/file-list"
    ATOM_URI_LIST = "atom-uri-list"

    def __init__(self):
        self.last_clipboard_content = ""

    @abstractmethod
    def open_clipboard(self) -> bool:
        """
        Open the clipboard for reading/writing.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def close_clipboard(self) -> None:
        """Close the clipboard."""
        pass

    @abstractmethod
    def has_file_drop(self) -> bool:
        """
        Check if the clipboard already contains native file drop format.
        Windows: CF_HDROP
        macOS: NSFilenamesPboardType
        """
        pass

    @abstractmethod
    def get_custom_format_data(self, format_name: str) -> Optional[str]:
        """
        Read data from a custom clipboard format.
        
        Args:
            format_name: The name of the custom format (e.g., 'code/file-list')
            
        Returns:
            The format data as string, or None if not available
        """
        pass

    @abstractmethod
    def get_text_data(self) -> Optional[str]:
        """
        Get plain text data from the clipboard.
        
        Returns:
            Text content or None if not available
        """
        pass

    @abstractmethod
    def set_clipboard_files(self, file_list: List[str]) -> bool:
        """
        Write file paths to clipboard in native file drop format.
        
        Args:
            file_list: List of absolute file paths
            
        Returns:
            True if successful, False otherwise
        """
        pass

    def extract_file_paths_from_clipboard(self) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Extract file paths from clipboard using various formats.
        This is the main method called by the monitor loop.
        
        Returns:
            Tuple of (file_list, source_format) or (None, None) if no files found
        """
        from app.utils.path_utils import text_to_files

        # If clipboard already has native file drop, no conversion needed
        if self.has_file_drop():
            return None, None

        # Try each format in priority order
        formats_to_try = [
            self.VSCODE_FILE_LIST,
            self.ELECTRON_URI_LIST,
            self.VSCODE_EDITOR_DROP,
            self.ATOM_URI_LIST,
        ]

        for format_name in formats_to_try:
            data = self.get_custom_format_data(format_name)
            if data:
                file_list = text_to_files(data)
                if file_list:
                    return file_list, format_name

        # Fallback: try plain text that looks like file paths
        text_data = self.get_text_data()
        if text_data:
            # Only process if text contains file:// URI or looks like absolute path
            if 'file://' in text_data or self._looks_like_path(text_data):
                file_list = text_to_files(text_data)
                if file_list:
                    return file_list, 'TEXT'

        return None, None

    def _looks_like_path(self, text: str) -> bool:
        """
        Check if text looks like an absolute file path.
        Platform-specific implementation recommended.
        """
        from app.utils.platform import is_windows
        
        if is_windows():
            # Windows: check for drive letter like C:\
            return len(text) > 2 and text[1] == ':'
        else:
            # Unix-like: check for leading /
            return text.startswith('/')

    def should_process_content(self, content_key: str) -> bool:
        """
        Check if the content should be processed (hasn't been processed before).
        
        Args:
            content_key: A unique key representing the current clipboard content
            
        Returns:
            True if this is new content that should be processed
        """
        if content_key != self.last_clipboard_content:
            self.last_clipboard_content = content_key
            return True
        return False

    def mark_as_converted(self, content_key: str) -> None:
        """Mark content as converted to avoid re-processing."""
        self.last_clipboard_content = content_key + "_converted"
