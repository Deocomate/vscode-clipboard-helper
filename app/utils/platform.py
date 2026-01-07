"""
Platform detection utilities.
Provides consistent platform identification across the application.
"""

import sys
import platform


def is_windows() -> bool:
    """Check if the current platform is Windows."""
    return sys.platform == 'win32' or sys.platform == 'cygwin'


def is_macos() -> bool:
    """Check if the current platform is macOS."""
    return sys.platform == 'darwin'


def is_linux() -> bool:
    """Check if the current platform is Linux."""
    return sys.platform.startswith('linux')


def get_platform_name() -> str:
    """
    Get a human-readable platform name.
    
    Returns:
        'Windows', 'macOS', 'Linux', or the raw platform string
    """
    if is_windows():
        return 'Windows'
    elif is_macos():
        return 'macOS'
    elif is_linux():
        return 'Linux'
    else:
        return platform.system()


def get_os_version() -> str:
    """Get the OS version string."""
    return platform.version()


def get_python_version() -> str:
    """Get the Python version string."""
    return platform.python_version()
