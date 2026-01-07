# VS Code Clipboard Helper

<div align="center">

🔗 **Seamlessly copy files from VS Code to Explorer/Finder**

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-blue)](#installation)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](#requirements)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

</div>

---

## 🎯 Problem

When you copy files in VS Code's Explorer sidebar, it uses a custom clipboard format (`code/file-list`). Most applications expect the native file drop format:
- **Windows**: `CF_HDROP` 
- **macOS**: `NSFilenamesPboardType`

This means you can't paste files directly from VS Code to Windows Explorer, macOS Finder, or other applications.

## ✨ Solution

This lightweight utility runs in the background and automatically converts VS Code's clipboard format to the native format, enabling seamless file paste operations.

## 🚀 Features

- **Automatic Conversion** - Works silently in the background
- **System Tray** - Minimizes to tray to keep your taskbar/menubar clean  
- **Cross-Platform** - Supports Windows and macOS
- **Low Resource Usage** - Optimized polling with minimal CPU impact
- **Standalone Executable** - Build once, deploy anywhere (no Python required)

## 📦 Installation

### Quick Start (From Source)

**Windows:**
```bash
pip install -r requirements.txt -r requirements-windows.txt
python main.py
```

**macOS:**
```bash
pip install -r requirements.txt -r requirements-macos.txt
python main.py
```

> 📖 See [Installation Guide](docs/installation.md) for detailed instructions.

### Pre-built Executables

Download the latest release from the [Releases](https://github.com/your-repo/vscode-clipboard-helper/releases) page.

## 🛠️ Usage

1. Launch the application
2. Click **"Start Monitoring"** (or **"Bật Tool"** on Windows)
3. Copy files in VS Code using `Ctrl+C` (Windows) or `Cmd+C` (macOS)
4. Paste into Explorer, Finder, or any other application

The app runs in the system tray. Right-click the tray icon to show the window or quit.

> 📖 See [Usage Guide](docs/usage.md) for more details.

## 🔧 Building

To build a standalone executable:

```bash
python build.py
```

This creates:
- **Windows**: `dist/VSCodeClipboardHelper.exe`
- **macOS**: `dist/VSCodeClipboardHelper.app`

> 📖 See [Build Guide](docs/build-guide.md) for detailed instructions.

## 📁 Project Structure

```
vscode-clipboard-helper/
├── main.py                    # Entry point
├── build.py                   # Build script
├── requirements.txt           # Common dependencies
├── requirements-windows.txt   # Windows-specific deps
├── requirements-macos.txt     # macOS-specific deps
├── app/
│   ├── core/                  # Clipboard handling
│   │   ├── clipboard_base.py
│   │   ├── clipboard_windows.py
│   │   └── clipboard_macos.py
│   ├── gui/                   # UI components
│   │   ├── main_window.py
│   │   └── tray_icon.py
│   └── utils/                 # Utilities
│       ├── platform.py
│       ├── resources.py
│       └── path_utils.py
└── docs/                      # Documentation
    ├── installation.md
    ├── build-guide.md
    └── usage.md
```

## 📋 Requirements

- Python 3.10 or higher
- Dependencies vary by platform (see requirements files)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
