# Design Guidelines

## UI Design Principles

### Core Philosophy

The VS Code Clipboard Helper follows a **utility-first** design approach:
- Minimal visible UI — the app should disappear into the system tray
- Status-at-a-glance — one color tells you everything (red = off, green = on)
- Zero configuration needed for basic operation

### Window Layout

```
┌──────────────────────────────────┐
│    VS Code Clipboard Helper      │
│                                  │
│    ● Trạng thái: Đang chạy ngầm  │  ← Status label (red/green)
│                                  │
│    ┌──────────────────────────┐  │
│    │      Bật Tool            │  │  ← Toggle button
│    └──────────────────────────┘  │
│                                  │
│    Chọn file trong VS Code →     │  ← Instructions
│    Ctrl+C → Paste vào nơi cần    │
│                                  │
│    ☐ Show in Dock  (macOS only)  │  ← Dock visibility checkbox
│                                  │
└──────────────────────────────────┘
```

- **Window size**: 320×180 pixels, non-resizable
- **Layout**: Single column, centered content, 20px padding

### Color Scheme

| Element | Color | Usage |
|---------|-------|-------|
| Status: Stopped | Red | Monitoring is inactive |
| Status: Running | Green | Monitoring is active |
| Tray icon (default) | Blue | Default fallback icon |
| Tray icon (loaded) | Custom | From `icon.png` / `icon.ico` |

### Platform Differences

| Aspect | Windows | macOS |
|--------|---------|--------|
| Status text | Vietnamese: "Trạng thái: Đang chạy ngầm" / "Trạng thái: Đang dừng" | English: "Status: Running" / "Status: Stopped" |
| Button text | Vietnamese: "Bật Tool" / "Dừng Tool" | English: "Start Monitoring" / "Stop Monitoring" |
| Instructions | Vietnamese: "Chọn file trong VS Code → Ctrl+C → Paste vào nơi cần" | English: "Copy files in VS Code (Cmd+C) → Paste into Finder or other apps" |
| Tray menu | "Hiện giao diện" / "Thoát" | "Show Window" / "Quit" |
| Dock visibility | N/A | Checkbox to toggle Dock icon |
| Tray icon size | 32×32 | 22×22 |

## System Tray Design

### Icon States

- **Default**: Blue square with white center (generated via PIL)
- **Custom**: Loaded from `icon.png` (and `icon.ico` on Windows)
- Resized automatically: 22×22 on macOS, 32×32 on Windows

### Tray Menu Items

**Windows:**
1. Hiện giao diện (Show window)
2. —separator—
3. Thoát (Quit)

**macOS:**
1. Show Window
2. —separator—
3. Quit

## Interaction Patterns

### Startup Flow

```
App launches → Window shown → User clicks "Start Monitoring"
→ Tray icon appears → Clipboard polling begins
```

### Window Close Behavior

```
User clicks X → Window hides (withdraw) → App continues in tray
→ Tray menu "Show Window" → Window restores (deiconify)
```

### Clipboard Conversion Flow

```
User copies files in VS Code
→ 500ms poll detects clipboard change
→ Extract file paths from Electron format
→ Validate paths exist on disk
→ Write to clipboard in native format
→ Mark content as converted (dedup)
→ User pastes in Explorer/Finder → Files appear
```

### Quit Flow

```
Tray menu "Quit" → stop monitoring → stop tray → destroy window → sys.exit(0)
```

## Error Handling UX

| Scenario | User Feedback |
|----------|---------------|
| Clipboard open fails | Silent (logged at debug level) |
| Path validation fails | Silent (skipped, logged at debug level) |
| Icon file missing | Fallback to generated blue icon |
| Permission denied (macOS) | Check console for error messages |
| Build missing deps | Warning printed to console |

## Accessibility

- High contrast status colors (red/green) with text labels — not color-only indicators
- Keyboard-accessible toggle button (standard Tkinter widget)
- System tray follows OS conventions for accessibility
- Minimum touch/click target size: 30×30 pixels for buttons