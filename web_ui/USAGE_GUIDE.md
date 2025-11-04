# Web Access Scripts Usage Guide

This guide explains how to use the two web access scripts for controlling Android emulators through a web browser.

## Overview

There are two web access scripts available:

1. **`start_web_access_scrcpy.py`** (Recommended) - scrcpy-based web access (30-60 FPS, real-time streaming)
2. **`start_web_access_adb.py`** - ADB-based web access (~10 FPS, polling-based)

Both scripts allow you to control an Android emulator running on a Linux server from a web browser on your local machine (e.g., Mac laptop).

**Recommendation:** Use `start_web_access_scrcpy.py` for the best performance and smoothest experience. It provides real-time video streaming at 30-60 FPS with low latency, making it ideal for interactive use and team collaboration.

---

## Global Environment Setup

Before using the web access scripts, you need to set up the Android SDK environment variables. This ensures that `adb`, `emulator`, and other Android tools are available in your PATH.

### Setup Android Environment Variables

Run the following commands, replacing `<intended_path_here>` with your actual Android SDK path (e.g., `/home/username/Android/Sdk`):

```bash
# Set ANDROID_HOME to your Android SDK path
export ANDROID_HOME=<intended_path_here>

# Add to ~/.bashrc for persistence
echo "export ANDROID_HOME=$ANDROID_HOME" >> ~/.bashrc

echo 'export SDK=$ANDROID_HOME' >> ~/.bashrc

echo 'export ANDROID_SDK_ROOT=$ANDROID_HOME' >> ~/.bashrc

echo 'export ANDROID_AVD_HOME=$ANDROID_HOME/avd' >> ~/.bashrc

echo 'export PATH=$SDK/emulator:$SDK/tools:$SDK/tools/bin:$SDK/platform-tools:$PATH' >> ~/.bashrc

# Reload bash configuration
source ~/.bashrc
```

### Server-Specific Configuration

**For server 202.78.161.193 users:**

If you are using server 202.78.161.193, the Android Home is located at `/shared/ken/.android`. Use this command:

```bash
export ANDROID_HOME=/shared/ken/.android
```

Then continue with the rest of the setup commands above (adding to `~/.bashrc`, etc.).

### Verify Setup

After running the setup commands, verify that the environment is configured correctly:

```bash
# Check if ANDROID_HOME is set
echo $ANDROID_HOME

# Verify adb is in PATH
which adb

# Verify emulator is in PATH
which emulator

# Check adb version
adb version
```

**Note:** If you're using a different shell (e.g., zsh), replace `~/.bashrc` with `~/.zshrc` in the commands above.

---

## Quick Start

### Step 1: Start the Android Emulator

Before starting the web access scripts, you must first start the Android emulator on the Linux server.

#### Start Emulator

```bash
# Start the emulator with recommended settings
emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8556 -port 5556
```

**Command Options Explained:**
- `-avd AWAvd`: Uses the AVD named "AWAvd"
- `-snapshot clean`: Starts from a clean snapshot (faster boot)
- `-no-window`: Runs headless (no GUI window)
- `-no-audio`: Disables audio (not needed for web access)
- `-skip-adb-auth`: Skips ADB authentication
- `-no-boot-anim`: Disables boot animation (faster startup)
- `-gpu auto`: Auto-selects GPU mode
- `-no-snapshot-save`: Doesn't save snapshots (faster)
- `-read-only`: Uses read-only mode
- `-grpc 8556`: GRPC port for emulator control
- `-port 5556`: ADB port (device will appear as `emulator-5556`)

#### Verify Emulator is Running

```bash
# Check if emulator is connected via ADB
adb devices

# You should see output like:
# List of devices attached
# emulator-5556    device
```

#### Multiple Emulators (Team Members)

If multiple team members need to work simultaneously, each can start their own emulator with a different port:

```bash
# Team member 1
emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8556 -port 5554

# Team member 2
emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8557 -port 5556

# Team member 3
emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8558 -port 5558
```

**Note:** Each emulator instance needs:
- Unique ADB port (`-port`): 5554, 5556, 5558, etc.
- Unique GRPC port (`-grpc`): 8556, 8557, 8558, etc.

### Step 2: Prerequisites

1. **Android emulator must be running** (see Step 1 above)
   ```bash
   # Verify emulator is connected
   adb devices
   ```

2. **Server must be accessible** from your local machine
   - Direct network access, or
   - SSH tunnel

### Choosing the Right Script

| Feature | scrcpy Script (Recommended) | ADB Script |
|---------|------------------------------|------------|
| **Performance** | 30-60 FPS | ~10 FPS |
| **Update Method** | Real-time streaming | Polling (auto-refresh) |
| **Latency** | Low (~30-50ms) | Higher (~100-200ms) |
| **User Experience** | Smooth, responsive | Basic, some lag |
| **Dependencies** | ADB + scrcpy + Xvfb + x11vnc + websockify | ADB only |
| **Setup Complexity** | More complex | Simple |
| **Use Case** | Smooth interaction, demos, team collaboration | Quick testing, basic control |
| **Multi-Device Support** | ✅ Yes (device selection) | ⚠️ Limited |

**Recommendation:** Use `start_web_access_scrcpy.py` for the best experience. It provides real-time streaming, low latency, and supports multiple team members working simultaneously. Only use `start_web_access_adb.py` if you have dependency issues or need a simpler setup.

---

## Script 1: scrcpy Web Access (`start_web_access_scrcpy.py`) - Recommended

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

#### List Available Devices

```bash
# List all connected emulators/devices
python3 start_web_access_scrcpy.py --list-devices

# Output example:
# Connected devices:
#   1. emulator-5554
#   2. emulator-5556
#   3. emulator-5558
```

#### Basic Usage

```bash
# Start with default ports (web: 6080, VNC: 5901)
# Automatically connects to first available device
python3 start_web_access_scrcpy.py
```

#### Select Specific Device (Multiple Emulators)

When multiple emulators are running, specify which one to connect to:

```bash
# Connect to specific emulator
python3 start_web_access_scrcpy.py --device-serial emulator-5556

# With custom ports
python3 start_web_access_scrcpy.py --device-serial emulator-5556 --web-port 6081 --vnc-port 5902
```

#### Custom Ports

```bash
# Custom web port and VNC port
python3 start_web_access_scrcpy.py --web-port 6090 --vnc-port 5902
```

#### Multiple Team Members Example

Each team member can run their own instance targeting their emulator:

```bash
# Team member 1
python3 start_web_access_scrcpy.py --device-serial emulator-5554 --web-port 6080 --vnc-port 5901

# Team member 2
python3 start_web_access_scrcpy.py --device-serial emulator-5556 --web-port 6081 --vnc-port 5902

# Team member 3
python3 start_web_access_scrcpy.py --device-serial emulator-5558 --web-port 6082 --vnc-port 5903
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

## Script 2: ADB Web Access (`start_web_access_adb.py`)

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

## Comparison: scrcpy vs ADB

| Aspect | scrcpy Script (Recommended) | ADB Script |
|--------|------------------------------|------------|
| **Performance** | 30-60 FPS | ~10 FPS |
| **Latency** | Lower (~30-50ms) | Higher (~100-200ms) |
| **CPU Usage** | Higher | Lower |
| **Memory Usage** | Higher | Lower |
| **Setup** | More complex | Simple |
| **Dependencies** | Multiple tools | ADB only |
| **Network Usage** | Higher (streaming) | Lower (polling) |
| **Best For** | Smooth interaction, team collaboration | Quick testing |
| **Multi-Device Support** | ✅ Yes (device selection) | ⚠️ Limited |

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

# If not, start the emulator first:
emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8556 -port 5556

# Wait for emulator to boot (check with: adb devices)
# Then run the web access script again
```

### Issue: "Multiple devices detected" (scrcpy script)

**Solution:**
```bash
# List available devices
python3 start_web_access_scrcpy.py --list-devices

# Specify which device to use
python3 start_web_access_scrcpy.py --device-serial emulator-5556
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

You can run multiple instances on different ports. This is especially useful when multiple team members are working with different emulators:

#### ADB Method - Multiple Instances

```bash
# Terminal 1
python3 start_web_access_adb.py --web-port 6080

# Terminal 2
python3 start_web_access_adb.py --web-port 6081
```

#### scrcpy Method - Multiple Instances with Device Selection

```bash
# Team member 1 - emulator on port 5554
python3 start_web_access_scrcpy.py --device-serial emulator-5554 --web-port 6080 --vnc-port 5901

# Team member 2 - emulator on port 5556
python3 start_web_access_scrcpy.py --device-serial emulator-5556 --web-port 6081 --vnc-port 5902

# Team member 3 - emulator on port 5558
python3 start_web_access_scrcpy.py --device-serial emulator-5558 --web-port 6082 --vnc-port 5903
```

**Important:** Each team member should:
1. Start their emulator with a unique `-port` (e.g., 5554, 5556, 5558)
2. Use `--device-serial` to specify their emulator
3. Use unique `--web-port` and `--vnc-port` to avoid conflicts

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

### Complete Workflow

| Step | Task | Command |
|------|------|---------|
| **1** | **Start emulator** | `emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8556 -port 5556` |
| **2** | **Verify emulator** | `adb devices` |
| **3** | **List devices** (scrcpy only) | `python3 start_web_access_scrcpy.py --list-devices` |
| **4** | **Start scrcpy web access** (Recommended) | `python3 start_web_access_scrcpy.py` |
| **4** | **Start scrcpy with device** | `python3 start_web_access_scrcpy.py --device-serial emulator-5556` |
| **4** | **Start ADB web access** | `python3 start_web_access_adb.py` |
| **5** | **Custom port** | Add `--web-port <port>` |
| **6** | **Access from Mac** | `http://server-ip:port` or `http://localhost:port` (via SSH tunnel) |
| **7** | **Stop server** | Press `Ctrl+C` |

### Quick Reference

| Task | Command |
|------|---------|
| **Start emulator** | `emulator -avd AWAvd -snapshot clean -no-window -no-audio -skip-adb-auth -no-boot-anim -gpu auto -no-snapshot-save -read-only -grpc 8556 -port 5556` |
| **Start scrcpy web access** (Recommended) | `python3 start_web_access_scrcpy.py` |
| **List devices** | `python3 start_web_access_scrcpy.py --list-devices` |
| **Select device** | `python3 start_web_access_scrcpy.py --device-serial emulator-5556` |
| **Start ADB web access** | `python3 start_web_access_adb.py` |
| **Custom port** | Add `--web-port <port>` |
| **Access from Mac** | `http://server-ip:port` or `http://localhost:port` (via SSH tunnel) |
| **Stop server** | Press `Ctrl+C` |

Choose the script that best fits your needs:
- **Smooth and responsive** (Recommended): Use `start_web_access_scrcpy.py` - Best for interactive use, demos, and team collaboration
- **Simple and quick**: Use `start_web_access_adb.py` - Use only if you have dependency issues or need a simpler setup

