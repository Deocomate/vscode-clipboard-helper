# Project Roadmap

## Current Status: v2.0.0

Fully functional clipboard format converter for Windows and macOS with system tray integration.

### Completed Features

| Feature | Status | Notes |
|---------|--------|-------|
| Windows clipboard conversion | Done | CF_HDROP via DROPFILES struct |
| macOS clipboard conversion | Done | NSFilenamesPboardType via PyObjC |
| Multi-format detection | Done | code/file-list, text/uri-list, vscode-editor-drop, atom-uri-list, file:// URIs |
| System tray icon | Done | pystray with platform-specific menus |
| Tkinter GUI | Done | Status label, start/stop toggle |
| PyInstaller build | Done | .exe (Windows), .app (macOS) |
| Vietnamese UI (Windows) | Done | Localized status text and tray menu |
| macOS dock visibility toggle | Done | NSApplicationActivationPolicy |
| Content deduplication | Done | should_process_content/mark_as_converted |
| Main-thread polling | Done | 500ms interval, avoids GIL issues |

## Planned Enhancements

### Short Term

| Feature | Priority | Description |
|---------|----------|-------------|
| Linux support | Medium | Add clipboard handler for X11/Wayland (xclip, wl-copy) |
| Auto-start on boot | Medium | Register with OS startup (Windows Task Scheduler, macOS Login Items) |
| Config file | Medium | User preferences (polling interval, language, auto-start) |
| Notification on conversion | Low | Brief toast notification when files are converted |

### Medium Term

| Feature | Priority | Description |
|---------|----------|-------------|
| File content preview | Low | Show converted file names in a small overlay |
| Keyboard shortcut | Medium | Global hotkey to toggle monitoring |
| Logging to file | Medium | Persistent logs for debugging |
| Auto-update | Low | Check for new versions and notify |

### Long Term

| Feature | Priority | Description |
|---------|----------|-------------|
| Settings GUI | Low | Full preferences window |
| Multiple language support | Low | i18n framework beyond Vietnamese/English |
| Integration with other editors | Low | Support for JetBrains, Sublime Text clipboard formats |

## Known Issues

| Issue | Platform | Description |
|-------|----------|-------------|
| Double-copy needed sometimes | All | Timing issue when tool starts immediately after copying — first copy may not be detected |
| macOS accessibility permissions | macOS | App may need accessibility permissions for tray icon |
| Windows Defender false positive | Windows | PyInstaller executables commonly flagged; code signing recommended |
| Tray icon overflow | Windows | May be in system tray overflow area; user must drag to main tray |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025 | Refactored project structure, cross-platform support, system tray |
| 1.x | 2024 | Initial Windows-only implementation |