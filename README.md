# VS Code Clipboard Helper

<div align="center">

Seamlessly copy files from VS Code to Explorer/Finder

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue)](#installation)
[![Python](https://img.shields.io/badge/Python-3.12+-green)](#requirements)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

</div>

---

## Problem

When you copy files in VS Code's Explorer sidebar, it uses a custom clipboard format (`code/file-list`). Most applications expect the native file drop format:

- **Windows**: `CF_HDROP`
- **macOS**: `NSFilenamesPboardType`

This means you can't paste files directly from VS Code to Windows Explorer, macOS Finder, or other applications.

## Solution

This lightweight utility runs in the background and automatically converts VS Code's clipboard format to the native format, enabling seamless file paste operations.

## Features

- **Automatic Conversion** - Silently converts `code/file-list` and other Electron formats to native file drop format
- **Multi-Format Detection** - Supports `code/file-list`, `text/uri-list`, `vscode-editor-drop`, `atom-uri-list`, and plain `file://` URIs
- **Cross-Platform** - Windows and macOS with platform-specific clipboard implementations
- **System Tray** - Minimizes to tray to keep your taskbar/menubar clean
- **Low Resource Usage** - 500ms polling on the main thread with minimal CPU impact (~20-50 MB memory)
- **Localized UI** - Vietnamese interface on Windows, English on macOS
- **Standalone Executable** - Build once, deploy anywhere (no Python required)

## Installation

### Quick Start (From Source)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt -r requirements-windows.txt
python main.py
```

**macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-macos.txt
python main.py
```

> See [Installation Guide](docs/installation.md) for detailed instructions.

### Pre-built Executables

Download the latest release from the [Releases](https://github.com/Deocomate/vscode-clipboard-helper/releases) page.

## Usage

1. Launch the application
2. Click **"Start Monitoring"** (or **"Bat Tool"** on Windows)
3. Copy files in VS Code using `Ctrl+C` (Windows) or `Cmd+C` (macOS)
4. Paste into Explorer, Finder, or any other application

The app runs in the system tray. Close the window to minimize to tray. Right-click the tray icon to show the window or quit.

> See [Usage Guide](docs/usage.md) for more details.

## Building

To build a standalone executable:

```bash
python build.py
```

This creates:
- **Windows**: `dist/VSCodeClipboardHelper.exe` (single file)
- **macOS**: `dist/VSCodeClipboardHelper.app` (app bundle)

> See [Build Guide](docs/build-guide.md) for detailed instructions.

## Project Structure

```
vscode-clipboard-helper/
├── main.py                       # Entry point
├── build.py                      # PyInstaller build script
├── requirements.txt              # Common dependencies (pystray, Pillow, pyinstaller)
├── requirements-windows.txt      # Windows deps (pywin32)
├── requirements-macos.txt        # macOS deps (pyobjc-framework-Cocoa)
├── app/
│   ├── __init__.py               # Package metadata (v2.0.0)
│   ├── core/
│   │   ├── __init__.py           # Factory: get_clipboard_handler()
│   │   ├── clipboard_base.py     # ClipboardHandlerBase ABC
│   │   ├── clipboard_windows.py  # Windows handler (pywin32 + ctypes)
│   │   └── clipboard_macos.py    # macOS handler (PyObjC)
│   ├── gui/
│   │   ├── __init__.py           # Exports VSCodeBridgeApp
│   │   ├── main_window.py        # Main Tkinter window + clipboard polling
│   │   └── tray_icon.py          # System tray (pystray + Pillow)
│   └── utils/
│       ├── __init__.py           # Re-exports utility functions
│       ├── platform.py           # OS detection (Windows/macOS/Linux)
│       ├── resources.py          # PyInstaller-aware resource paths
│       └── path_utils.py         # Path cleaning & file:// URI parsing
└── docs/
    ├── installation.md
    ├── build-guide.md
    └── usage.md
```

## Requirements

- **Python 3.12+**
- **Common**: pystray, Pillow, pyinstaller
- **Windows only**: pywin32
- **macOS only**: pyobjc-framework-Cocoa

## Supported Clipboard Formats

| Format | Source |
|--------|--------|
| `code/file-list` | VS Code (primary) |
| `text/uri-list` | Electron apps |
| `vscode-editor-drop` | VS Code drag-and-drop |
| `atom-uri-list` | Atom editor |
| Plain text `file://` URIs | Various apps |

## How It Works

1. VS Code copies files using `code/file-list` clipboard format
2. The tool polls the clipboard every 500ms on the main thread
3. When a supported format is detected, it extracts file paths
4. File paths are written to the clipboard in native format (CF_HDROP / NSFilenamesPboardType)
5. Any application can now paste the files as if copied from the file manager

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.