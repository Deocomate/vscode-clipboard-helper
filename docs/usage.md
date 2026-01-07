# Usage Guide

Learn how to use VSCode Clipboard Helper effectively.

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

When launched, you'll see the main window with:
- **Status indicator** - Shows whether monitoring is active
- **Start/Stop button** - Toggle clipboard monitoring
- **Instructions** - Quick usage reminder

## Using the Tool

### Basic Workflow

1. **Start the app** and click the Start button
2. **Copy files in VS Code:**
   - Select files in the Explorer sidebar
   - Press `Ctrl+C` (Windows) or `Cmd+C` (macOS)
3. **Paste anywhere:**
   - Windows Explorer
   - macOS Finder
   - File manager
   - Upload dialogs
   - Email attachments

### What Happens Behind the Scenes

1. VS Code places file paths in the clipboard using `code/file-list` format
2. The tool detects this format
3. It converts the data to native file drop format
4. Now any app can receive the files as if copied from the file manager

## System Tray

The app runs in the system tray for convenience.

### Minimizing to Tray

- Click the window's close button (X)
- The app continues running in the background
- Look for the icon in your system tray

### Tray Icon Menu

Right-click the tray icon to see:
- **Show Window** - Bring back the main window
- **Show in Dock** (macOS only) - Toggle dock icon visibility
- **Quit** - Exit the application completely

### macOS Dock Icon

By default, the app runs as a **menu bar-only** application (no dock icon). To show/hide the dock icon:

1. Click the menu bar icon
2. Select **"Show in Dock"** to toggle
3. When checked, the app icon appears in the Dock

> **Note:** Running without a dock icon keeps your Dock clean while the app runs in the background.

### Quick Restore

- **Windows:** Click or right-click the tray icon
- **macOS:** Click the menubar icon


## Supported Formats

The tool detects multiple clipboard formats:

| Format | Source |
|--------|--------|
| `code/file-list` | VS Code (primary) |
| `text/uri-list` | Electron apps |
| `vscode-editor-drop` | VS Code drag |
| `atom-uri-list` | Atom editor |
| Plain text `file://` URIs | Various apps |

## Performance Tips

### CPU Usage

The tool polls the clipboard every 500ms. This uses minimal CPU but is noticeable on battery. Consider:
- Only starting the tool when needed
- Stopping when not actively copying files

### Memory

Typical memory usage is 20-50 MB. The Pillow library for icons and Tkinter for the UI are the main consumers.

## Troubleshooting

### Files not pasting

1. Ensure monitoring is **ON** (status should be green)
2. Copy the files again - the first copy after starting may not be converted
3. Check if the files actually exist at the copied paths

### Tray icon not visible

**Windows:** Check the system tray overflow area (arrow icon)

**macOS:** The icon should appear in the menubar. If not:
- Ensure the app has accessibility permissions
- Try restarting the app

### Application crashes

Check the console output for error messages:
```bash
python main.py  # Run from terminal to see errors
```

Common causes:
- Missing dependencies
- Permission issues (especially on macOS)
- Corrupted icon files

### Multiple copies needed

Sometimes you need to copy twice:
1. First copy: Tool detects and converts
2. Second copy: Already in native format, pastes correctly

This is a timing issue when the tool starts immediately after copying.

## Keyboard Shortcuts Reference

| Action | Windows | macOS |
|--------|---------|-------|
| Copy files | `Ctrl+C` | `Cmd+C` |
| Paste files | `Ctrl+V` | `Cmd+V` |

---

[← Build Guide](build-guide.md) | [Back to README →](../README.md)
