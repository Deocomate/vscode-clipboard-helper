"""
Resource path utilities.
Handles finding resources when running from source or as a bundled executable.
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works for dev and for PyInstaller.
    
    When running as a PyInstaller bundle, resources are extracted to a 
    temporary folder whose path is stored in sys._MEIPASS.
    
    Args:
        relative_path: Path relative to the application root or bundle
        
    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in development mode
        base_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    return os.path.join(base_path, relative_path)


def get_icon_path(icon_name: str = None) -> str:
    """
    Get the path to the application icon.
    
    Args:
        icon_name: Optional specific icon filename. If None, uses platform default.
        
    Returns:
        Path to the icon file
    """
    from app.utils.platform import is_windows, is_macos
    
    if icon_name:
        return get_resource_path(icon_name)
    
    # Platform-specific defaults
    if is_windows():
        return get_resource_path("icon.ico")
    elif is_macos():
        # Try .icns first, fall back to .png
        icns_path = get_resource_path("icon.icns")
        if os.path.exists(icns_path):
            return icns_path
        return get_resource_path("icon.png")
    else:
        return get_resource_path("icon.png")


def resource_exists(relative_path: str) -> bool:
    """Check if a resource exists."""
    return os.path.exists(get_resource_path(relative_path))
