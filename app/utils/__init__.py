"""
Utility modules for the VSCode Clipboard Helper application.
"""

from app.utils.platform import is_windows, is_macos, get_platform_name
from app.utils.resources import get_resource_path
from app.utils.path_utils import clean_path, text_to_files

__all__ = [
    'is_windows',
    'is_macos', 
    'get_platform_name',
    'get_resource_path',
    'clean_path',
    'text_to_files',
]
