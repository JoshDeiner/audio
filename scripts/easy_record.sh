#!/bin/bash
# The simplest possible script to run the audio recorder

echo "=== Easy Audio Recorder ==="
echo "This script will run the audio recorder directly with no Docker"

# Create virtual environment if needed
if [ ! -d "venv" ]; then
  echo "Setting up virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make sure we have the input directory
mkdir -p input

# Run the device selector app directly
echo "Starting device selector..."
# Get the root directory of the project
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
python "$PROJECT_ROOT/device_file_app.py"