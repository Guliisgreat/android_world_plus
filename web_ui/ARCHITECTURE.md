# Web Access Architecture Design

This document describes the architecture and design of the web access scripts for Android emulator control.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Process Management](#process-management)
6. [Network Architecture](#network-architecture)
7. [Technology Stack](#technology-stack)

---

## System Overview

The web access system provides remote control of Android emulators through a web browser. Two different approaches are implemented:

1. **scrcpy-based Approach** (Recommended): Uses scrcpy for real-time video streaming with high frame rates and low latency
2. **ADB-based Approach**: Uses ADB commands for screenshot capture and input events

Both approaches enable remote access from a web browser (e.g., on a Mac laptop) to an Android emulator running on a Linux server.

### Multiple Team Members Support

The system supports multiple team members working simultaneously, each with their own emulator:

- **Device Selection**: Each team member can specify which emulator to connect to using the `--device-serial` parameter
- **Port Isolation**: Multiple instances can run simultaneously using different ports (`--web-port`, `--vnc-port`)
- **Automatic Detection**: The script automatically detects and lists all connected devices
- **Device Validation**: Validates that the specified device exists before starting

**Usage Example for Teams:**

```bash
# Team member 1 - List available devices
python3 start_web_access_scrcpy.py --list-devices

# Team member 1 - Connect to their emulator
python3 start_web_access_scrcpy.py --device-serial emulator-5554 --web-port 6080

# Team member 2 - Connect to their emulator with different ports
python3 start_web_access_scrcpy.py --device-serial emulator-5556 --web-port 6081 --vnc-port 5902

# Team member 3 - Connect to their emulator
python3 start_web_access_scrcpy.py --device-serial emulator-5558 --web-port 6082 --vnc-port 5903
```

Each team member runs their own instance, targeting their specific emulator and using unique ports to avoid conflicts.

### Key Design Principles

- **Separation of Concerns**: Each script handles one specific method
- **Process Isolation**: Child processes run independently
- **Error Handling**: Graceful degradation and clear error messages
- **Network Binding**: Binds to `0.0.0.0` for remote access support
- **Resource Cleanup**: Proper cleanup of all processes on exit

---

## Architecture Diagrams

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Linux Server                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Android Emulator (via ADB)                      │  │
│  │         - Running Android OS                             │  │
│  │         - Connected via ADB                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                      │
│                            │ ADB Protocol                         │
│                            ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Web Access Script                                 │  │
│  │         (start_web_access_*.py)                          │  │
│  │                                                            │  │
│  │  - Orchestrates all components                            │  │
│  │  - Manages child processes                                │  │
│  │  - Handles signals and cleanup                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                      │
│                            │                                      │
│         ┌──────────────────┴──────────────────┐                 │
│         │                                      │                 │
│         ▼                                      ▼                 │
│  ┌──────────────┐                      ┌──────────────┐         │
│  │ Method A:    │                      │ Method B:    │         │
│  │ ADB Server   │                      │ scrcpy Stack │         │
│  └──────────────┘                      └──────────────┘         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            │
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser (Mac)                         │
│  - Chrome, Firefox, Safari                                      │
│  - JavaScript VNC Client (noVNC)                                │
│  - HTML/JavaScript UI                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Method A: scrcpy-Based Architecture (Recommended)

The scrcpy-based approach provides real-time video streaming with high frame rates (30-60 FPS) and low latency (~30-50ms). It's the recommended method for interactive use and provides the smoothest user experience.

### Multi-Device Support

When multiple team members work together, each can run their own instance:

```
┌─────────────────────────────────────────────────────────────────┐
│  Linux Server                                                    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Team Member 1 Instance                                   │  │
│  │  python3 start_web_access_scrcpy.py                      │  │
│  │  --device-serial emulator-5554                           │  │
│  │  --web-port 6080 --vnc-port 5901                        │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │  Xvfb    │  │  scrcpy  │  │  x11vnc   │              │  │
│  │  │  :10     │  │  (5554)  │  │  :5901    │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  │                     │                                      │  │
│  │                     │ ADB                                  │  │
│  │                     ▼                                      │  │
│  │              ┌──────────────┐                              │  │
│  │              │ Emulator 5554│                              │  │
│  │              └──────────────┘                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Team Member 2 Instance                                   │  │
│  │  python3 start_web_access_scrcpy.py                      │  │
│  │  --device-serial emulator-5556                           │  │
│  │  --web-port 6081 --vnc-port 5902                        │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │  │
│  │  │  Xvfb    │  │  scrcpy  │  │  x11vnc   │              │  │
│  │  │  :11     │  │  (5556)  │  │  :5902    │              │  │
│  │  └──────────┘  └──────────┘  └──────────┘              │  │
│  │                     │                                      │  │
│  │                     │ ADB                                  │  │
│  │                     ▼                                      │  │
│  │              ┌──────────────┐                              │  │
│  │              │ Emulator 5556│                              │  │
│  │              └──────────────┘                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Team Member 3 Instance                                   │  │
│  │  python3 start_web_access_scrcpy.py                      │  │
│  │  --device-serial emulator-5558                           │  │
│  │  --web-port 6082 --vnc-port 5903                        │  │
│  │  ... (similar structure)                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Device Selection Features

- **Automatic Device Detection**: Lists all connected devices via `--list-devices`
- **Device Validation**: Ensures the specified device exists before starting
- **Multiple Device Warning**: Warns if multiple devices are connected without specifying a serial
- **Port Management**: Each instance uses unique ports to avoid conflicts

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  start_web_access_scrcpy.py (Parent Process)                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ScrcpyWebAccess Class                                    │  │
│  │                                                            │  │
│  │  Methods:                                                 │  │
│  │  - check_dependencies()                                   │  │
│  │  - list_devices()         → List connected devices        │  │
│  │  - check_emulator_connected() → Validate device          │  │
│  │  - start_xvfb()          → Virtual display                │  │
│  │  - start_scrcpy()        → Screen mirroring               │  │
│  │  - start_x11vnc()       → VNC server                     │  │
│  │  - start_websockify()   → WebSocket bridge                │  │
│  │  - stop()                → Cleanup all processes          │  │
│  │  - run()                  → Main loop                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                      │
│         ┌──────────────────┼──────────────────┐                 │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │  Xvfb     │      │  scrcpy  │      │  x11vnc   │           │
│  │ (display  │      │          │      │  (VNC)   │           │
│  │  :10)     │      │          │      │          │           │
│  └─────┬─────┘      └─────┬────┘      └─────┬────┘           │
│        │                  │                  │                 │
│        │                  │                  │                 │
│        └──────────┬───────┴─────────────────┘                 │
│                   │                                              │
│                   │ DISPLAY=:10                                 │
│                   ▼                                              │
│        ┌──────────────────────┐                                 │
│        │  Virtual X Display   │                                 │
│        │  (1920x1080x24)      │                                 │
│        │                      │                                 │
│        │  scrcpy window       │                                 │
│        │  renders here       │                                 │
│        └──────────────────────┘                                 │
│                   │                                              │
│                   │ x11vnc captures                              │
│                   ▼                                              │
│        ┌──────────────────────┐                                 │
│        │  x11vnc              │                                 │
│        │  (VNC Server)        │                                 │
│        │  Port: 5901          │                                 │
│        └──────────┬───────────┘                                 │
│                   │                                              │
│                   │ VNC Protocol (TCP)                          │
│                   ▼                                              │
│        ┌──────────────────────┐                                 │
│        │  websockify          │                                 │
│        │  (WebSocket Bridge)  │                                 │
│        │  Port: 6080          │                                 │
│        │                      │                                 │
│        │  - WebSocket Server  │                                 │
│        │  - VNC Client        │                                 │
│        │  - HTTP Server       │                                 │
│        │    (serves noVNC UI) │                                 │
│        └──────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
                   │
                   │ HTTP/WebSocket
                   │
┌─────────────────────────────────────────────────────────────────┐
│  Web Browser                                                     │
│  - noVNC Client (JavaScript)                                    │
│  - WebSocket Connection                                         │
│  - VNC Protocol over WebSocket                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Detailed Component Stack

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Android Emulator                                     │
│ - Android OS running                                          │
│ - ADB connection active                                      │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ ADB Protocol
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: scrcpy                                              │
│ - Connects to emulator via ADB                               │
│ - Captures screen frames                                     │
│ - Encodes video (H.264)                                      │
│ - Renders to X window                                        │
│ - Runs on virtual display :10                                │
│ - Supports --serial flag for device selection               │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ Renders to X window
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Xvfb (Virtual X Server)                             │
│ - Virtual display :10                                        │
│ - Resolution: 1920x1080x24                                   │
│ - No physical display needed                                 │
│ - Provides X11 protocol for scrcpy window                   │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ X11 protocol
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: x11vnc (VNC Server)                                 │
│ - Captures X11 display                                       │
│ - Provides VNC protocol (RFB)                               │
│ - Listens on TCP port 5901                                   │
│ - Handles multiple clients                                   │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ VNC Protocol (TCP)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: websockify (WebSocket Bridge)                       │
│ - WebSocket Server (port 6080)                               │
│ - VNC Client (connects to x11vnc)                            │
│ - Protocol translation: WebSocket ↔ VNC                      │
│ - HTTP Server (serves noVNC UI)                               │
└────────────────────┬──────────────────────────────────────────┘
                     │
                     │ HTTP/WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 6: Web Browser                                         │
│ - noVNC JavaScript Client                                    │
│ - WebSocket connection                                       │
│ - Renders VNC frames in canvas                               │
│ - Handles user input (mouse/keyboard)                        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: scrcpy Method (Video Streaming)

```
┌──────────┐
│ Browser  │
│ (noVNC)  │
└────┬─────┘
     │
     │ 1. WebSocket: Connect to ws://server:6080
     ▼
┌─────────────────────┐
│  websockify         │
│  - Accepts WebSocket│
│  - Connects to VNC  │
└────┬────────────────┘
     │
     │ 2. VNC Protocol: FramebufferUpdateRequest
     ▼
┌─────────────────────┐
│  x11vnc             │
│  (VNC Server)       │
└────┬────────────────┘
     │
     │ 3. Captures X11 display
     ▼
┌─────────────────────┐
│  Xvfb               │
│  (Virtual Display)  │
│  Display :10        │
└────┬────────────────┘
     │
     │ 4. X11 framebuffer data
     ▼
┌─────────────────────┐
│  scrcpy             │
│  - Window on :10    │
│  - Renders frames   │
└────┬────────────────┘
     │
     │ 5. ADB Protocol: Get screen data (with --serial if specified)
     ▼
┌──────────────┐
│   Emulator   │
│ (Android OS) │
└────┬─────────┘
     │
     │ 6. Screen frame data (compressed H.264)
     │ 7. Returns to scrcpy
     ▼
┌─────────────────────┐
│  scrcpy             │
│  - Decodes video    │
│  - Renders to X    │
└────┬────────────────┘
     │
     │ 8. Updated X11 framebuffer
     ▼
[Loop back to x11vnc → websockify → browser]
```

### Input Event Flow: scrcpy Method

```
┌──────────┐
│ Browser  │
│ (User clicks)
└────┬─────┘
     │
     │ 1. WebSocket: Mouse event
     ▼
┌─────────────────────┐
│  websockify         │
│  - Receives WebSocket│
│  - Translates to VNC │
└────┬────────────────┘
     │
     │ 2. VNC Protocol: PointerEvent
     ▼
┌─────────────────────┐
│  x11vnc             │
│  - Receives VNC event│
│  - Translates to X11│
└────┬────────────────┘
     │
     │ 3. X11: XButtonPress/XButtonRelease
     ▼
┌─────────────────────┐
│  Xvfb               │
│  (Virtual Display)  │
└────┬────────────────┘
     │
     │ 4. X11 event delivered to scrcpy window
     ▼
┌─────────────────────┐
│  scrcpy             │
│  - Receives X11 event│
│  - Translates to ADB│
└────┬────────────────┘
     │
     │ 5. ADB: input tap X Y (to specified device)
     ▼
┌──────────────┐
│   Emulator   │
│ (Processes input)
└──────────────┘
```

---

## Method B: ADB-Based Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  start_web_access_adb.py (Parent Process)                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ADBWebAccess Class                                       │  │
│  │                                                            │  │
│  │  Methods:                                                 │  │
│  │  - check_dependencies()                                   │  │
│  │  - check_emulator_connected()                              │  │
│  │  - start_adb_web_server()                                 │  │
│  │  - stop()                                                  │  │
│  │  - run()                                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                      │
│                            │ subprocess.Popen()                    │
│                            ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  adb_web_server.py (Child Process)                       │  │
│  │                                                            │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  HTTPServer (0.0.0.0:6080)                         │  │  │
│  │  │                                                    │  │  │
│  │  │  ┌──────────────────────────────────────────────┐ │  │  │
│  │  │  │  ADBWebHandler                               │ │  │  │
│  │  │  │                                              │ │  │  │
│  │  │  │  GET  /              → HTML page             │ │  │  │
│  │  │  │  GET  /screenshot    → Screenshot PNG       │ │  │  │
│  │  │  │  POST /input         → Input events         │ │  │  │
│  │  │  └──────────────────────────────────────────────┘ │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                            │                               │  │
│  │                            │ subprocess.run()             │  │
│  │                            ▼                               │  │
│  │              ┌──────────────────────────────┐             │  │
│  │              │  ADB Commands                │             │  │
│  │              │  - adb exec-out screencap -p │             │  │
│  │              │  - adb shell input tap X Y   │             │  │
│  │              │  - adb shell input text ...  │             │  │
│  │              │  - adb shell input keyevent  │             │  │
│  │              └──────────────────────────────┘             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: ADB Method

```
┌──────────┐
│ Browser  │
└────┬─────┘
     │
     │ 1. HTTP GET /screenshot
     ▼
┌─────────────────────┐
│ adb_web_server.py   │
│ ADBWebHandler       │
└────┬────────────────┘
     │
     │ 2. subprocess.run(['adb', 'exec-out', 'screencap', '-p'])
     ▼
┌──────────┐
│   ADB    │
└────┬─────┘
     │
     │ 3. Connects to emulator via ADB protocol
     ▼
┌──────────────┐
│   Emulator   │
│ (Android OS) │
└────┬─────────┘
     │
     │ 4. Captures screen as PNG
     │ 5. Returns PNG data (~500KB - 2MB)
     ▼
┌──────────┐
│   ADB    │
└────┬─────┘
     │
     │ 6. PNG data via stdout
     ▼
┌─────────────────────┐
│ adb_web_server.py   │
│ ADBWebHandler       │
└────┬────────────────┘
     │
     │ 7. HTTP 200 OK
     │    Content-Type: image/png
     │    Body: PNG image data
     ▼
┌──────────┐
│ Browser  │
│ (displays image, waits 100ms, requests again)
└──────────┘
```

### Input Event Flow: ADB Method

```
┌──────────┐
│ Browser  │
│ (User clicks at x=100, y=200)
└────┬─────┘
     │
     │ 1. HTTP POST /input
     │    { "action": "tap", "x": 100, "y": 200 }
     ▼
┌─────────────────────┐
│ adb_web_server.py   │
│ ADBWebHandler       │
│ send_tap(100, 200)  │
└────┬────────────────┘
     │
     │ 2. subprocess.run(['adb', 'shell', 'input', 'tap', '100', '200'])
     ▼
┌──────────┐
│   ADB    │
└────┬─────┘
     │
     │ 3. Sends input event to emulator
     ▼
┌──────────────┐
│   Emulator   │
│ (Receives tap event, processes it)
└──────────────┘
```

---

## Process Management

### Process Hierarchy

```
start_web_access_*.py (Parent Process, PID: 1000)
│
├── adb_web_server.py (Child Process, PID: 1001)
│   └── ADB subprocess calls (temporary, PID: varies)
│
└── [scrcpy method only]
    ├── Xvfb (Child Process, PID: 1002)
    ├── scrcpy (Child Process, PID: 1003)
    ├── x11vnc (Child Process, PID: 1004)
    │   └── x11vnc child (daemon, PID: 1005)
    └── websockify (Child Process, PID: 1006)
```

### Signal Handling

Both scripts handle:
- `SIGINT` (Ctrl+C): Graceful shutdown
- `SIGTERM`: Graceful shutdown

On signal:
1. Set `self.running = False`
2. Call `stop()` method
3. Terminate all child processes
4. Wait for processes to exit (with timeout)
5. Force kill if needed
6. Exit cleanly

### Process Monitoring

The parent process monitors child processes:
- Checks if processes are still alive (`poll()`)
- For x11vnc (background mode): Checks VNC port instead of process
- Logs errors if processes die unexpectedly
- Exits if critical processes die

---

## Network Architecture

### Port Usage

#### scrcpy Method
- **Web Port**: 6080 (default, configurable)
- **VNC Port**: 5901 (default, configurable)
- **Protocols**: 
  - HTTP (for noVNC UI)
  - WebSocket (for VNC data)
  - VNC/RFB (internal, x11vnc ↔ websockify)
- **Binding**: `0.0.0.0:6080` (websockify), `localhost:5901` (x11vnc)
- **Multi-Instance**: Each team member can use different ports (e.g., 6080, 6081, 6082)

#### ADB Method
- **Web Port**: 6080 (default, configurable)
- **Protocol**: HTTP
- **Binding**: `0.0.0.0:6080` (all interfaces)

### Network Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Linux Server (202.78.161.193)                              │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Firewall (if enabled)                                 │ │
│  │  - Allow port 6080 (web access)                        │ │
│  │  - Allow port 5901 (VNC, optional for direct access)   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                  │
│                            │ Internet/Network                 │
│                            ▼                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
                            │
┌─────────────────────────────────────────────────────────────┐
│  Mac Laptop                                                  │
│                                                               │
│  Option 1: Direct Access                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Browser                                                │ │
│  │  http://202.78.161.193:6080                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Option 2: SSH Tunnel (Recommended)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SSH Client                                            │ │
│  │  ssh -L 6080:localhost:6080 user@server               │ │
│  │  └─→ Creates tunnel: localhost:6080 → server:6080    │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                  │
│                            │                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Browser                                                │ │
│  │  http://localhost:6080                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Security Considerations

1. **No Authentication**: Scripts provide no built-in authentication
2. **Network Binding**: Binding to `0.0.0.0` allows remote access
3. **Firewall**: Should be configured to restrict access
4. **SSH Tunnel**: Recommended for secure remote access
5. **Local Use**: Designed for local network or SSH-tunneled access

---

## Technology Stack

### scrcpy Method

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Script** | Python 3 | Orchestration |
| **Xvfb** | X Virtual Framebuffer | Virtual display |
| **scrcpy** | Screen Copy (v3.x) | Screen mirroring |
| **x11vnc** | VNC Server for X11 | VNC protocol |
| **websockify** | Python WebSocket bridge | WebSocket ↔ VNC |
| **noVNC** | JavaScript VNC client | Web frontend |
| **Protocols** | HTTP, WebSocket, VNC/RFB | Communication |

### ADB Method

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Script** | Python 3 | Orchestration |
| **HTTP Server** | Python `http.server` | Web server |
| **ADB** | Android Debug Bridge | Device communication |
| **Protocol** | HTTP/HTTPS | Web communication |
| **Frontend** | HTML/JavaScript | Web UI |

---

## Key Design Decisions

### 1. Separate Scripts vs. Single Script

**Decision**: Two separate scripts instead of one with flags

**Rationale**:
- Clear separation of concerns
- Different dependency requirements
- Easier to maintain and understand
- Better error messages (script-specific)

### 2. Process Management

**Decision**: Parent process manages child processes

**Rationale**:
- Clean process hierarchy
- Easier cleanup on exit
- Better error handling
- Process monitoring

### 3. Network Binding

**Decision**: Bind to `0.0.0.0` (all interfaces)

**Rationale**:
- Supports remote access out of the box
- Works with SSH tunnels
- Can be restricted by firewall if needed

### 4. scrcpy v3.x Support

**Decision**: Use Xvfb + x11vnc instead of `--vnc` flag

**Rationale**:
- scrcpy v3.x removed `--vnc` flag
- Xvfb + x11vnc provides same functionality
- More flexible and compatible
- Works with headless servers

### 5. Multi-Device Support

**Decision**: Support device selection via `--device-serial` parameter

**Rationale**:
- Enables multiple team members to work simultaneously
- Each member can connect to their own emulator
- Prevents conflicts when multiple devices are connected
- Validates device existence before starting
- Provides clear warnings when multiple devices detected

**Implementation**:
- `list_devices()` method queries ADB for connected devices
- `check_emulator_connected()` validates specified device exists
- `start_scrcpy()` passes `--serial` flag to scrcpy for device targeting
- Port isolation allows multiple instances to run simultaneously

### 6. Error Handling

**Decision**: Strict dependency checking, clear error messages

**Rationale**:
- Better user experience
- Easier troubleshooting
- Prevents runtime errors
- Provides installation guidance

---

## Performance Characteristics

### scrcpy Method

- **Frame Rate**: 30-60 FPS (depending on network)
- **Latency**: ~30-50ms
- **Bandwidth**: ~5-20 Mbps (depending on content)
- **CPU**: Moderate to high
- **Memory**: Moderate (~200-500 MB)
- **Multi-Instance**: Each instance uses separate resources (isolated)

### ADB Method

- **Frame Rate**: ~10 FPS (limited by polling interval)
- **Latency**: ~100-200ms
- **Bandwidth**: ~1-5 Mbps (depending on screen content)
- **CPU**: Low to moderate
- **Memory**: Low (~50-100 MB)

---

## Future Enhancements

Potential improvements:

1. **Authentication**: Add password protection
2. **SSL/TLS**: Support HTTPS/WSS
3. **Multi-device Management**: Web UI for managing multiple instances
4. **Configuration File**: YAML/JSON config
5. **Logging**: Structured logging to file
6. **Metrics**: Performance metrics collection
7. **Health Checks**: Built-in health check endpoints
8. **Auto-restart**: Automatic restart on failure

---

## Conclusion

The web access architecture provides two complementary approaches for remote Android emulator control:

- **scrcpy Method** (Recommended): High-performance, smooth experience with 30-60 FPS, ideal for interactive use and team collaboration. Supports multiple team members working simultaneously with device selection and port isolation.
- **ADB Method**: Simple, lightweight, good for basic use cases and low-resource scenarios

Both methods are designed for ease of use, reliability, and remote access support. The architecture prioritizes clarity, maintainability, and proper resource management. The scrcpy method is recommended for production use, especially when multiple team members need to work simultaneously, as it provides better performance and supports device selection for multi-user scenarios.

