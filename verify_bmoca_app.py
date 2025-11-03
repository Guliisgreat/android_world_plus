"""Quick smoke runner for BMOCA apps on the current emulator.

This script:
- Creates an AndroidWorld AsyncEnv attached to the current emulator
- Optionally installs BMOCA APKs (if not already installed)
- Runs app setup flows to complete onboarding

Usage:
    # Test a specific app
    python verify_bmoca_app.py --app walmart
    
    # Test all apps
    python verify_bmoca_app.py --app all
    
    # Test multiple specific apps
    python verify_bmoca_app.py --app walmart wikipedia
"""

import argparse
import os
import sys
import traceback
import shutil

# Ensure a writable temp directory before importing android_world.
_AW_TMPDIR = os.path.join(os.path.dirname(__file__), ".aw_tmp")
os.makedirs(_AW_TMPDIR, exist_ok=True)

# Set up environment variables (matching run_minimal_task.sh)
os.environ['TMPDIR'] = _AW_TMPDIR
os.environ['ANDROID_HOME'] = os.environ.get('ANDROID_HOME', '/shared/ken/.android')
os.environ['ANDROID_SDK_ROOT'] = os.environ.get('ANDROID_SDK_ROOT', '/shared/ken/.android')
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = 'none'

from android_world.env import interface
from android_world.env import env_launcher
from android_world.env import adb_utils
from android_world.env.setup_device import setup as setup_module
from android_world.env.setup_device.bmoca_apps import (
    WalmartApp,
    WikipediaApp,
    InstagramApp,
)
from android_env.proto import adb_pb2


# Map app names to their AppSetup classes
APP_CLASSES = {
    'walmart': WalmartApp,
    'wikipedia': WikipediaApp,
    'instagram': InstagramApp,
}

# Map app names to their package names
APP_PACKAGES = {
    'walmart': 'com.walmart.android',
    'wikipedia': 'org.wikipedia',
    'instagram': 'com.instagram.android',
}


def uninstall_apps(app_names: list[str], env: interface.AsyncEnv) -> None:
    """Uninstall specified apps before running setup.
    
    Args:
        app_names: List of app names to uninstall
        env: The Android environment interface
    """
    print(f"\n{'='*80}")
    print("[verify_bmoca_app] Uninstalling apps before setup...")
    print(f"{'='*80}")
    
    for app_name in app_names:
        if app_name not in APP_PACKAGES:
            print(f"[verify_bmoca_app] ⚠ Skipping {app_name} (package name not mapped)")
            continue
            
        package_name = APP_PACKAGES[app_name]
        print(f"[verify_bmoca_app] Uninstalling {app_name} (package: {package_name})...")
        try:
            result = adb_utils.issue_generic_request(
                ['shell', 'pm', 'uninstall', package_name],
                env.controller
            )
            output = result.generic.output.decode('utf-8').strip() if result.generic.output else ''
            
            # pm uninstall returns "Success" on success, or error message if failed
            if result.status == adb_pb2.AdbResponse.Status.OK and 'Success' in output:
                print(f"[verify_bmoca_app] ✓ {app_name} uninstalled successfully")
            elif 'not found' in output.lower() or 'not installed' in output.lower():
                print(f"[verify_bmoca_app] ⚠ {app_name} not installed (skipping)")
            else:
                print(f"[verify_bmoca_app] ⚠ {app_name} uninstall result: {output}")
        except Exception as e:
            print(f"[verify_bmoca_app] ⚠ Failed to uninstall {app_name}: {e}")


def verify_app(app_name: str, app_class, env: interface.AsyncEnv) -> bool:
    """Verify a single app by installing (if needed) and running setup.
    
    Args:
        app_name: Name of the app (e.g., 'walmart')
        app_class: The AppSetup class for this app
        env: The Android environment interface
        
    Returns:
        True if setup succeeded, False otherwise
    """
    print(f"\n{'='*80}")
    print(f"[verify_bmoca_app] Verifying {app_name}...")
    print(f"{'='*80}")
    
    try:
        # Attempt install if APK is configured and not installed.
        try:
            print(f"[verify_bmoca_app] Attempting {app_name} APK install if needed...")
            setup_module.maybe_install_app(app_class, env)
            print(f"[verify_bmoca_app] ✓ {app_name} installation completed")
        except Exception as install_err:
            # Not fatal for smoke run if the app is already present or install infra differs.
            print(f"[verify_bmoca_app] ⚠ {app_name} APK install step skipped/failed: {install_err}")
        
        # Run the app setup flow
        print(f"[verify_bmoca_app] Running {app_class.__name__}.setup()...")
        app_class.setup(env)
        print(f"[verify_bmoca_app] ✓ {app_class.__name__}.setup() completed successfully")
        return True
        
    except Exception as e:
        print(f"[verify_bmoca_app] ✗ {app_class.__name__}.setup() failed with an exception:")
        traceback.print_exc(file=sys.stdout)
        return False


def main() -> int:
    """Runs smoke setup for BMOCA apps on the current emulator."""
    parser = argparse.ArgumentParser(
        description='Verify BMOCA app setup flows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a specific app
  python verify_bmoca_app.py --app walmart
  
  # Test all apps
  python verify_bmoca_app.py --app all
  
  # Test multiple apps
  python verify_bmoca_app.py --app walmart wikipedia
        """
    )
    parser.add_argument(
        '--app',
        nargs='+',
        default=['walmart', 'wikipedia'],
        choices=['walmart', 'wikipedia', 'instagram', 'all'],
        help='App(s) to verify. Use "all" to test all apps. (default: walmart)'
    )
    parser.add_argument(
        '--console-port',
        type=int,
        default=5554,
        help='Console port of the emulator (default: 5554)'
    )
    parser.add_argument(
        '--grpc-port',
        type=int,
        default=8554,
        help='gRPC port of the emulator (default: 8554)'
    )
    
    args = parser.parse_args()
    
    # Determine which apps to test
    if 'all' in args.app:
        apps_to_test = list(APP_CLASSES.keys())
    else:
        apps_to_test = args.app
    
    # Validate app names
    invalid_apps = [app for app in apps_to_test if app not in APP_CLASSES]
    if invalid_apps:
        print(f"[verify_bmoca_app] ✗ Invalid app names: {invalid_apps}")
        print(f"[verify_bmoca_app] Available apps: {list(APP_CLASSES.keys())}")
        return 1
    
    print(f"[verify_bmoca_app] Creating environment (using current emulator on port {args.console_port})...")
    adb_path = shutil.which("adb") or '~/Android/Sdk/platform-tools/adb'
    
    # Use _get_env directly to connect to existing emulator (no launch/grpc auth issues)
    env: interface.AsyncEnv = env_launcher._get_env(
        console_port=args.console_port,
        adb_path=adb_path,
        grpc_port=args.grpc_port,
    )
    
    try:
        # Uninstall walmart and wikipedia apps before running setup
        uninstall_apps(['walmart', 'wikipedia'], env)
        
        results = {}
        for app_name in apps_to_test:
            app_class = APP_CLASSES[app_name]
            success = verify_app(app_name, app_class, env)
            results[app_name] = success
        
        # Print summary
        print(f"\n{'='*80}")
        print("[verify_bmoca_app] Verification Summary")
        print(f"{'='*80}")
        for app_name, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"  {status}: {app_name}")
        
        all_passed = all(results.values())
        if all_passed:
            print(f"\n[verify_bmoca_app] ✓ All apps verified successfully!")
            return 0
        else:
            failed_apps = [app for app, success in results.items() if not success]
            print(f"\n[verify_bmoca_app] ✗ Some apps failed: {failed_apps}")
            return 1
            
    finally:
        env.close()


if __name__ == "__main__":
    sys.exit(main())
