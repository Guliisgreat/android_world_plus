#!/usr/bin/env python3
"""
ADB-based Web Access Server for Android Emulator

This server uses ADB screencap/input commands for web access.
Screenshot updates require manual refresh in the web UI.

Usage:
    python3 start_web_access_adb.py
    python3 start_web_access_adb.py --web-port 8080
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


class ADBWebAccess:
    def __init__(self, web_port: int = 6080):
        self.web_port = web_port
        self.adb_server_process = None
        self.running = True
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        if not shutil.which("adb"):
            logger.error("Missing required dependency: adb")
            logger.error("Please install Android Debug Bridge (adb)")
            return False
        return True
    
    def check_emulator_connected(self) -> bool:
        """Check if emulator is connected via ADB."""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line for line in lines if line.strip() and 'device' in line]
            
            if devices:
                logger.info(f"Found {len(devices)} device(s) connected")
                return True
            else:
                logger.warning("No devices connected. Make sure emulator is running.")
                logger.info("You can check with: adb devices")
                return False
        except Exception as e:
            logger.error("Error checking devices: %s", str(e))
            return False
    
    def start_adb_web_server(self) -> bool:
        """Start the ADB web server."""
        logger.info("Starting ADB-based web server...")
        
        try:
            # Start the ADB web server in a separate process
            script_path = Path(__file__).parent / "adb_web_server.py"
            
            # Check if the server script exists
            if not script_path.exists():
                logger.error(f"ADB web server script not found: {script_path}")
                logger.error("Please ensure adb_web_server.py exists in the project directory")
                return False
            
            # Start the server
            logger.info(f"Starting web server on port {self.web_port}")
            self.adb_server_process = subprocess.Popen(
                [sys.executable, str(script_path), 
                 "--port", str(self.web_port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(2)
            
            if self.adb_server_process.poll() is None:
                logger.info("✓ ADB web server started successfully")
                return True
            else:
                logger.error("ADB web server failed to start")
                stdout, stderr = self.adb_server_process.communicate()
                if stdout:
                    logger.error("stdout: %s", stdout.decode())
                if stderr:
                    logger.error("stderr: %s", stderr.decode())
                return False
                
        except Exception as e:
            logger.error("Failed to start ADB web server: %s", str(e))
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
        print("🚀 ADB WEB SERVER READY")
        print("="*70)
        print(f"\n🌐 Open in your web browser:")
        print(f"   Local:   http://localhost:{self.web_port}")
        if local_ip != "localhost":
            print(f"   Network: http://{local_ip}:{self.web_port}")
        print(f"\n📱 Method: ADB Screencap/Input")
        print(f"🌍 Web Port: {self.web_port}")
        print(f"\n💡 Usage:")
        print(f"   - Screenshot updates: ~10 FPS (automatic polling)")
        print(f"   - Click on screen to interact with emulator")
        print(f"   - Type text in the input field and click 'Send Text'")
        print(f"   - Use Back/Home buttons for navigation")
        print(f"   - Press Ctrl+C here to stop")
        print("\n⚠️  Note: This uses screenshot polling, so may have some lag.")
        print("   For better performance, use start_web_access_scrcpy.py")
        print("="*70 + "\n")
    
    def start(self) -> bool:
        """Start web access."""
        if not self.check_dependencies():
            return False
        
        if not self.check_emulator_connected():
            logger.warning("No emulator detected, but continuing anyway...")
            logger.info("Make sure emulator is running: adb devices")
        
        if not self.start_adb_web_server():
            return False
        
        self.print_access_info()
        return True
    
    def stop(self):
        """Stop all processes."""
        logger.info("Stopping services...")
        self.running = False
        
        if self.adb_server_process and self.adb_server_process.poll() is None:
            logger.info("Stopping ADB web server...")
            try:
                self.adb_server_process.terminate()
                self.adb_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.adb_server_process.kill()
            except Exception as e:
                logger.warning("Error stopping ADB web server: %s", str(e))
    
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
                # Check if process is still alive
                if self.adb_server_process and self.adb_server_process.poll() is not None:
                    logger.error("ADB web server process died")
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
        description="Start ADB-based web access to Android emulator"
    )
    parser.add_argument(
        "--web-port",
        type=int,
        default=6080,
        help="Web server port (default: 6080)"
    )
    
    args = parser.parse_args()
    
    access = ADBWebAccess(web_port=args.web_port)
    access.run()


if __name__ == "__main__":
    main()

