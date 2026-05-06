"""
System tray icon management.
Provides cross-platform tray icon functionality using pystray.
"""

import os
import threading
import logging
from typing import Callable, Optional

import pystray
import queue
from PIL import Image, ImageDraw

from app.utils.resources import get_resource_path
from app.utils.platform import is_macos, is_windows

logger = logging.getLogger(__name__)


class TrayIcon:
    """
    Manages the system tray icon for the application.
    Works on both Windows and macOS using pystray.
    
    Note: On macOS, pystray.Icon.run() must be called on the main thread.
    On Windows, it can run in a background thread.
    """

    def __init__(
        self,
        app_name: str = "VSCodeBridge",
        tooltip: str = "VS Code Clipboard Helper",
        tray_queue: Optional[queue.Queue] = None
    ):
        """
        Initialize the tray icon.
        
        Args:
            app_name: Internal name for the icon
            tooltip: Tooltip text shown on hover
            tray_queue: Queue used to communicate with the main thread
        """
        self.app_name = app_name
        self.tooltip = tooltip
        self.tray_queue = tray_queue
        
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def create_icon_image(self) -> Image.Image:
        """
        Create or load the tray icon image.
        
        Returns:
            PIL Image for the tray icon
        """
        # Try to load icon from file
        icon_path = get_resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                img = Image.open(icon_path)
                # Resize for tray icon (typically 22x22 on macOS, 16x16 or 32x32 on Windows)
                if is_macos():
                    img = img.resize((22, 22), Image.Resampling.LANCZOS)
                else:
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                return img
            except Exception as e:
                logger.error(f"Cannot load icon.png: {e}")
        
        # Fallback: create a simple blue icon
        size = 22 if is_macos() else 32
        image = Image.new('RGB', (size, size), 'blue')
        draw = ImageDraw.Draw(image)
        margin = size // 4
        draw.rectangle((margin, margin, size - margin, size - margin), fill='white')
        return image

    def _create_menu(self) -> pystray.Menu:
        """Create the tray icon context menu."""
        if is_macos():
            # macOS menu items
            return pystray.Menu(
                pystray.MenuItem('Show Window', self._handle_show_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('Quit', self._handle_quit)
            )
        else:
            # Windows menu items (Vietnamese text for consistency with original)
            return pystray.Menu(
                pystray.MenuItem('Hiện giao diện', self._handle_show_window),
                pystray.MenuItem('Thoát', self._handle_quit)
            )

    def _handle_show_window(self, icon=None, item=None):
        """Handle the show window menu item."""
        if self.tray_queue:
            self.tray_queue.put("SHOW_WINDOW")

    def _handle_quit(self, icon=None, item=None):
        """Handle the quit menu item."""
        self.stop()
        if self.tray_queue:
            self.tray_queue.put("QUIT")

    def _run_icon(self):
        """Run the tray icon (called in a separate thread on Windows)."""
        self._icon = pystray.Icon(
            self.app_name,
            self.create_icon_image(),
            self.tooltip,
            self._create_menu()
        )
        self._icon.run()

    def start(self):
        """
        Start the tray icon.
        On Windows: runs in a background thread
        On macOS: must be called from main thread, blocks until stopped
        """
        if is_windows():
            # Windows can run tray in background thread
            self._thread = threading.Thread(target=self._run_icon, daemon=True)
            self._thread.start()
        else:
            # macOS: create icon but don't run yet
            # The icon will be run by the main application
            self._icon = pystray.Icon(
                self.app_name,
                self.create_icon_image(),
                self.tooltip,
                self._create_menu()
            )

    def run_detached(self, setup_callback: Optional[Callable] = None):
        """
        Run the tray icon with a setup callback (for macOS).
        This runs the icon's event loop and calls the callback in a background thread.
        
        Args:
            setup_callback: Function to call after icon is set up (runs in thread)
        """
        if self._icon:
            self._icon.run_detached()
            if setup_callback:
                setup_callback()

    def run(self):
        """Run the tray icon's main loop (blocking)."""
        if self._icon:
            self._icon.run()

    def stop(self):
        """Stop and remove the tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None

    def update_icon(self, image: Image.Image):
        """
        Update the tray icon image.
        
        Args:
            image: New PIL Image for the icon
        """
        if self._icon:
            self._icon.icon = image

    def update_tooltip(self, tooltip: str):
        """
        Update the tray icon tooltip.
        
        Args:
            tooltip: New tooltip text
        """
        if self._icon:
            self._icon.title = tooltip

