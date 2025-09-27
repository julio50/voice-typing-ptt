#!/bin/bash
# Wrapper script to start voice typing tray with proper environment

# Change to the script directory
cd "$(dirname "$0")"

# Activate virtual environment and start the tray
source venv/bin/activate
exec python voice_tray_qt.py