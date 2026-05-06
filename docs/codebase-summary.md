# Codebase Summary

## Overview

VS Code Clipboard Helper (v2.0.0) is a Python desktop application that converts VS Code's clipboard file format to native OS file drop format. It uses a Tkinter GUI with system tray support and platform-specific clipboard handlers.

**Total LOC:** ~1,400 (Python)

## Module Map

| Module | File | LOC | Purpose |
|--------|------|-----|---------|
| Entry | `main.py` | 36 | Application entry point |
| Build | `build.py` | 120 | PyInstaller build script |
| App | `app/__init__.py` | 10 | Package metadata |
| Core | `app/core/__init__.py` | 22 | Factory: `get_clipboard_handler()` |
| Core | `app/core/clipboard_base.py` | 157 | `ClipboardHandlerBase` ABC |
| Core | `app/core/clipboard_windows.py` | 144 | `WindowsClipboardHandler` |
| Core | `app/core/clipboard_macos.py` | 146 | `MacOSClipboardHandler` |
| GUI | `app/gui/__init__.py` | 7 | Exports `VSCodeBridgeApp` |
| GUI | `app/gui/main_window.py` | 337 | Main window, polling, tray integration |
| GUI | `app/gui/tray_icon.py` | 185 | `TrayIcon` wrapper for pystray |
| Utils | `app/utils/__init__.py` | 16 | Re-exports |
| Utils | `app/utils/platform.py` | 49 | OS detection helpers |
| Utils | `app/utils/resources.py` | 63 | PyInstaller-aware resource paths |
| Utils | `app/utils/path_utils.py` | 108 | Path cleaning & file URI parsing |

## Dependencies

### Common (`requirements.txt`)
| Package | Version | Purpose |
|---------|---------|---------|
| pystray | >=0.19.4 | System tray icon |
| Pillow | >=10.0.0 | Icon image loading/resizing |
| pyinstaller | >=6.0.0 | Build standalone executables |

### Windows (`requirements-windows.txt`)
| Package | Version | Purpose |
|---------|---------|---------|
| pywin32 | >=306 | Win32 clipboard API (`win32clipboard`, `win32con`) |

### macOS (`requirements-macos.txt`)
| Package | Version | Purpose |
|---------|---------|---------|
| pyobjc-framework-Cocoa | >=10.0 | macOS pasteboard API (`NSPasteboard`, `NSFilenamesPboardType`) |

## Key Classes

### ClipboardHandlerBase (`clipboard_base.py`)

Abstract base class defining the clipboard interface:

- `open_clipboard() -> bool` — Open clipboard for reading/writing
- `close_clipboard() -> None` — Close clipboard
- `has_file_drop() -> bool` — Check for native file drop format
- `get_custom_format_data(format_name) -> Optional[str]` — Read custom clipboard format
- `get_text_data() -> Optional[str]` — Read plain text from clipboard
- `set_clipboard_files(file_list) -> bool` — Write native file drop format
- `extract_file_paths_from_clipboard() -> Tuple[Optional[List[str]], Optional[str]]` — Main extraction method
- `should_process_content(content_key) -> bool` — Deduplication check
- `mark_as_converted(content_key) -> None` — Mark content as processed

### WindowsClipboardHandler (`clipboard_windows.py`)

Uses `win32clipboard` + `ctypes` for clipboard operations. Constructs `DROPFILES` struct for `CF_HDROP` format.

### MacOSClipboardHandler (`clipboard_macos.py`)

Uses `NSPasteboard` + `NSURL` via PyObjC. Writes file URLs with `writeObjects_()`.

### VSCodeBridgeApp (`main_window.py`)

Tkinter application with 500ms main-thread polling. Manages:
- Status label and toggle button
- System tray icon integration
- Cross-thread communication (flag-based for GIL safety)
- macOS dock visibility toggle
- Clipboard monitoring lifecycle

### TrayIcon (`tray_icon.py`)

Pystray wrapper with platform-specific menus:
- **Windows**: Vietnamese labels ("Hien giao dien", "Thoat")
- **macOS**: English labels ("Show Window", "Quit")

## Data Flow

```
VS Code (Ctrl+C/Cmd+C)
  → Clipboard contains code/file-list format
    → VSCodeBridgeApp polls clipboard (500ms, main thread)
      → ClipboardHandlerBase.extract_file_paths_from_clipboard()
        → Try formats: code/file-list → text/uri-list → vscode-editor-drop → atom-uri-list → plain text
          → path_utils.text_to_files() parses and validates paths
            → ClipboardHandlerBase.set_clipboard_files()
              → Windows: DROPFILES struct via ctypes
              → macOS: NSURL array via PyObjC
```

## Build Output

| Platform | Output | Type |
|----------|--------|------|
| Windows | `dist/VSCodeClipboardHelper.exe` | Single executable (--onefile) |
| macOS | `dist/VSCodeClipboardHelper.app` | App bundle (--onedir) |