# Fix: Permission Error with /tmp/default.textproto

## Problem

```
PermissionError: [Errno 13] Permission denied: '/tmp/default.textproto'
```

File `/tmp/default.textproto` is owned by another user and not writable.

## Solution: Use Environment Variable

**Yes!** You can change the temp directory using the `TMPDIR` environment variable, but you **must set it before Python starts** (before `tempfile` module is imported).

## Why This Works

`android_world.utils.file_utils.get_local_tmp_directory()` calls `tempfile.gettempdir()`, which:
1. Checks the `TMPDIR` environment variable
2. **Caches the result on first call**
3. Never re-checks if environment changes later

So `TMPDIR` must be set **before Python imports `tempfile`**.

## Solution 1: Bash Wrapper Script (Recommended) ✅

I've created a wrapper script: **`run_minimal_task.sh`**

### Usage

```bash
# Instead of:
python3 minimal_task_runner.py --task=something

# Use:
./run_minimal_task.sh --task=something
```

The script sets `TMPDIR=.aw_tmp` before Python starts, so your temp files go to:
```
.aw_tmp/default.textproto  ✅ You have full access
```

### What the script does:

```bash
#!/bin/bash
# Set TMPDIR before Python imports tempfile module
export TMPDIR="$SCRIPT_DIR/.aw_tmp"

# Run Python
python3 minimal_task_runner.py "$@"
```

## Solution 2: Shell Export

Set it in your shell before running:

```bash
export TMPDIR="$PWD/.aw_tmp"
mkdir -p .aw_tmp
python3 minimal_task_runner.py --task=something
```

Or create a one-liner:
```bash
TMPDIR=.aw_tmp python3 minimal_task_runner.py --task=something
```

## Solution 3: .env File + wrapper

Create a `.env` file:
```bash
TMPDIR=.aw_tmp
ANDROID_HOME=/shared/ken/.android
ANDROID_SDK_ROOT=/shared/ken/.android
```

Then use `run_minimal_task.sh` which will load it.

## Why NOT sudo?

- ❌ Security risk
- ❌ Might break other users
- ❌ Wrong approach - fix the location, not permissions
- ✅ Correct: Use your own temp directory

## Verify It Works

After setting TMPDIR, verify:
```bash
python3 << 'EOF'
import os
os.environ["TMPDIR"] = ".aw_tmp"
import tempfile
print(tempfile.gettempdir())  # Should print .aw_tmp path
EOF
```

Or check the file location:
```bash
./run_minimal_task.sh --help  # Just to initialize
ls -la .aw_tmp/default.textproto  # Should exist and be yours
```

## Summary

**Problem**: Cannot write to `/tmp/default.textproto` owned by another user.

**Root Cause**: `tempfile.gettempdir()` caches result, TMPDIR must be set before first call.

**Solution**: Set `TMPDIR` environment variable **before Python starts**.

**Best Practice**: Use the `run_minimal_task.sh` wrapper script.

**Result**: Files go to `.aw_tmp/default.textproto` where you have full access.

