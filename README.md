# VSCode Clipboard Helper

A lightweight Windows system tray utility that fixes the file copy-paste issue between VS Code and other applications (Explorer, Outlook, Browsers, etc.).

## Problem

When you copy files in VS Code's Explorer, it places a text-based format (`code/file-list`) in the clipboard. Most Windows applications expect a standard "File Drop" format (`CF_HDROP`). This mismatch prevents you from pasting files directly from VS Code to other apps.

## Solution

This tool runs in the background, monitors the clipboard, and automatically converts VS Code's file format into standard Windows File Drop format.

## Features

-   **Automatic Conversion**: Works silently in the background.
-   **System Tray Icon**: Minimizes to tray to keep your taskbar clean.
-   **Low Resource Usage**: Optimized polling and reduced logging.
-   **Standalone EXE**: Easy to deploy, no Python required (if built).

## Installation & Usage

### Option 1: Run from Source

1.  **Install Python 3.10+**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the App**:
    ```bash
    python main.py
    ```
4.  Control the app via the system tray icon (Right-click -> Hiện giao diện / Thoát).

### Option 2: Build Executable

1.  Run the build script:
    ```bash
    python build.py
    ```
2.  Find the `VSCodeClipboardHelper.exe` in the `dist` folder.
3.  You can place this EXE in your Startup folder to run automatically with Windows.

## Development

-   `main.py`: Core application logic using `tkinter` for UI and `pystray` for system tray.
-   `build.py`: PyInstaller build configuration.

## License

MIT
