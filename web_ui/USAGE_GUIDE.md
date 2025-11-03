# Web Access Scripts Usage Guide

This guide explains how to use the two web access scripts for controlling Android emulators through a web browser.

## Overview

There are two web access scripts available:

1. **`start_web_access_adb.py`** - ADB-based web access (~10 FPS, manual refresh)
2. **`start_web_access_scrcpy.py`** - scrcpy-based web access (30-60 FPS, automatic refresh)

Both scripts allow you to control an Android emulator running on a Linux server from a web browser on your local machine (e.g., Mac laptop).

---

## Quick Start

### Prerequisites

1. **Android emulator must be running** on the Linux server
   ```bash
   # Check if emulator is connected
   adb devices
   ```

2. **Server must be accessible** from your local machine
   - Direct network access, or
   - SSH tunnel

### Choosing the Right Script

| Feature | ADB Script | scrcpy Script |
|---------|-----------|---------------|
| **Performance** | ~10 FPS | 30-60 FPS |
| **Update Method** | Polling (auto-refresh) | Real-time streaming |
| **Dependencies** | ADB only | ADB + scrcpy + Xvfb + x11vnc + websockify |
| **Setup Complexity** | Simple | More complex |
| **Use Case** | Quick testing, basic control | Smooth interaction, demos |

**Recommendation:** Use `start_web_access_scrcpy.py` for better performance, unless you have dependency issues.

---

## Script 1: ADB Web Access (`start_web_access_adb.py`)

### Overview

Uses ADB `screencap` and `input` commands to capture screenshots and send input events. Screenshots are automatically refreshed every ~100ms (~10 FPS).

### Requirements

- ✅ **ADB** (Android Debug Bridge)
- ✅ **Android emulator running** and connected via ADB
- ✅ **`adb_web_server.py`** (must exist in the same directory)

### Installation

No additional installation needed if ADB is already available.

### Usage

#### Basic Usage

```bash
# Start the web server (default port: 6080)
python3 start_web_access_adb.py
```

#### Custom Port

```bash
# Use a different port
python3 start_web_access_adb.py --web-port 8080
```

### Output

When started successfully, you'll see:

```
======================================================================
🚀 ADB WEB SERVER READY
======================================================================

🌐 Open in your web browser:
   Local:   http://localhost:6080
   Network: http://202.78.161.193:6080

📱 Method: ADB Screencap/Input
🌍 Web Port: 6080

💡 Usage:
   - Screenshot updates: ~10 FPS (automatic polling)
   - Click on screen to interact with emulator
   - Type text in the input field and click 'Send Text'
   - Use Back/Home buttons for navigation
   - Press Ctrl+C here to stop

⚠️  Note: This uses screenshot polling, so may have some lag.
   For better performance, use start_web_access_scrcpy.py
======================================================================
```

### Accessing from Remote Machine

#### Option 1: Direct Access (if firewall allows)

From your Mac browser, open:
```
http://202.78.161.193:6080
```

#### Option 2: SSH Tunnel (recommended)

On your Mac terminal:
```bash
ssh -L 6080:localhost:6080 ligu@202.78.161.193
```

Then open in browser:
```
http://localhost:6080
```

### Web Interface Features

- **Screen Display**: Shows current emulator screen (auto-refreshes)
- **Click/Tap**: Click anywhere on the screen to tap that location
- **Text Input**: Type text in the input field and click "Send Text"
  - **Note**: This method is reliable for all text input, including special characters
- **Navigation Buttons**: Back, Home, Recent Apps buttons
- **Refresh Control**: Manual refresh button (though auto-refresh is enabled)

### Text Input Tips

- **Best for**: Reliable text input, special characters, passwords
- **Works with**: All input field types
- **Alternative**: You can also use `adb shell input text "your text"` from terminal

### Stopping the Server

Press `Ctrl+C` in the terminal where the script is running.

---

## Script 2: scrcpy Web Access (`start_web_access_scrcpy.py`)

### Overview

Uses scrcpy (v3.x) with Xvfb (virtual display) and x11vnc to provide real-time video streaming at 30-60 FPS. This offers a smooth, responsive experience similar to using scrcpy directly.

### Requirements

- ✅ **ADB** (Android Debug Bridge)
- ✅ **scrcpy v3.x** (v3.3.3+ recommended)
- ✅ **Xvfb** (X virtual framebuffer)
- ✅ **x11vnc** (VNC server for X11)
- ✅ **websockify** (Python package)
- ✅ **noVNC** (optional, for better web UI)

### Installation

#### Install Dependencies

```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y scrcpy xvfb x11vnc

# Install Python package
pip install websockify
# or
pip3 install --user websockify

# Optional: Clone noVNC for better UI
git clone https://github.com/novnc/noVNC.git novnc
```

#### Verify Installation

```bash
# Check all dependencies
which adb
which scrcpy
which Xvfb
which x11vnc
which websockify
```

### Usage

#### Basic Usage

```bash
# Start with default ports (web: 6080, VNC: 5901)
python3 start_web_access_scrcpy.py
```

#### Custom Ports

```bash
# Custom web port and VNC port
python3 start_web_access_scrcpy.py --web-port 6090 --vnc-port 5902
```

### Output

When started successfully, you'll see:

```
======================================================================
🚀 SCRCPY v3.x WEB SERVER READY
======================================================================

🌐 Open in your web browser:
   Local:   http://localhost:6080
   Network: http://202.78.161.193:6080

📱 Method: scrcpy v3.x + Xvfb + x11vnc (Real-time streaming)
🖥️  Virtual Display: :10
🔌 VNC Port: 5901
🌍 Web Port: 6080

💡 Usage:
   - Screen updates automatically (30-60 FPS)
   - Click and drag to interact with emulator
   - Type on your keyboard to input text
   - Smooth, responsive experience
   - Press Ctrl+C here to stop

🌍 Remote Access (from Mac):
   - From your Mac, open: http://202.78.161.193:6080/vnc_lite.html
   - Or use full version: http://202.78.161.193:6080/vnc.html
   - Ensure firewall allows port 6080
   - If using SSH tunnel: ssh -L 6080:localhost:6080 ligu@202.78.161.193

✨ Performance: Real-time streaming with low latency
======================================================================
```

### Accessing from Remote Machine

#### Option 1: Direct Access

From your Mac browser, open:
```
http://202.78.161.193:6080/vnc_lite.html
```

Or for the full version:
```
http://202.78.161.193:6080/vnc.html
```

#### Option 2: SSH Tunnel

On your Mac terminal:
```bash
ssh -L 6080:localhost:6080 ligu@202.78.161.193
```

Then open:
```
http://localhost:6080/vnc_lite.html
```

### Web Interface Features

- **Real-time Streaming**: Smooth 30-60 FPS video stream
- **Mouse Interaction**: Click, drag, and scroll
- **Keyboard Input**: Type directly (keyboard focus on the VNC canvas)
  - **Important**: Click on the VNC canvas first to give it keyboard focus
  - **If keyboard doesn't work**: See "Keyboard Troubleshooting" below
  - **Alternative**: Use ADB method for reliable text input
- **Touch Events**: Multi-touch gestures supported
- **Low Latency**: Near real-time response

### Keyboard Input Tips

**For reliable text input:**
1. **Click on the VNC canvas** (the screen display area) before typing
2. **Click in the input field** you want to type in
3. **Type normally** - characters should appear

**If keyboard doesn't work:**
- The app may be showing a numeric-only keypad (this is expected for zip code, phone fields)
- Use the ADB method for text input: `adb shell input text "your text"`
- Or use the noVNC on-screen keyboard (keyboard icon in toolbar)
- See `KEYBOARD_TROUBLESHOOTING.md` for detailed solutions

### Troubleshooting

#### scrcpy Version Issues

If you see an error about `--vnc` flag:
- This script requires **scrcpy v3.x** (which removed `--vnc`)
- If you have scrcpy v2.x, use `start_web_access_adb.py` instead

#### Missing Dependencies

The script will check for all dependencies and provide installation instructions if any are missing.

#### Port Conflicts

If ports are in use:
```bash
# Use different ports
python3 start_web_access_scrcpy.py --web-port 6090 --vnc-port 5902
```

### Stopping the Server

Press `Ctrl+C` in the terminal. The script will clean up all processes (Xvfb, scrcpy, x11vnc, websockify).

---

## Comparison: ADB vs scrcpy

| Aspect | ADB Script | scrcpy Script |
|--------|-----------|---------------|
| **Performance** | ~10 FPS | 30-60 FPS |
| **Latency** | Higher (~100ms) | Lower (~30ms) |
| **CPU Usage** | Lower | Higher |
| **Memory Usage** | Lower | Higher |
| **Setup** | Simple | More complex |
| **Dependencies** | ADB only | Multiple tools |
| **Network Usage** | Lower (polling) | Higher (streaming) |
| **Best For** | Quick testing | Smooth interaction |

---

## Keyboard Input Troubleshooting

If you're having trouble typing alphabetic characters:

### Quick Fix
1. **Click on the VNC canvas** (screen display area) to focus it
2. **Click in the input field** where you want to type
3. Try typing again

### Common Causes

1. **Numeric-only field**: Some apps show numeric keypad (zip code, phone) - this is expected
2. **VNC canvas not focused**: Click on the screen area first
3. **Keyboard events not captured**: Use ADB method for text input

### Solutions

**Option 1: Use ADB for text input**
```bash
# From terminal on Linux server
adb shell input text "Hello World"
```

**Option 2: Use ADB web interface**
- Open `http://server-ip:6081` (ADB web interface) in another tab
- Use the text input field there

**Option 3: Use noVNC on-screen keyboard**
- Click the keyboard icon in noVNC toolbar
- Use the virtual keyboard

For detailed troubleshooting, see `KEYBOARD_TROUBLESHOOTING.md`

---

## Common Issues and Solutions

### Issue: "No devices connected"

**Solution:**
```bash
# Check if emulator is running
adb devices

# If not, start the emulator first
# Then run the web access script again
```

### Issue: "Port already in use"

**Solution:**
```bash
# Use a different port
python3 start_web_access_adb.py --web-port 8080
# or
python3 start_web_access_scrcpy.py --web-port 6090
```

### Issue: "Missing dependency: Xvfb"

**Solution:**
```bash
sudo apt-get install xvfb
```

### Issue: "Cannot connect from Mac"

**Solution:**
1. Check firewall settings on Linux server
2. Use SSH tunnel instead:
   ```bash
   ssh -L 6080:localhost:6080 user@server-ip
   ```

### Issue: "Web page shows directory listing"

**Solution (for scrcpy script):**
- Access the VNC client directly: `http://server-ip:6080/vnc_lite.html`
- Or check if `novnc/index.html` exists (should auto-redirect)

---

## Advanced Usage

### Running in Background

```bash
# Using nohup
nohup python3 start_web_access_scrcpy.py > web_access.log 2>&1 &

# Check if running
ps aux | grep start_web_access

# Stop the process
pkill -f start_web_access_scrcpy
```

### Multiple Instances

You can run multiple instances on different ports:

```bash
# Terminal 1
python3 start_web_access_adb.py --web-port 6080

# Terminal 2
python3 start_web_access_adb.py --web-port 6081
```

### Custom Configuration

Both scripts accept command-line arguments. See help:

```bash
python3 start_web_access_adb.py --help
python3 start_web_access_scrcpy.py --help
```

---

## Security Considerations

⚠️ **Important Security Notes:**

1. **No Authentication**: These scripts provide no authentication. Anyone with network access can control the emulator.

2. **Firewall**: Use a firewall to restrict access, or use SSH tunnels.

3. **Local Use**: Designed for local network use or SSH tunneled access.

4. **Production**: Not recommended for production environments without additional security measures.

---

## Next Steps

- For architecture details, see `ARCHITECTURE.md`
- For troubleshooting, check script logs
- For emulator setup, see project documentation

---

## Summary

| Task | Command |
|------|---------|
| **Start ADB web access** | `python3 start_web_access_adb.py` |
| **Start scrcpy web access** | `python3 start_web_access_scrcpy.py` |
| **Custom port** | Add `--web-port <port>` |
| **Access from Mac** | `http://server-ip:port` or `http://localhost:port` (via SSH tunnel) |
| **Stop server** | Press `Ctrl+C` |

Choose the script that best fits your needs:
- **Simple and quick**: Use `start_web_access_adb.py`
- **Smooth and responsive**: Use `start_web_access_scrcpy.py`

