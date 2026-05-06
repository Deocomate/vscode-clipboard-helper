# Usage Guide

Learn how to use VS Code Clipboard Helper effectively.

## Getting Started

### Launching the Application

**From source:**
```bash
python main.py
```

**From built executable:**
- Windows: Double-click `VSCodeClipboardHelper.exe`
- macOS: Double-click `VSCodeClipboardHelper.app`

### Main Window

When launched, you'll see a 320×180 window with:
- **Status indicator** — Red (Stopped) or Green (Running) with text label
- **Start/Stop button** — Toggle clipboard monitoring on/off
- **Instructions** — Platform-specific usage reminder

## Using the Tool

### Basic Workflow

1. **Start the app** and click the Start button
2. **Copy files in VS Code:**
   - Select files in the Explorer sidebar
   - Press `Ctrl+C` (Windows) or `Cmd+C` (macOS)
3. **Paste anywhere:**
   - Windows Explorer
   - macOS Finder
   - File upload dialogs
   - Email attachments
   - Any application that accepts file drops

### What Happens Behind the Scenes

1. VS Code places file paths in the clipboard using `code/file-list` format
2. The tool polls the clipboard every 500ms on the main thread
3. When a supported format is detected, file paths are extracted and validated
4. Paths are written to the clipboard in native file drop format
5. Content is marked as converted to prevent re-processing
6. Any application can now paste the files as if copied from the file manager

## System Tray

The app runs in the system tray for convenience.

### Minimizing to Tray

- Click the window's close button (X) — the app continues running in the background
- Look for the icon in your system tray (Windows) or menu bar (macOS)

### Tray Icon Menu

Right-click the tray icon to see:

**Windows:**
| Menu Item | Action |
|-----------|--------|
| Hiện giao diện | Show the main window |
| Thoát | Quit the application |

**macOS:**
| Menu Item | Action |
|-----------|--------|
| Show Window | Show the main window |
| Quit | Quit the application |

### macOS Dock Icon

By default, the app runs as a **menu bar-only** application (no Dock icon). To toggle Dock visibility:

1. Check/uncheck the **"Show in Dock"** checkbox in the main window
2. When checked, the app icon appears in the Dock
3. When unchecked, the app only appears in the menu bar

> **Note:** Running without a Dock icon keeps your Dock clean while the app runs in the background.

## Supported Clipboard Formats

The tool detects multiple clipboard formats in priority order:

| Priority | Format | Source |
|----------|--------|--------|
| 1 | `code/file-list` | VS Code (primary) |
| 2 | `text/uri-list` | Electron apps |
| 3 | `vscode-editor-drop` | VS Code drag-and-drop |
| 4 | `atom-uri-list` | Atom editor |
| 5 | Plain text with `file://` URIs | Various apps |

If the clipboard already contains native file drop format (CF_HDROP on Windows, NSFilenamesPboardType on macOS), the tool skips conversion.

## Path Processing

The tool processes clipboard data through several steps:

1. **Format detection** — Try each supported format in priority order
2. **Path extraction** — Parse text into individual file paths (one per line)
3. **Path cleaning** — Remove quotes, URL-decode (`%20` → space), strip `file://` prefix
4. **Path normalization** — Convert separators to platform-native format (`\` on Windows, `/` on macOS)
5. **Path validation** — Verify each path exists on disk
6. **Native conversion** — Write validated paths in native clipboard format

## Performance

### CPU and Memory

| Metric | Value |
|--------|-------|
| Polling interval | 500ms |
| Typical memory | 20-50 MB |
| CPU when idle | < 1% |
| CPU when converting | Brief spike, < 100ms |

Main consumers: Pillow (icon handling) and Tkinter (UI).

### Tips

- Only start monitoring when needed — the toggle button is always available
- Stop monitoring when not actively copying files to save battery
- The app uses main-thread polling to avoid GIL issues with PyObjC on macOS

## Troubleshooting

### Files not pasting

1. Ensure monitoring is **ON** (status should be green)
2. Copy the files again — the first copy after starting may not be detected
3. Check that the source files exist at the copied paths
4. Try copying twice — sometimes a timing issue means the first copy is detected but not converted

### Tray icon not visible

**Windows:** Check the system tray overflow area (click the arrow icon in the taskbar)

**macOS:** The icon should appear in the menu bar. If not:
- Ensure the app has accessibility permissions
- Try restarting the app

### Application crashes

Run from terminal to see error messages:
```bash
python main.py
```

Common causes:
- Missing dependencies (run `pip install -r requirements.txt -r requirements-<platform>.txt`)
- Permission issues (especially on macOS with accessibility)
- Corrupted or missing icon files

### Double-copy needed

Sometimes you need to copy twice:
1. **First copy:** Tool detects and converts the format
2. **Second copy:** Already in native format, pastes correctly

This is a timing issue that occurs when the tool starts immediately after copying.

## Keyboard Shortcuts

| Action | Windows | macOS |
|--------|---------|-------|
| Copy files in VS Code | `Ctrl+C` | `Cmd+C` |
| Paste files anywhere | `Ctrl+V` | `Cmd+V` |

---

[← Installation Guide](installation.md) | [Build Guide →](build-guide.md)