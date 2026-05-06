# Build Guide

This guide explains how to build standalone executables for Windows and macOS using PyInstaller.

## Prerequisites

- **Python 3.12+** with pip
- All dependencies installed (see [Installation Guide](installation.md))
- Icon files in the project root:
  - `icon.png` — Required for both platforms
  - `icon.ico` — Recommended for Windows
  - `icon.icns` — Recommended for macOS

## Quick Build

Simply run:

```bash
python build.py
```

The script automatically detects your platform and applies the appropriate PyInstaller settings.

## Build Output

| Platform | Output Location | Type |
|----------|----------------|------|
| Windows | `dist/VSCodeClipboardHelper.exe` | Single executable (`--onefile`) |
| macOS | `dist/VSCodeClipboardHelper.app` | Application bundle (`--onedir`) |

## Windows Build Details

### What Gets Built

- Single `.exe` file containing all dependencies
- No console window (runs silently via `--noconsole`)
- Icon embedded in the executable
- Both `icon.png` and `icon.ico` bundled as data files

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
- Windowed application (no terminal via `--windowed`)
- Icon displayed in Finder and Dock
- Uses `--onedir` for better macOS compatibility

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

> **Note:** The build script automatically falls back to `icon.png` if `icon.icns` is not found.

### Creating an Icon File (.icns)

If you only have a PNG, convert it using `sips` and `iconutil`:

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

## Resource Bundling

PyInstaller bundles resources using `sys._MEIPASS`. The `get_resource_path()` function in `app/utils/resources.py` handles this automatically:

| Running Mode | Resource Path |
|-------------|---------------|
| Source (`python main.py`) | Project root directory |
| PyInstaller bundle | `sys._MEIPASS` temp directory |

Bundled resources:
- `icon.png` — Tray icon and window icon (all platforms)
- `icon.ico` — Windows executable icon

## Troubleshooting

### Build fails with "ModuleNotFoundError"

Ensure all dependencies are installed:
```bash
# Windows
pip install -r requirements.txt -r requirements-windows.txt

# macOS
pip install -r requirements.txt -r requirements-macos.txt
```

### Windows Defender blocks the executable

This is common with PyInstaller executables. Options:
1. Sign the executable with a code signing certificate
2. Add an exception in Windows Defender
3. Build on the target machine

### macOS: "App is damaged and can't be opened"

This happens with unsigned apps. Clear the quarantine attribute:
```bash
xattr -cr dist/VSCodeClipboardHelper.app
```

### Build is very large

Use `--onefile` for single-file distribution (Windows default) or `--onedir` for smaller initial download with faster startup (macOS default). The build script already chooses the best option per platform.

### Missing icon after build

Ensure `icon.png` exists in the project root. For platform-specific icons:
- Windows: `icon.ico` in project root
- macOS: `icon.icns` in project root (falls back to `icon.png`)

---

[← Usage Guide](usage.md) | [Back to README →](../README.md)