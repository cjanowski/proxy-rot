#!/bin/bash
#
# PROXY ROT - Quick Run Script
# Automatically activates venv and runs the tool
#

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "✗ Virtual environment not found!"
    echo ""
    echo "Please run setup first:"
    echo "  ./setup.sh"
    echo ""
    exit 1
fi

# Activate virtual environment and run
source venv/bin/activate
python ip_rotator.py

# Deactivate is automatic when script exits

