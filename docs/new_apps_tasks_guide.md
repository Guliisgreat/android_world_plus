# Running 6 Apps Evaluation Guide

This guide explains how to set up and run the 6 app evaluation tasks on the provided AVD.

## Overview

The 6 apps are divided into two categories:

| Category | Apps | Test Script |
|----------|------|-------------|
| **BMOCA** | Calculator, Snapseed, Wikipedia | `scripts/test_all_bmoca_tasks.py` |
| **AndroidLab** | Bluecoins, MAPS.ME, Pi Music | `scripts/test_androidlab_apps.py` |

## Prerequisites

### 1. Python Environment Setup

```bash
# Create a new Python 3.12 virtual environment
python3.12 -m venv aw_env
source aw_env/bin/activate

# Install dependencies
pip install -r requirements_aw_env_312.txt
```

### 2. OpenAI API Key

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Android SDK

Ensure Android SDK is installed and `adb` is in your PATH:
```bash
export ANDROID_HOME=~/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
```

---

## Loading the AVD

### Important: Do NOT modify the AVD or app snapshots!

The AVD comes with pre-configured app snapshots that are required for task evaluation.

### AVD Details

| Property | Value |
|----------|-------|
| AVD Name | `AWAvd` |
| Snapshot Name | `apps_ready_dec2025` |

### Start the Emulator

```bash
# Set your ports (adjust if needed)
export CONSOLE_PORT=5554
export GRPC_PORT=8554

# Start the emulator with the provided AVD and snapshot (READ-ONLY mode)
emulator -avd AWAvd \
  -no-window \
  -no-audio \
  -skip-adb-auth \
  -no-boot-anim \
  -gpu auto \
  -grpc $GRPC_PORT \
  -port $CONSOLE_PORT \
  -snapshot apps_ready_dec2025 \
  -no-snapshot-save &

# Wait for the emulator to fully boot
adb -s emulator-$CONSOLE_PORT wait-for-device
```

**Key flags:**
- `-snapshot apps_ready_dec2025`: Loads the pre-configured snapshot with all 6 apps ready
- `-no-snapshot-save`: **IMPORTANT** - Prevents saving changes to the snapshot (keeps it clean)
- `-no-window`: Run headless (no GUI window)
- `-no-audio`: Disable audio
- `-grpc`: gRPC port for Android World communication
- `-port`: Console port (ADB will use this port)

### Verify Emulator is Ready

```bash
# Check if emulator is running
adb devices

# Should show something like:
# emulator-5554   device
```

---

## Running the Tasks

### Set Your Ports First

```bash
# Set these to match your emulator settings
export CONSOLE_PORT=5554
export GRPC_PORT=8554
```

### Option 1: Run All Tasks for a Single App

**BMOCA Apps (Calculator, Snapseed, Wikipedia):**
```bash
# Calculator (19 tasks)
python scripts/test_all_bmoca_tasks.py --app calculator --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT

# Snapseed (11 tasks)
python scripts/test_all_bmoca_tasks.py --app snapseed --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT

# Wikipedia (5 tasks)
python scripts/test_all_bmoca_tasks.py --app wikipedia --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT
```

**AndroidLab Apps (Bluecoins, MAPS.ME, Pi Music):**
```bash
# Bluecoins (16 tasks)
python scripts/test_androidlab_apps.py --app bluecoins --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT

# MAPS.ME (15 tasks)
python scripts/test_androidlab_apps.py --app maps.me --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT

# Pi Music (12 tasks)
python scripts/test_androidlab_apps.py --app pimusic --run_all --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT
```

### Option 2: Run a Single Task

**BMOCA Apps:**
```bash
python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorOpen --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT
```

**AndroidLab Apps:**
```bash
python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsQuerySpendingOnDate --console_port $CONSOLE_PORT --grpc_port $GRPC_PORT
```

### Option 3: Run All 6 Apps Sequentially

```bash
# Pass your ports as arguments
./scripts/run_remaining_apps.sh $CONSOLE_PORT $GRPC_PORT
```

---

## Task Summary

| App | # Tasks | Complexity Range | Type |
|-----|---------|------------------|------|
| Calculator | 19 | 1.0 - 3.0 | Input/Compute |
| Snapseed | 11 | 1.0 - 3.0 | Photo Editing |
| Wikipedia | 5 | 1.0 - 4.0 | Navigation/Settings |
| Bluecoins | 16 | 1.5 - 3.5 | Finance Query/Entry |
| MAPS.ME | 15 | 2.0 - 3.5 | Navigation Query |
| Pi Music | 12 | 1.0 - 2.0 | Music Query/Control |

**Total: 78 tasks across 6 apps**

---

## Output and Logging

Each run produces:
1. **Console output**: Real-time task progress and results
2. **Summary**: Success rate and per-task scores at the end

To save output to a log file:
```bash
python scripts/test_all_bmoca_tasks.py --app calculator --run_all --console_port 5706 --grpc_port 8556 2>&1 | tee calculator_results.log
```

---

## Troubleshooting

### Emulator not connecting
```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices
```

### "Could not get a11y tree" warnings
This is normal and the system will auto-retry. If it persists, restart the emulator.

### OpenAI API errors
- Check your API key is set correctly
- Verify you have sufficient API credits
- The M3A agent uses `gpt-4o` model

### App not loading correctly
The app snapshots are restored automatically before each task. If issues persist:
```bash
# Manually restore an app snapshot (replace ports with your values)
python app_content_lg.py --console $CONSOLE_PORT --grpc $GRPC_PORT restore --package <app_name>
```

App names for restore: `calculator`, `snapseed`, `wikipedia`, `bluecoins`, `maps.me`, `pi music player`

---

## Notes

- **Do NOT save emulator state** after running tasks (use `-no-snapshot-save`)
- Each task automatically restores the app snapshot before execution
- Results are based on the M3A agent with GPT-4o
- Task validation is done via UI state checking, SQLite queries, or XML preferences depending on the app
- **Ports are configurable** - use any available ports for your setup

