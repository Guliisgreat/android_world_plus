import argparse
import shutil
from android_world.env import interface
from android_world.env import env_launcher
from android_world.utils import app_snapshot


def connect_env(console_port, grpc_port):
    adb_path = shutil.which("adb") or '~/Android/Sdk/platform-tools/adb'
    env: interface.AsyncEnv = env_launcher._get_env(
        console_port=console_port,
        adb_path=adb_path,
        grpc_port=grpc_port,
    )
    return env


def main():
    parser = argparse.ArgumentParser()

    # Global emulator parameters
    parser.add_argument("--console", type=int, default=5706,
                        help="Emulator console port (default: 5706)")
    parser.add_argument("--grpc", type=int, default=8554,
                        help="Emulator grpc port (default: 8554)")

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # save
    p_save = subparsers.add_parser("save")
    p_save.add_argument("--package", required=True,
                        help="App package name, e.g., com.walmart.android")

    # restore
    p_restore = subparsers.add_parser("restore")
    p_restore.add_argument("--package", required=True,
                           help="App package name, e.g., com.walmart.android")

    args = parser.parse_args()

    env = connect_env(args.console, args.grpc)
    print(f"[✓] Connected to emulator (console={args.console}, grpc={args.grpc})")

    if args.cmd == "save":
        print(f"[*] Saving snapshot for: {args.package}")
        app_snapshot.save_snapshot(args.package, env.controller)
        print("[✓] Snapshot saved.")

    elif args.cmd == "restore":
        print(f"[*] Restoring snapshot for: {args.package}")
        app_snapshot.restore_snapshot(args.package, env.controller)
        print("[✓] Snapshot restored.")


if __name__ == "__main__":
    main()