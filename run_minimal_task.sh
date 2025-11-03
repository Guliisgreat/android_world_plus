#!/bin/bash
# Wrapper script to set TMPDIR before Python starts

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AW_TMPDIR="$SCRIPT_DIR/.aw_tmp"

# Create the temp directory if it doesn't exist
mkdir -p "$AW_TMPDIR"

# Set TMPDIR environment variable
export TMPDIR="$AW_TMPDIR"

# Set other Android environment variables
export ANDROID_HOME="${ANDROID_HOME:-/shared/ken/.android}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-/shared/ken/.android}"

# Set GRPC options
export GRPC_VERBOSITY='ERROR'
export GRPC_TRACE='none'

echo "TMPDIR is set to: $TMPDIR"
echo "Running minimal_task_runner.py..."

# Activate conda environment if it exists
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)"
    conda activate aw_plus 2>/dev/null || echo "Warning: aw_plus conda environment not found"
fi

# OPENAI_API_KEY should be set as an environment variable before running this script
# For example: export OPENAI_API_KEY=your-key-here

# Run the Python script with all arguments passed through
python minimal_task_runner.py "$@"

