#!/usr/bin/env python3
"""
scrcpy v3.x Web Access Server for Android Emulator

This server uses scrcpy v3.3.3+ with Xvfb (virtual display) + x11vnc for web access.
Works with scrcpy v3.x which removed the --vnc flag.

Requirements:
    - ADB (required)
    - scrcpy v3.x (required)
    - Xvfb (X virtual framebuffer, for virtual display)
    - x11vnc (VNC server for X11)
    - websockify (pip install websockify, required)
    - noVNC (optional, for better web UI)

Usage:
    python3 start_web_access_scrcpy.py
    python3 start_web_access_scrcpy.py --web-port 6080 --vnc-port 5901
    python3 start_web_access_scrcpy.py --device-serial emulator-5554
    python3 start_web_access_scrcpy.py --list-devices  # List available devices
"""

import os
import sys
import time
import subprocess
import logging
import socket
import shutil
import signal
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrcpyWebAccess:
    def __init__(self, web_port: int = 6080, vnc_port: int = 5901, device_serial: str = None):
        self.web_port = web_port
        self.vnc_port = vnc_port
        self.device_serial = device_serial
        self.scrcpy_process = None
        self.xvfb_process = None
        self.x11vnc_process = None
        self.websockify_process = None
        self.running = True
        self.display_num = 10  # Virtual display number
    
    def _get_scrcpy_version(self) -> str:
        """Get scrcpy version string."""
        try:
            result = subprocess.run(
                ["scrcpy", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if lines:
                return lines[0].strip()
            return "unknown"
        except Exception:
            return "unknown"
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        missing = []
        
        # ADB is required
        if not shutil.which("adb"):
            missing.append("adb")
        
        # scrcpy is required
        if not shutil.which("scrcpy"):
            missing.append("scrcpy")
        
        # Xvfb is required (for virtual display)
        if not shutil.which("Xvfb"):
            missing.append("Xvfb")
        
        # x11vnc is required (for VNC server)
        if not shutil.which("x11vnc"):
            missing.append("x11vnc")
        
        # websockify is required
        if not shutil.which("websockify"):
            missing.append("websockify")
        
        if missing:
            logger.error("Missing required dependencies: %s", ", ".join(missing))
            logger.error("\nInstallation instructions:")
            logger.error("  - adb: Usually part of Android SDK")
            logger.error("  - scrcpy: sudo apt-get install scrcpy (or brew install scrcpy)")
            logger.error("  - Xvfb: sudo apt-get install xvfb")
            logger.error("  - x11vnc: sudo apt-get install x11vnc")
            logger.error("  - websockify: pip install websockify")
            logger.error("")
            logger.error("Or run: ./install_scrcpy_v3_deps.sh")
            return False
        
        # Verify scrcpy is v3.x (doesn't have --vnc)
        try:
            result = subprocess.run(
                ["scrcpy", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            help_text = result.stdout + result.stderr
            
            # Check if it's v3.x (no --vnc flag)
            if "--vnc" in help_text:
                version = self._get_scrcpy_version()
                logger.error("="*70)
                logger.error("This script is designed for scrcpy v3.x (without --vnc)")
                logger.error("="*70)
                logger.error("Your scrcpy version: %s", version)
                logger.error("")
                logger.error("scrcpy v2.x has --vnc flag which this script doesn't use")
                logger.error("This script uses Xvfb + x11vnc method for scrcpy v3.x")
                logger.error("="*70)
                # Continue anyway, might work
        except Exception:
            pass
        
        return True
    
    def list_devices(self) -> list:
        """List all connected devices and return their serial numbers."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = []
            for line in lines:
                if line.strip() and 'device' in line:
                    serial = line.split()[0]
                    devices.append(serial)
            
            return devices
        except Exception as e:
            logger.error("Error listing devices: %s", str(e))
            return []
    
    def check_emulator_connected(self) -> bool:
        """Check if emulator is connected via ADB."""
        devices = self.list_devices()
        
        if not devices:
            logger.warning("No devices connected. Make sure emulator is running.")
            logger.info("You can check with: adb devices")
            return False
        
        logger.info(f"Found {len(devices)} device(s) connected")
        
        # If device_serial is specified, verify it exists
        if self.device_serial:
            if self.device_serial not in devices:
                logger.error(f"Specified device '{self.device_serial}' not found!")
                logger.error(f"Available devices: {', '.join(devices)}")
                return False
            logger.info(f"Using device: {self.device_serial}")
        elif len(devices) > 1:
            logger.warning(f"Multiple devices detected: {', '.join(devices)}")
            logger.warning("scrcpy will connect to the first device. Use --device-serial to specify which one.")
            logger.info(f"Will use: {devices[0]}")
        else:
            logger.info(f"Using device: {devices[0]}")
        
        return True
    
    def start_xvfb(self) -> bool:
        """Start Xvfb (virtual X server)."""
        try:
            # Try to find an available display number
            # Check if ports are in use (simple check)
            available_display = None
            for i in range(10, 100):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex(('localhost', 6000 + i))
                    sock.close()
                    if result != 0:  # Port not in use
                        available_display = i
                        break
                except:
                    continue
            
            if available_display is None:
                available_display = 99  # Fallback
            
            self.display_num = available_display
            display = f":{available_display}"
            logger.info(f"Starting Xvfb on display {display}")
            
            # Start Xvfb
            cmd = [
                "Xvfb",
                display,
                "-screen", "0", "1920x1080x24",  # 1080p, 24-bit color
                "-ac",  # Disable access control
                "-nolisten", "tcp",  # Don't listen on TCP (local only)
                "-dpi", "96"  # Standard DPI
            ]
            
            logger.info("Executing: %s", " ".join(cmd))
            self.xvfb_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.xvfb_process.poll() is None:
                logger.info(f"✓ Xvfb started on display {display}")
                self.display = display
                return True
            else:
                logger.error("Xvfb failed to start")
                stdout, stderr = self.xvfb_process.communicate()
                if stderr:
                    logger.error("stderr: %s", stderr.decode())
                return False
                
        except Exception as e:
            logger.error("Failed to start Xvfb: %s", str(e))
            return False
    
    def start_scrcpy(self) -> bool:
        """Start scrcpy on virtual display."""
        try:
            display = f":{self.display_num}"
            logger.info(f"Starting scrcpy on virtual display {display}")
            
            # Set environment variables
            env = os.environ.copy()
            env["DISPLAY"] = display
            
            # Ensure PATH includes common adb locations and ~/.local/bin
            current_path = env.get("PATH", "")
            adb_paths = [
                os.path.expanduser("~/.local/bin"),
                "/shared/ken/.android/platform-tools",
                current_path
            ]
            env["PATH"] = ":".join(filter(None, adb_paths))
            
            cmd = [
                "scrcpy",
                "--no-audio",
                "--turn-screen-off",
                "--disable-screensaver",
                "--window-x", "0",
                "--window-y", "0",
                "--window-width", "1920",
                "--window-height", "1080"
            ]
            
            # Add device serial if specified
            if self.device_serial:
                cmd.extend(["--serial", self.device_serial])
            
            logger.info("Executing: DISPLAY=%s PATH=%s %s", display, env["PATH"][:100], " ".join(cmd))
            self.scrcpy_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            time.sleep(5)  # Give scrcpy more time to start and render
            
            if self.scrcpy_process.poll() is None:
                logger.info("✓ scrcpy started successfully")
                return True
            else:
                logger.error("scrcpy failed to start")
                stdout, stderr = self.scrcpy_process.communicate()
                if stdout:
                    logger.error("stdout: %s", stdout.decode()[:500])
                if stderr:
                    logger.error("stderr: %s", stderr.decode()[:500])
                return False
                
        except Exception as e:
            logger.error("Failed to start scrcpy: %s", str(e))
            return False
    
    def start_x11vnc(self) -> bool:
        """Start x11vnc to capture virtual display."""
        try:
            display = f":{self.display_num}"
            logger.info(f"Starting x11vnc on display {display}, VNC port {self.vnc_port}")
            
            # Wait a bit for display to be ready
            time.sleep(1)
            
            # Use user-specific log file to avoid permission conflicts in /tmp
            log_file = os.path.join(os.path.expanduser("~"), f".x11vnc_{self.vnc_port}.log")
            
            cmd = [
                "x11vnc",
                "-display", display,
                "-rfbport", str(self.vnc_port),
                "-forever",  # Keep running
                "-shared",  # Allow multiple connections
                "-noxdamage",  # Don't use X DAMAGE extension
                "-noxfixes",  # Don't use XFIXES extension
                "-noxinerama",  # Don't use Xinerama
                "-nopw",  # No password (local use)
                "-wait", "10",  # Wait for clients
                "-defer", "10",  # Defer updates
                "-bg",  # Run in background
                "-o", log_file  # Log file for debugging (user-specific)
            ]
            
            logger.info("Executing: %s", " ".join(cmd))
            self.x11vnc_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # When using -bg, x11vnc forks and parent exits quickly
            # So poll() will return quickly, but child process is running
            time.sleep(2)
            
            # Check if VNC port is listening (better check for background process)
            import socket
            port_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            port_check.settimeout(1)
            result = port_check.connect_ex(('localhost', self.vnc_port))
            port_check.close()
            
            if result == 0:
                logger.info(f"✓ x11vnc started on port {self.vnc_port} (port is listening)")
                return True
            else:
                # Port not listening yet, wait a bit more
                time.sleep(2)
                port_check2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                port_check2.settimeout(1)
                result2 = port_check2.connect_ex(('localhost', self.vnc_port))
                port_check2.close()
                
                if result2 == 0:
                    logger.info(f"✓ x11vnc started on port {self.vnc_port}")
                    return True
                
                logger.error("x11vnc failed to start (port not listening)")
                stdout, stderr = self.x11vnc_process.communicate(timeout=1)
                if stdout:
                    logger.error("stdout: %s", stdout.decode()[:500])
                if stderr:
                    logger.error("stderr: %s", stderr.decode()[:500])
                # Try to read log file
                log_file = os.path.join(os.path.expanduser("~"), f".x11vnc_{self.vnc_port}.log")
                if os.path.exists(log_file):
                    try:
                        with open(log_file, "r") as f:
                            log_content = f.read()[-1000:]  # Last 1000 chars
                            if log_content:
                                logger.error("x11vnc log (last part): %s", log_content)
                    except Exception as e:
                        logger.warning("Could not read log file: %s", str(e))
                return False
                
        except Exception as e:
            logger.error("Failed to start x11vnc: %s", str(e))
            return False
    
    def start_websockify(self) -> bool:
        """Start websockify to bridge VNC to WebSocket."""
        try:
            # Check for noVNC directory (optional)
            # First check in web_ui directory, then parent directory
            novnc_dir = Path(__file__).parent / "novnc"
            if not novnc_dir.exists():
                # Try parent directory (project root)
                novnc_dir = Path(__file__).parent.parent / "novnc"
            
            if not novnc_dir.exists():
                logger.warning("noVNC directory not found. Using websockify's default web interface.")
                logger.warning("For better UI, clone noVNC: git clone https://github.com/novnc/noVNC.git novnc")
                logger.warning("Access the VNC client via: http://localhost:{}/vnc.html (if websockify provides it)", self.web_port)
                web_dir = None
            else:
                web_dir = str(novnc_dir)
                logger.info(f"Using noVNC directory: {web_dir}")
            
            logger.info(f"Starting websockify on port {self.web_port} -> localhost:{self.vnc_port}")
            logger.info("Websockify will bind to 0.0.0.0 (all interfaces) for remote access")
            
            cmd = [
                "websockify",
                f"0.0.0.0:{self.web_port}",  # Bind to all interfaces (0.0.0.0) for remote access
                f"localhost:{self.vnc_port}",
            ]
            
            if web_dir:
                cmd.extend(["--web", web_dir])
            
            # For local use, disable SSL
            cmd.append("--cert")
            cmd.append("none")
            
            logger.info("Executing: %s", " ".join(cmd))
            self.websockify_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.websockify_process.poll() is None:
                logger.info("✓ websockify started successfully")
                return True
            else:
                logger.error("websockify failed to start")
                stdout, stderr = self.websockify_process.communicate()
                if stdout:
                    logger.error("stdout: %s", stdout.decode())
                if stderr:
                    logger.error("stderr: %s", stderr.decode())
                return False
                
        except Exception as e:
            logger.error("Failed to start websockify: %s", str(e))
            return False
    
    def get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    def print_access_info(self):
        """Print access information."""
        local_ip = self.get_local_ip()
        
        print("\n" + "="*70)
        print("🚀 SCRCPY v3.x WEB SERVER READY")
        print("="*70)
        print(f"\n🌐 Open in your web browser:")
        # Check if noVNC directory exists
        novnc_dir = Path(__file__).parent / "novnc"
        if not novnc_dir.exists():
            novnc_dir = Path(__file__).parent.parent / "novnc"
        
        if novnc_dir.exists():
            print(f"   Local:   http://localhost:{self.web_port}/vnc_lite.html")
            print(f"   Full UI: http://localhost:{self.web_port}/vnc.html")
            if local_ip != "localhost":
                print(f"   Network: http://{local_ip}:{self.web_port}/vnc_lite.html")
        else:
            print(f"   Local:   http://localhost:{self.web_port}/vnc_lite.html")
            print(f"   ⚠️  Note: Access /vnc_lite.html or /vnc.html directly (noVNC directory not found)")
            if local_ip != "localhost":
                print(f"   Network: http://{local_ip}:{self.web_port}/vnc_lite.html")
        print(f"\n📱 Method: scrcpy v3.x + Xvfb + x11vnc (Real-time streaming)")
        print(f"🖥️  Virtual Display: :{self.display_num}")
        print(f"🔌 VNC Port: {self.vnc_port}")
        print(f"🌍 Web Port: {self.web_port}")
        if self.device_serial:
            print(f"📱 Device: {self.device_serial}")
        print(f"\n💡 Usage:")
        print(f"   - Screen updates automatically (30-60 FPS)")
        print(f"   - Click and drag to interact with emulator")
        print(f"   - Type on your keyboard to input text")
        print(f"   - Smooth, responsive experience")
        print(f"   - Press Ctrl+C here to stop")
        print("\n🌍 Remote Access (from Mac):")
        print(f"   - IMPORTANT: Use /vnc_lite.html or /vnc.html (not root URL)")
        print(f"   - From your Mac, open: http://{local_ip}:{self.web_port}/vnc_lite.html")
        print(f"   - Or use full version: http://{local_ip}:{self.web_port}/vnc.html")
        print(f"   - ⚠️  Root URL (http://{local_ip}:{self.web_port}/) may show 405 error - use /vnc_lite.html instead")
        print(f"   - Ensure firewall allows port {self.web_port}")
        print(f"   - If using SSH tunnel: ssh -L {self.web_port}:localhost:{self.web_port} ligu@{local_ip}")
        print("\n✨ Performance: Real-time streaming with low latency")
        print("="*70 + "\n")
    
    def start(self) -> bool:
        """Start web access."""
        if not self.check_dependencies():
            return False
        
        if not self.check_emulator_connected():
            logger.warning("No emulator detected, but continuing anyway...")
            logger.info("Make sure emulator is running: adb devices")
        
        # Start components in order
        if not self.start_xvfb():
            return False
        
        if not self.start_scrcpy():
            logger.error("Failed to start scrcpy, cleaning up...")
            self.stop()
            return False
        
        if not self.start_x11vnc():
            logger.error("Failed to start x11vnc, cleaning up...")
            self.stop()
            return False
        
        if not self.start_websockify():
            logger.error("Failed to start websockify, cleaning up...")
            self.stop()
            return False
        
        self.print_access_info()
        return True
    
    def stop(self):
        """Stop all processes."""
        logger.info("Stopping services...")
        self.running = False
        
        # Stop processes in reverse order
        processes = [
            ("websockify", self.websockify_process),
            ("scrcpy", self.scrcpy_process),
            ("Xvfb", self.xvfb_process)
        ]
        
        for name, process in processes:
            if process and process.poll() is None:
                logger.info("Stopping %s...", name)
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    logger.warning("Error stopping %s: %s", name, str(e))
        
        # x11vnc runs with -bg, so we need to find and kill by port/name
        if self.x11vnc_process:
            logger.info("Stopping x11vnc...")
            try:
                # Try to terminate the process if it still exists
                if self.x11vnc_process.poll() is None:
                    self.x11vnc_process.terminate()
                    self.x11vnc_process.wait(timeout=2)
                # Also kill any x11vnc processes on the VNC port
                result = subprocess.run(
                    ["pkill", "-f", f"x11vnc.*:{self.display_num}"],
                    capture_output=True,
                    timeout=3
                )
            except Exception as e:
                logger.warning("Error stopping x11vnc: %s", str(e))
    
    def run(self):
        """Run until interrupted."""
        if not self.start():
            logger.error("Failed to start web access")
            sys.exit(1)
        
        def signal_handler(sig, frame):
            logger.info("Received interrupt signal")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                # Check if processes are still alive
                if self.websockify_process and self.websockify_process.poll() is not None:
                    logger.error("websockify process died")
                    break
                # x11vnc runs with -bg, so parent exits but child runs
                # Check VNC port instead of process status
                import socket
                port_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                port_check.settimeout(0.5)
                result = port_check.connect_ex(('localhost', self.vnc_port))
                port_check.close()
                if result != 0:
                    logger.error(f"x11vnc port {self.vnc_port} not listening")
                    break
                if self.scrcpy_process and self.scrcpy_process.poll() is not None:
                    logger.error("scrcpy process died")
                    break
                if self.xvfb_process and self.xvfb_process.poll() is not None:
                    logger.error("Xvfb process died")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Start scrcpy v3.x web access to Android emulator"
    )
    parser.add_argument(
        "--web-port",
        type=int,
        default=6080,
        help="Web server port (default: 6080)"
    )
    parser.add_argument(
        "--vnc-port",
        type=int,
        default=5901,
        help="VNC server port (default: 5901)"
    )
    parser.add_argument(
        "--device-serial",
        type=str,
        default=None,
        help="ADB device serial number to connect to (required if multiple devices are connected). Use 'adb devices' to list available devices."
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all connected devices and exit"
    )
    
    args = parser.parse_args()
    
    # List devices if requested
    if args.list_devices:
        access = ScrcpyWebAccess()
        devices = access.list_devices()
        if devices:
            print("\nConnected devices:")
            for i, device in enumerate(devices, 1):
                print(f"  {i}. {device}")
            print(f"\nUse --device-serial {devices[0]} to select a specific device")
        else:
            print("No devices connected. Use 'adb devices' to check.")
        sys.exit(0)
    
    access = ScrcpyWebAccess(
        web_port=args.web_port,
        vnc_port=args.vnc_port,
        device_serial=args.device_serial
    )
    
    access.run()


if __name__ == "__main__":
    main()
