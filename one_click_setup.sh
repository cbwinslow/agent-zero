#!/bin/bash
set -e

# Install dependencies
if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt
fi

# Prepare environment
python3 prepare.py "$@"

# Preload models or data
python3 preload.py "$@"

# Start the Agent Zero web UI
exec python3 run_ui.py "$@"
