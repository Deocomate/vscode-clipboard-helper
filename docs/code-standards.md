# Code Standards

## General Conventions

| Aspect | Convention |
|--------|-----------|
| Language | Python 3.12+ |
| Line length | 120 characters (soft limit) |
| Naming: modules | `snake_case.py` |
| Naming: classes | `PascalCase` |
| Naming: functions/methods | `snake_case` |
| Naming: constants | `UPPER_SNAKE_CASE` |
| Naming: private members | `_leading_underscore` |
| String quotes | Double quotes for docstrings, single quotes for string literals preferred |
| Type hints | Required for all public methods (`from typing import ...`) |
| Docstrings | Google-style for all public classes and methods |

## Project Structure

```
app/
├── core/           # Clipboard abstraction layer
│   ├── clipboard_base.py      # ABC defining the interface
│   ├── clipboard_windows.py   # Windows implementation
│   └── clipboard_macos.py     # macOS implementation
├── gui/            # UI components
│   ├── main_window.py         # Tkinter app + clipboard polling
│   └── tray_icon.py           # System tray wrapper
└── utils/          # Shared utilities
    ├── platform.py             # OS detection
    ├── resources.py            # Resource path resolution
    └── path_utils.py           # Path cleaning & parsing
```

## Import Ordering

1. Standard library (`os`, `sys`, `logging`, `ctypes`, `tkinter`)
2. Third-party (`pystray`, `PIL`, `win32clipboard`, `AppKit`)
3. Local application (`from app.core import ...`, `from app.utils import ...`)

Separate groups with blank lines.

## Logging

- Use `logging.getLogger(__name__)` in every module
- Levels: `logger.debug()` for detailed tracing, `logger.info()` for key events, `logger.error()` for failures
- Module-level `DEBUG` flag controls verbose output in clipboard handlers

## Platform-Specific Code

- Platform detection via `app.utils.platform.is_windows()` / `is_macos()`
- Platform-specific imports are **inside methods** or in platform-specific modules only (e.g., `win32clipboard` only in `clipboard_windows.py`)
- Conditional UI text: Vietnamese on Windows, English on macOS

## Error Handling

- Clipboard operations wrapped in `try/except` — clipboard access is inherently unreliable
- `open_clipboard()` returns `bool` to signal success/failure
- Always `close_clipboard()` in a `finally` block or after operations
- Windows: close clipboard explicitly even on error in `set_clipboard_files()`

## GUI Conventions

- Tkinter for main window, pystray for system tray
- Main-thread polling at 500ms interval (`POLL_INTERVAL_MS`)
- Cross-thread communication via flags (`_pending_show_window`, `_pending_quit`) — not direct tkinter calls from pystray thread
- Window close minimizes to tray (does not quit)

## Build Conventions

- PyInstaller for standalone executables
- Windows: `--onefile --noconsole` with icon embedding
- macOS: `--windowed --onedir` with app bundle structure
- Resource files bundled via `--add-data`
- `sys._MEIPASS` for finding resources when running from PyInstaller bundle