# Installation Guide

This guide covers installing VS Code Clipboard Helper on Windows and macOS.

## Prerequisites

- **Python 3.12+** — [Download from python.org](https://www.python.org/downloads/)
- **pip** — Usually included with Python
- **Git** (optional) — For cloning the repository

## Windows Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/Deocomate/vscode-clipboard-helper.git
cd vscode-clipboard-helper
```

Or download and extract the ZIP from the [Releases](https://github.com/Deocomate/vscode-clipboard-helper/releases) page.

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt -r requirements-windows.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| pystray >=0.19.4 | System tray icon |
| Pillow >=10.0.0 | Icon image handling |
| pyinstaller >=6.0.0 | Building executables |
| pywin32 >=306 | Windows clipboard API |

### Step 4: Run

```bash
python main.py
```

## macOS Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/Deocomate/vscode-clipboard-helper.git
cd vscode-clipboard-helper
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt -r requirements-macos.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| pystray >=0.19.4 | System tray icon |
| Pillow >=10.0.0 | Icon image handling |
| pyinstaller >=6.0.0 | Building executables |
| pyobjc-framework-Cocoa >=10.0 | macOS pasteboard API |

> **Note:** PyObjC compiles native extensions during installation. This may take several minutes on first install.

### Step 4: Run

```bash
python main.py
```

## Dependencies Overview

| Package | Platform | Purpose |
|---------|----------|---------|
| pystray >=0.19.4 | All | System tray icon |
| Pillow >=10.0.0 | All | Icon image loading/resizing |
| pyinstaller >=6.0.0 | All | Building standalone executables |
| pywin32 >=306 | Windows | Win32 clipboard API (`win32clipboard`, `win32con`) |
| pyobjc-framework-Cocoa >=10.0 | macOS | macOS pasteboard (`NSPasteboard`, `NSFilenamesPboardType`) |

## Troubleshooting

### Windows: "pywin32" installation fails

Try installing the pre-built wheel:
```bash
pip install pywin32 --no-cache-dir
```

If still failing, try:
```bash
python -m pip install pywin32 --no-cache-dir --force-reinstall
```

### macOS: "pyobjc" installation is slow

PyObjC compiles native extensions, which takes time. This is normal. Expect 2-5 minutes on first install.

### macOS: App crashes on startup

Ensure you have Xcode Command Line Tools:
```bash
xcode-select --install
```

Also verify Python version:
```bash
python3 --version  # Must be 3.12+
```

### Windows: "No module named 'win32clipboard'"

Make sure you installed the Windows-specific requirements:
```bash
pip install -r requirements-windows.txt
```

## Auto-Start on Boot

### Windows

1. Build the executable (see [Build Guide](build-guide.md))
2. Press `Win+R`, type `shell:startup`, and press Enter
3. Copy `VSCodeClipboardHelper.exe` to this folder

### macOS

1. Build the app bundle (see [Build Guide](build-guide.md))
2. Open **System Preferences → Users & Groups → Login Items**
3. Add `VSCodeClipboardHelper.app` to the list

---

[← Back to README](../README.md) | [Usage Guide →](usage.md)