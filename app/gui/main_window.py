"""
Main application window.
Provides the Tkinter-based GUI for the VSCode Clipboard Helper.

Uses main-thread polling on macOS to avoid PyObjC/GIL threading issues.
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk

from app.core import get_clipboard_handler
from app.gui.tray_icon import TrayIcon
from app.utils.resources import get_resource_path
from app.utils.platform import is_windows, is_macos

logger = logging.getLogger(__name__)

# Polling interval in milliseconds
POLL_INTERVAL_MS = 500


class VSCodeBridgeApp:
    """
    Main application class for the VS Code Clipboard Helper.
    
    Provides a simple GUI with:
    - Status indicator
    - Start/Stop toggle button
    - System tray icon for background operation
    - Dock icon visibility toggle (macOS only)
    """

    def __init__(self):
        self.is_running = False
        self._poll_job = None
        self.clipboard_handler = None
        self._show_in_dock = False  # macOS dock visibility
        
        # Flags for cross-thread communication (pystray -> tkinter)
        self._pending_show_window = False
        self._pending_quit = False
        
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("VS Code Clipboard Helper")
        self.root.geometry("320x180")
        self.root.resizable(False, False)
        
        # Handle window close -> minimize to tray
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # Setup UI components
        self._setup_ui()
        self._setup_window_icon()
        
        # Setup tray icon (uses flags instead of direct callbacks to avoid GIL issues)
        self.tray = TrayIcon(
            app_name="VSCodeClipboardHelper",
            tooltip="VS Code Clipboard Helper",
            on_show_window=self._request_show_window,
            on_quit=self._request_quit
        )
        
        # Platform-specific initialization
        if is_macos():
            # Defer dock visibility and start flag polling
            self.root.after(100, lambda: self._set_dock_visibility(False))
            self._start_tray_flag_polling()
        
        # Start tray icon
        self.tray.start()

    def _setup_ui(self):
        """Setup the main UI components."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        status_text = "Status: Stopped" if not is_windows() else "Trạng thái: Đang dừng"
        self.status_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground="red",
            font=("Helvetica", 10, "bold")
        )
        self.status_label.pack(pady=10)
        
        # Toggle button
        button_text = "Start Monitoring" if not is_windows() else "Bật Tool"
        self.toggle_btn = ttk.Button(
            main_frame,
            text=button_text,
            command=self.toggle_monitoring
        )
        self.toggle_btn.pack(pady=5, fill=tk.X)
        
        # Instructions
        if is_macos():
            instruction = "Copy files in VS Code (Cmd+C) → Paste into Finder or other apps."
        else:
            instruction = "Chọn file trong VS Code → Ctrl+C → Paste vào nơi cần."
        
        note = ttk.Label(
            main_frame,
            text=instruction,
            font=("Helvetica", 9),
            wraplength=280,
            justify="center"
        )
        note.pack(pady=10)
        
        # macOS: Add dock visibility checkbox
        if is_macos():
            self._dock_var = tk.BooleanVar(value=False)
            self.dock_checkbox = ttk.Checkbutton(
                main_frame,
                text="Show in Dock",
                variable=self._dock_var,
                command=self._on_dock_checkbox_changed
            )
            self.dock_checkbox.pack(pady=5)

    def _setup_window_icon(self):
        """Set the window icon if available."""
        if is_windows():
            icon_path = get_resource_path("icon.ico")
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except Exception:
                    pass
        else:
            # macOS/Linux: try to set icon via iconphoto
            icon_path = get_resource_path("icon.png")
            if os.path.exists(icon_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, photo)
                    # Keep reference to prevent garbage collection
                    self._icon_photo = photo
                except Exception:
                    pass

    # ===== Cross-thread communication (pystray -> tkinter) =====
    
    def _request_show_window(self):
        """Set flag to show window (called from pystray thread)."""
        self._pending_show_window = True
    
    def _request_quit(self):
        """Set flag to quit (called from pystray thread)."""
        self._pending_quit = True
    
    def _start_tray_flag_polling(self):
        """Start polling for tray icon flags (macOS only)."""
        self._check_tray_flags()
    
    def _check_tray_flags(self):
        """Check and handle pending tray icon requests."""
        if self._pending_show_window:
            self._pending_show_window = False
            self._deiconify_window()
        
        if self._pending_quit:
            self._pending_quit = False
            self._destroy_app()
            return  # Don't schedule next check
        
        # Continue polling
        self.root.after(100, self._check_tray_flags)

    def _show_window_from_tray(self):
        """Show the main window from tray icon callback (Windows only)."""
        self.root.after(0, self._deiconify_window)

    def _deiconify_window(self):
        """Restore and focus the main window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit_from_tray(self):
        """Quit the application from tray icon (Windows only)."""
        self.root.after(0, self._destroy_app)

    def _destroy_app(self):
        """Clean up and exit the application."""
        self.is_running = False
        if self._poll_job:
            self.root.after_cancel(self._poll_job)
            self._poll_job = None
        self.tray.stop()
        self.root.destroy()
        sys.exit(0)

    def hide_window(self):
        """Hide the main window (minimize to tray)."""
        self.root.withdraw()

    def toggle_monitoring(self):
        """Toggle the clipboard monitoring on/off."""
        if not self.is_running:
            self._start_monitoring()
        else:
            self._stop_monitoring()

    def _start_monitoring(self):
        """Start clipboard monitoring using main-thread polling."""
        self.is_running = True
        
        # Update UI
        if is_windows():
            self.status_label.config(text="Trạng thái: Đang chạy ngầm", foreground="green")
            self.toggle_btn.config(text="Dừng Tool")
        else:
            self.status_label.config(text="Status: Running", foreground="green")
            self.toggle_btn.config(text="Stop Monitoring")
        
        # Initialize clipboard handler
        self.clipboard_handler = get_clipboard_handler()
        
        logger.info("Started clipboard monitoring...")
        
        # Start main-thread polling (avoids GIL issues with PyObjC on macOS)
        self._schedule_clipboard_poll()

    def _stop_monitoring(self):
        """Stop clipboard monitoring."""
        self.is_running = False
        
        # Cancel pending poll job
        if self._poll_job:
            self.root.after_cancel(self._poll_job)
            self._poll_job = None
        
        # Update UI
        if is_windows():
            self.status_label.config(text="Trạng thái: Đang dừng", foreground="red")
            self.toggle_btn.config(text="Bật Tool")
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            self.toggle_btn.config(text="Start Monitoring")

    def _schedule_clipboard_poll(self):
        """Schedule the next clipboard poll on the main thread."""
        if self.is_running:
            self._poll_job = self.root.after(POLL_INTERVAL_MS, self._poll_clipboard)

    def _poll_clipboard(self):
        """
        Poll clipboard once (runs on main thread).
        This avoids PyObjC GIL conflicts on macOS.
        """
        if not self.is_running:
            return
        
        try:
            # Open clipboard
            if self.clipboard_handler.open_clipboard():
                # Extract file paths
                file_list, source_format = self.clipboard_handler.extract_file_paths_from_clipboard()
                
                # Close clipboard
                self.clipboard_handler.close_clipboard()
                
                if file_list:
                    # Create key for deduplication
                    files_key = "|".join(sorted(file_list))
                    
                    # Only process if content changed
                    if self.clipboard_handler.should_process_content(files_key):
                        logger.info(f"Detected {len(file_list)} files from {source_format}")
                        
                        # Convert to native file format
                        self.clipboard_handler.set_clipboard_files(file_list)
                        
                        # Mark as converted
                        self.clipboard_handler.mark_as_converted(files_key)
                        
        except Exception as e:
            logger.debug(f"Error in clipboard poll: {e}")
            try:
                self.clipboard_handler.close_clipboard()
            except Exception:
                pass
        
        # Schedule next poll
        self._schedule_clipboard_poll()

    # ===== macOS Dock Icon Management =====
    
    def _on_dock_checkbox_changed(self):
        """Handle dock visibility checkbox change (runs on main thread)."""
        if is_macos():
            show = self._dock_var.get()
            self._show_in_dock = show
            self._set_dock_visibility(show)
    
    def _set_dock_visibility(self, show: bool):
        """Set dock icon visibility on macOS."""
        if not is_macos():
            return
        
        try:
            from AppKit import NSApp, NSApplicationActivationPolicyRegular, NSApplicationActivationPolicyAccessory
            
            if show:
                # Show in Dock
                NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
                logger.info("Showing app in Dock")
            else:
                # Hide from Dock (accessory app - only menu bar)
                NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
                logger.info("Hiding app from Dock")
        except Exception as e:
            logger.error(f"Error setting dock visibility: {e}")

    def run(self):
        """Start the application main loop."""
        if is_macos():
            # macOS: run tray icon in detached mode with tkinter
            if self.tray._icon:
                self.tray._icon.run_detached()
            
            # Now run tkinter mainloop
            self.root.mainloop()
        else:
            # Windows: tray already running in thread, just run tkinter
            self.root.mainloop()

