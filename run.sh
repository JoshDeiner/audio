#!/bin/bash
# Helper script to run the audio app in different environments

# Make script executable
chmod +x run.sh

# Set default values
PLATFORM=${PLATFORM:-pi}
AUDIO_INPUT_DIR=${AUDIO_INPUT_DIR:-./input}
AUDIO_DEVICE_PATH=${AUDIO_DEVICE_PATH:-/dev/snd}

# Display usage information
function show_help {
  echo "Usage: ./run.sh [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --help            Show this help message"
  echo "  --platform=PLAT   Set platform (pi, linux, osx, win) [default: pi]"
  echo "  --input-dir=DIR   Set audio input directory [default: ./input]"
  echo "  --device=PATH     Set audio device path [default: /dev/snd]"
  echo "  --local           Run the app locally (not in Docker)"
  echo "  --build           Force rebuild Docker image"
  echo ""
  echo "Examples:"
  echo "  ./run.sh                           # Run with Pi defaults"
  echo "  ./run.sh --platform=osx            # Run in macOS mode"
  echo "  ./run.sh --input-dir=/path/to/dir  # Use custom input directory"
  echo "  ./run.sh --local                   # Run locally outside Docker"
}

# Process command line arguments
RUN_LOCAL=false
FORCE_BUILD=false

for arg in "$@"; do
  case $arg in
    --help)
      show_help
      exit 0
      ;;
    --platform=*)
      PLATFORM="${arg#*=}"
      ;;
    --input-dir=*)
      AUDIO_INPUT_DIR="${arg#*=}"
      ;;
    --device=*)
      AUDIO_DEVICE_PATH="${arg#*=}"
      ;;
    --local)
      RUN_LOCAL=true
      ;;
    --build)
      FORCE_BUILD=true
      ;;
    *)
      echo "Unknown option: $arg"
      show_help
      exit 1
      ;;
  esac
done

# Ensure input directory exists
mkdir -p "$AUDIO_INPUT_DIR"

# Export variables for docker-compose
export PLATFORM
export AUDIO_INPUT_DIR
export AUDIO_DEVICE_PATH

echo "=== Audio Recording App ==="
echo "Platform: $PLATFORM"
echo "Input Directory: $AUDIO_INPUT_DIR"
echo "Audio Device: $AUDIO_DEVICE_PATH"

if [ "$RUN_LOCAL" = true ]; then
  echo "Running locally (not in Docker)..."
  
  # Check for Python and install dependencies if needed
  if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
  fi

  # Create virtual environment if it doesn't exist
  if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
  fi

  # Activate virtual environment
  source venv/bin/activate

  # Install dependencies
  echo "Installing dependencies..."
  pip install -r requirements.txt

  # Run the app
  echo "Running the app..."
  AUDIO_INPUT_DIR="$AUDIO_INPUT_DIR" PLATFORM="$PLATFORM" python3 transcriber.py
else
  echo "Running in Docker..."
  
  # Build if needed
  if [ "$FORCE_BUILD" = true ]; then
    echo "Forcing Docker image rebuild..."
    docker-compose build --no-cache
  fi

  # Handle audio group permissions (Linux/Pi)
  if [ -e "/dev/snd" ]; then
    # Get the audio group ID
    AUDIO_GID=$(getent group audio | cut -d: -f3 || echo "")
    if [ -n "$AUDIO_GID" ]; then
      echo "Setting audio group permissions..."
      # Run with proper audio group permissions
      docker-compose run --user "$(id -u):$AUDIO_GID" audio-app
    else
      # Regular run
      docker-compose up
    fi
  else
    # No audio device found, try with host networking
    echo "No audio device detected, using host network mode..."
    docker-compose up
  fi
fi