# System Architecture

## High-Level Architecture

```mermaid
graph TD
    VSCode[VS Code - Ctrl/Cmd+C] -->|code/file-list format| Clipboard[System Clipboard]
    Clipboard -->|500ms poll| App[VSCodeBridgeApp]
    App -->|extract_file_paths| Handler[ClipboardHandler]
    Handler -->|parse paths| PathUtils[path_utils]
    Handler -->|write native format| Clipboard
    Clipboard -->|CF_HDROP / NSFilenamesPboardType| Explorer[Explorer / Finder / Apps]
    
    App -->|show/hide| Tray[TrayIcon - pystray]
    App -->|manage| Window[Tkinter Window]
```

## Module Dependency Graph

```mermaid
graph LR
    main[main.py] --> gui[app.gui]
    gui --> core[app.core]
    gui --> utils[app.utils]
    core --> utils
    
    gui -->|VSCodeBridgeApp| MainWindow[main_window.py]
    gui -->|TrayIcon| TrayIcon[tray_icon.py]
    core -->|ClipboardHandlerBase| Base[clipboard_base.py]
    core -->|WindowsClipboardHandler| Win[clipboard_windows.py]
    core -->|MacOSClipboardHandler| Mac[clipboard_macos.py]
    core -->|factory| Init[__init__.py]
    
    utils -->|is_windows is_macos| Platform[platform.py]
    utils -->|clean_path text_to_files| PathUtils[path_utils.py]
    utils -->|get_resource_path| Resources[resources.py]
```

## Class Hierarchy

```mermaid
classDiagram
    class ClipboardHandlerBase {
        <<abstract>>
        +last_clipboard_content: str
        +open_clipboard() bool
        +close_clipboard() None
        +has_file_drop() bool
        +get_custom_format_data(format_name) Optional~str~
        +get_text_data() Optional~str~
        +set_clipboard_files(file_list) bool
        +extract_file_paths_from_clipboard() Tuple
        +should_process_content(content_key) bool
        +mark_as_converted(content_key) None
        -_looks_like_path(text) bool
    }

    class WindowsClipboardHandler {
        -_clipboard_open: bool
        +open_clipboard() bool
        +close_clipboard() None
        +has_file_drop() bool
        +get_custom_format_data(format_name) Optional~str~
        +get_text_data() Optional~str~
        +set_clipboard_files(file_list) bool
        -_get_registered_format_id(format_name) int
    }

    class MacOSClipboardHandler {
        -_pasteboard: NSPasteboard
        +FILE_URL_TYPE: str
        +FILE_NAMES_TYPE: NSFilenamesPboardType
        +open_clipboard() bool
        +close_clipboard() None
        +has_file_drop() bool
        +get_custom_format_data(format_name) Optional~str~
        +get_text_data() Optional~str~
        +set_clipboard_files(file_list) bool
        +get_file_urls_from_pasteboard() Optional~List~str~~
    }

    ClipboardHandlerBase <|-- WindowsClipboardHandler
    ClipboardHandlerBase <|-- MacOSClipboardHandler
```

## Clipboard Processing Flow

```mermaid
sequenceDiagram
    participant App as VSCodeBridgeApp
    participant Handler as ClipboardHandler
    participant Utils as path_utils
    participant Clipboard as System Clipboard

    loop Every 500ms
        App->>Handler: open_clipboard()
        App->>Handler: extract_file_paths_from_clipboard()
        Handler->>Handler: has_file_drop? → skip if native format exists
        alt code/file-list format
            Handler->>Clipboard: get_custom_format_data("code/file-list")
            Handler->>Utils: text_to_files(data)
            Utils-->>Handler: [file_paths]
        else text/uri-list format
            Handler->>Clipboard: get_custom_format_data("text/uri-list")
            Handler->>Utils: text_to_files(data)
            Utils-->>Handler: [file_paths]
        else plain text fallback
            Handler->>Clipboard: get_text_data()
            Handler->>Utils: text_to_files(data)
            Utils-->>Handler: [file_paths]
        end
        Handler-->>App: (file_list, source_format) or (None, None)
        App->>Handler: close_clipboard()
        
        alt file_list found
            App->>App: should_process_content(files_key)?
            App->>Handler: set_clipboard_files(file_list)
            App->>App: mark_as_converted(files_key)
        end
    end
```

## Platform Implementation Details

### Windows (`clipboard_windows.py`)

- Uses `win32clipboard` module for clipboard operations
- Constructs `DROPFILES` ctypes Structure for `CF_HDROP` format
- `RegisterClipboardFormatW` for custom format detection
- Unicode path support via `fWide = True` in `DROPFILES`
- Multiple encoding fallback: UTF-8 → UTF-16 → Latin-1

### macOS (`clipboard_macos.py`)

- Uses `NSPasteboard` via PyObjC for pasteboard operations
- `NSFilenamesPboardType` and `public.file-url` for native format
- `NSURL.fileURLWithPath_()` for creating file URLs
- `writeObjects_()` for writing file array to pasteboard
- No explicit open/close needed (pasteboard is always accessible)

## Threading Model

```mermaid
graph TD
    MainThread[Main Thread - tkinter mainloop] -->|500ms poll| Poll[_poll_clipboard]
    MainThread -->|after callbacks| Flags[_pending_show_window / _pending_quit]
    
    subgraph Windows
        TrayThread[Background Thread] -->|pystray Icon.run| TrayWin[TrayIcon]
        TrayWin -->|set flags| Flags
    end
    
    subgraph macOS
        MainThread -->|run_detached| TrayMac[TrayIcon]
        TrayMac -->|set flags| Flags
    end
```

- **Windows**: Tray icon runs in a background daemon thread; communicates with tkinter via flags
- **macOS**: Tray icon uses `run_detached()`; flag polling via `root.after(100, _check_tray_flags)`
- No direct tkinter calls from pystray thread (avoids GIL issues)