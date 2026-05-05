# Installation Guide

This guide covers installing VSCode Clipboard Helper on Windows and macOS.

## Prerequisites

- **Python 3.12+** - [Download from python.org](https://www.python.org/downloads/)
- **pip** - Usually included with Python

## Windows Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/your-repo/vscode-clipboard-helper.git
cd vscode-clipboard-helper
```

Or download and extract the ZIP file.

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt -r requirements-windows.txt
```

### Step 4: Run

```bash
python main.py
```

## macOS Installation

### Step 1: Clone or Download

```bash
git clone https://github.com/your-repo/vscode-clipboard-helper.git
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

### Step 4: Run

```bash
python main.py
```

## Dependencies Overview

| Package | Platform | Purpose |
|---------|----------|---------|
| pystray | All | System tray icon |
| Pillow | All | Icon image handling |
| pyinstaller | All | Building executables |
| pywin32 | Windows | Windows clipboard API |
| pyobjc-framework-Cocoa | macOS | macOS pasteboard API |

## Troubleshooting

### Windows: "pywin32" installation fails

Try installing the pre-built wheel:
```bash
pip install pywin32 --no-cache-dir
```

### macOS: "pyobjc" installation is slow

PyObjC compiles native extensions, which takes time. Be patient during the first install.

### macOS: App crashes on startup

Ensure you have Xcode Command Line Tools:
```bash
xcode-select --install
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

[← Back to README](../README.md) | [Build Guide →](build-guide.md)
