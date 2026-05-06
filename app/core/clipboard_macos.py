"""
macOS-specific clipboard handler implementation.
Uses PyObjC (Cocoa framework) for clipboard operations.
"""

from typing import List, Optional
import logging
import subprocess

# macOS-specific imports
from AppKit import NSPasteboard, NSFilenamesPboardType, NSPasteboardTypeString
from Foundation import NSURL

from app.core.clipboard_base import ClipboardHandlerBase

logger = logging.getLogger(__name__)

# Debug mode flag
DEBUG = False


class MacOSClipboardHandler(ClipboardHandlerBase):
    """macOS implementation of clipboard handler using PyObjC."""

    # macOS pasteboard type constants
    FILE_URL_TYPE = "public.file-url"
    FILE_NAMES_TYPE = NSFilenamesPboardType

    def __init__(self):
        super().__init__()
        self._pasteboard = NSPasteboard.generalPasteboard()

    def open_clipboard(self) -> bool:
        """
        Open the clipboard for reading.
        On macOS, the pasteboard is always accessible, no explicit open needed.
        """
        return True

    def close_clipboard(self) -> None:
        """
        Close the clipboard.
        On macOS, no explicit close is needed.
        """
        pass

    def has_file_drop(self) -> bool:
        """Check if pasteboard has file names (native file format)."""
        try:
            types = self._pasteboard.types()
            if types is None:
                return False
            # Check for native file types
            return (NSFilenamesPboardType in types or 
                    self.FILE_URL_TYPE in types)
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error checking file drop: {e}")
            return False

    def get_custom_format_data(self, format_name: str) -> Optional[str]:
        """Read data from a custom pasteboard type."""
        try:
            types = self._pasteboard.types()
            if types and format_name in types:
                data = self._pasteboard.dataForType_(format_name)
                if data:
                    # Try to decode as UTF-8 string
                    try:
                        return data.bytes().tobytes().decode('utf-8')
                    except (UnicodeDecodeError, AttributeError):
                        pass
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading {format_name}: {e}")
        return None

    def get_text_data(self) -> Optional[str]:
        """Get plain text from pasteboard."""
        try:
            text = self._pasteboard.stringForType_(NSPasteboardTypeString)
            return text if text else None
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading text data: {e}")
            return None

    def set_clipboard_files(self, file_list: List[str]) -> bool:
        """
        Write file paths to pasteboard using NSFilenamesPboardType.
        This allows pasting files into Finder and other macOS apps.
        """
        try:
            # Clear and declare types
            self._pasteboard.clearContents()

            # Create file URLs
            file_urls = []
            for path in file_list:
                url = NSURL.fileURLWithPath_(path)
                if url:
                    file_urls.append(url)

            if not file_urls:
                logger.warning("No valid file URLs created")
                return False

            # Write file URLs to pasteboard
            success = self._pasteboard.writeObjects_(file_urls)

            if success:
                logger.info(f"Converted {len(file_list)} paths to file objects in clipboard.")
                return True
            else:
                logger.error("Failed to write files to pasteboard")
                return False

        except Exception as e:
            logger.error(f"Error writing to clipboard: {e}")
            return False

    def set_clipboard_text(self, text: str) -> bool:
        """Write plain text to pasteboard."""
        try:
            self._pasteboard.clearContents()
            success = self._pasteboard.setString_forType_(text, NSPasteboardTypeString)
            if success:
                logger.info("Successfully wrote text to pasteboard.")
                return True
            else:
                logger.error("Failed to write text to pasteboard")
                return False
        except Exception as e:
            logger.error(f"Error writing text to clipboard: {e}")
            return False

    def get_file_urls_from_pasteboard(self) -> Optional[List[str]]:
        """
        Read file paths from pasteboard if available.
        Useful for debugging pasteboard contents.
        """
        try:
            # Try NSFilenamesPboardType first
            types = self._pasteboard.types()
            if types and NSFilenamesPboardType in types:
                files = self._pasteboard.propertyListForType_(NSFilenamesPboardType)
                if files:
                    return list(files)

            # Try public.file-url
            if types and self.FILE_URL_TYPE in types:
                data = self._pasteboard.dataForType_(self.FILE_URL_TYPE)
                if data:
                    url_str = data.bytes().tobytes().decode('utf-8')
                    from app.utils.path_utils import clean_path
                    return [clean_path(url_str)]

        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading file URLs: {e}")
        return None
