# Build Guide

This guide explains how to build standalone executables for Windows and macOS.

## Prerequisites

- Python 3.10+ with pip
- All dependencies installed (see [Installation Guide](installation.md))
- Icon files in the project root:
  - `icon.png` - Required for both platforms
  - `icon.ico` - Recommended for Windows
  - `icon.icns` - Recommended for macOS

## Quick Build

Simply run:

```bash
python build.py
```

The script automatically detects your platform and applies the appropriate settings.

## Build Output

| Platform | Output Location | Type |
|----------|----------------|------|
| Windows | `dist/VSCodeClipboardHelper.exe` | Single executable |
| macOS | `dist/VSCodeClipboardHelper.app` | Application bundle |

## Windows Build Details

### What Gets Built

- Single `.exe` file containing all dependencies
- No console window (runs silently)
- Icon embedded in the executable

### Manual Build Command

```bash
pyinstaller main.py ^
    --name=VSCodeClipboardHelper ^
    --onefile ^
    --noconsole ^
    --icon=icon.ico ^
    --add-data="icon.png;." ^
    --add-data="icon.ico;." ^
    --clean
```

### Code Signing (Optional)

For distribution, consider signing your executable:

```bash
signtool sign /a /t http://timestamp.digicert.com dist\VSCodeClipboardHelper.exe
```

## macOS Build Details

### What Gets Built

- `.app` bundle with proper macOS structure
- Windowed application (no terminal)
- Icon displayed in Finder and Dock

### Manual Build Command

```bash
pyinstaller main.py \
    --name=VSCodeClipboardHelper \
    --windowed \
    --onedir \
    --icon=icon.icns \
    --add-data="icon.png:." \
    --clean
```

### Creating an Icon File (.icns)

If you only have a PNG, convert it:

```bash
# Create iconset directory
mkdir MyIcon.iconset

# Create all required sizes
sips -z 16 16     icon.png --out MyIcon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out MyIcon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out MyIcon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out MyIcon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out MyIcon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out MyIcon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out MyIcon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out MyIcon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out MyIcon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out MyIcon.iconset/icon_512x512@2x.png

# Generate .icns file
iconutil -c icns MyIcon.iconset -o icon.icns

# Cleanup
rm -rf MyIcon.iconset
```

### Code Signing and Notarization

For distribution outside the App Store:

```bash
# Sign the app
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name" \
    dist/VSCodeClipboardHelper.app

# Create ZIP for notarization
ditto -c -k --keepParent dist/VSCodeClipboardHelper.app VSCodeClipboardHelper.zip

# Submit for notarization
xcrun notarytool submit VSCodeClipboardHelper.zip \
    --apple-id "your@email.com" \
    --team-id YOUR_TEAM_ID \
    --password "app-specific-password" \
    --wait

# Staple the ticket
xcrun stapler staple dist/VSCodeClipboardHelper.app
```

## Troubleshooting

### Build fails with "ModuleNotFoundError"

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt -r requirements-$(uname -s | tr A-Z a-z).txt
```

### Windows Defender blocks the executable

This is common with PyInstaller executables. Options:
1. Sign the executable with a code signing certificate
2. Add an exception in Windows Defender
3. Build on the target system

### macOS: "App is damaged and can't be opened"

This happens with unsigned apps. Clear the quarantine attribute:
```bash
xattr -cr dist/VSCodeClipboardHelper.app
```

### Build is very large

Use `--onefile` carefully. Consider `--onedir` for smaller initial download with faster startup.

---

[← Installation Guide](installation.md) | [Usage Guide →](usage.md)
