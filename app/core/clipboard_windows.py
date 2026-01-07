"""
Windows-specific clipboard handler implementation.
Uses pywin32 and ctypes for clipboard operations.
"""

import ctypes
from ctypes import wintypes
from typing import List, Optional
import logging

# Windows-specific imports - only available on Windows
import win32clipboard
import win32con

from app.core.clipboard_base import ClipboardHandlerBase

logger = logging.getLogger(__name__)

# Debug mode flag
DEBUG = False


class DROPFILES(ctypes.Structure):
    """Windows DROPFILES structure for CF_HDROP clipboard format."""
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt", wintypes.POINT),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


class WindowsClipboardHandler(ClipboardHandlerBase):
    """Windows implementation of clipboard handler using pywin32."""

    def __init__(self):
        super().__init__()
        self._clipboard_open = False

    def open_clipboard(self) -> bool:
        """Open the Windows clipboard."""
        try:
            win32clipboard.OpenClipboard()
            self._clipboard_open = True
            return True
        except Exception as e:
            if DEBUG:
                logger.debug(f"Failed to open clipboard: {e}")
            return False

    def close_clipboard(self) -> None:
        """Close the Windows clipboard."""
        if self._clipboard_open:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            self._clipboard_open = False

    def has_file_drop(self) -> bool:
        """Check if clipboard has CF_HDROP format (Windows file drop)."""
        try:
            return win32clipboard.IsClipboardFormatAvailable(win32con.CF_HDROP)
        except Exception:
            return False

    def _get_registered_format_id(self, format_name: str) -> int:
        """Register or get ID of a custom clipboard format."""
        return ctypes.windll.user32.RegisterClipboardFormatW(format_name)

    def get_custom_format_data(self, format_name: str) -> Optional[str]:
        """Read data from a custom Windows clipboard format."""
        try:
            format_id = self._get_registered_format_id(format_name)
            if win32clipboard.IsClipboardFormatAvailable(format_id):
                data = win32clipboard.GetClipboardData(format_id)
                if isinstance(data, bytes):
                    # Try multiple encodings
                    for encoding in ['utf-8', 'utf-16', 'latin-1']:
                        try:
                            return data.decode(encoding)
                        except (UnicodeDecodeError, LookupError):
                            continue
                return data
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading {format_name}: {e}")
        return None

    def get_text_data(self) -> Optional[str]:
        """Get Unicode text from clipboard."""
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        except Exception as e:
            if DEBUG:
                logger.debug(f"Error reading text data: {e}")
        return None

    def set_clipboard_files(self, file_list: List[str]) -> bool:
        """
        Write file paths to clipboard using CF_HDROP format.
        This allows pasting files into Windows Explorer and other apps.
        """
        try:
            # Calculate buffer size
            offset = ctypes.sizeof(DROPFILES)
            length = sum(len(f) + 1 for f in file_list) + 1
            size = offset + length * ctypes.sizeof(wintypes.WCHAR)

            # Create buffer
            buf = (ctypes.c_char * size)()
            df = DROPFILES.from_buffer(buf)
            df.pFiles = offset
            df.fWide = True  # Unicode

            # Write file paths to buffer
            current_offset = offset
            for f in file_list:
                array_t = ctypes.c_wchar * (len(f) + 1)
                path_buf = array_t.from_buffer(buf, current_offset)
                path_buf.value = f
                current_offset += ctypes.sizeof(path_buf)

            # Null terminator
            buf[current_offset] = b'\0'
            buf[current_offset + 1] = b'\0'

            # Write to clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_HDROP, buf)
            win32clipboard.CloseClipboard()

            logger.info(f"Converted {len(file_list)} paths to file objects in clipboard.")
            return True

        except Exception as e:
            logger.error(f"Error writing to clipboard: {e}")
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            return False
