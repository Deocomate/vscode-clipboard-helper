"""
Clipboard utilities package.
Provides cross-platform clipboard monitoring and file operations.
"""

from app.utils.platform import is_windows, is_macos

def get_clipboard_handler():
    """
    Factory function to get the platform-specific clipboard handler.
    Returns the appropriate implementation based on the current OS.
    """
    if is_windows():
        from app.core.clipboard_windows import WindowsClipboardHandler
        return WindowsClipboardHandler()
    elif is_macos():
        from app.core.clipboard_macos import MacOSClipboardHandler
        return MacOSClipboardHandler()
    else:
        raise NotImplementedError(f"Clipboard handling not supported on this platform")

__all__ = ['get_clipboard_handler']
