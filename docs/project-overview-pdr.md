# Project Overview & Product Design Requirements

## Product Summary

**VS Code Clipboard Helper** is a cross-platform utility that bridges the clipboard format gap between VS Code and native file managers. When users copy files in VS Code's Explorer sidebar, the editor places data in `code/file-list` format — which most applications cannot read. This tool automatically converts that format to the native file drop format expected by Windows Explorer (`CF_HDROP`) or macOS Finder (`NSFilenamesPboardType`).

## Problem Statement

| Aspect | Detail |
|--------|--------|
| **Who** | Developers using VS Code who need to copy files to other applications |
| **What** | VS Code uses `code/file-list` clipboard format, not the OS-native file drop format |
| **Impact** | Users cannot paste copied files into Explorer, Finder, upload dialogs, or email attachments |
| **Workaround** | Manually navigating to files in the file manager, or using the terminal |

## Solution

A lightweight background application that:

1. Monitors the system clipboard for VS Code file copy events
2. Extracts file paths from Electron-specific clipboard formats
3. Writes them back in the OS-native file drop format
4. Runs silently in the system tray with minimal resource usage

## Key Features

| Feature | Description |
|---------|-------------|
| Automatic conversion | Detects and converts clipboard data without user action |
| Multi-format detection | Supports `code/file-list`, `text/uri-list`, `vscode-editor-drop`, `atom-uri-list`, plain `file://` URIs |
| Cross-platform | Separate implementations for Windows (pywin32/ctypes) and macOS (PyObjC) |
| System tray | Minimizes to tray; window close hides rather than quits |
| Low resource usage | 500ms main-thread polling, ~20-50 MB memory |
| Localized UI | Vietnamese interface on Windows, English on macOS |
| Standalone build | PyInstaller packaging into .exe (Windows) or .app (macOS) |
| Deduplication | Prevents re-processing the same clipboard content |

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Startup time | < 3 seconds |
| Memory usage | < 50 MB |
| CPU usage when idle | < 1% |
| Clipboard conversion latency | < 1 second from copy |
| Binary size (Windows) | < 20 MB |
| Supported Python | 3.12+ |
| Supported OS | Windows 10+, macOS 12+ |

## Technical Constraints

- **Main-thread polling required** — PyObjC and tkinter both require main-thread access; background threads cause GIL conflicts on macOS
- **No installable package** — Distributed as source or standalone binary, not on PyPI
- **No network access** — Purely local clipboard operations
- **No admin/root required** — Standard user permissions suffice

## User Personas

### Primary: Developer on Windows
- Uses VS Code daily
- Frequently copies files between VS Code and Explorer
- Prefers Vietnamese or English UI
- Wants a set-and-forget tool that starts with Windows

### Secondary: Developer on macOS
- Uses VS Code daily
- Copies files to Finder, upload dialogs
- Prefers menu bar-only apps (no Dock clutter)
- Wants lightweight background operation

## Success Metrics

- Files paste correctly on first attempt after conversion
- No noticeable system performance impact
- App survives sleep/wake cycles and long uptime