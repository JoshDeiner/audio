#!/bin/bash
# Simplified alternate run script that bypasses Docker

# Create virtual environment if needed
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create input directory
mkdir -p input

# Set environment variables
export AUDIO_INPUT_DIR="./input"
export PLATFORM="pi"

# Run the app directly
echo "Running audio recorder..."
python transcriber.py