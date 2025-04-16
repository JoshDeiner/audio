#!/bin/bash
# Cross-platform launcher for audio app

# Create config directory
mkdir -p config

# Set up default environment
if [ ! -f config/audio_config.env ]; then
  echo "AUDIO_DRIVER=alsa" > config/audio_config.env
  echo "DOCKER_AUDIO_ARGS=\"\"" >> config/audio_config.env
fi

# Detect OS
OS=$(uname -s)
echo "Detected OS: $OS"

# Process command line arguments
PLATFORM=""
RUN_LOCAL=false
DEBUG=false
SETUP_ONLY=false

for arg in "$@"; do
  case $arg in
    --mac)
      PLATFORM="mac"
      ;;
    --win)
      PLATFORM="win"
      ;;
    --pi)
      PLATFORM="pi"
      ;;
    --linux)
      PLATFORM="linux"
      ;;
    --local)
      RUN_LOCAL=true
      ;;
    --debug)
      DEBUG=true
      ;;
    --setup-only)
      SETUP_ONLY=true
      ;;
    --help)
      echo "Usage: ./cross_platform_run.sh [OPTIONS]"
      echo "Options:"
      echo "  --mac           Run in macOS mode"
      echo "  --win           Run in Windows mode"
      echo "  --pi            Run in Raspberry Pi mode (default for Pi hardware)"
      echo "  --linux         Run in Linux mode"
      echo "  --local         Run directly without Docker"
      echo "  --debug         Show additional debug information"
      echo "  --setup-only    Only configure audio, don't run app"
      echo "  --help          Show this help message"
      exit 0
      ;;
  esac
done

# Auto-detect platform if not specified
if [ -z "$PLATFORM" ]; then
  case $OS in
    Linux)
      # Check if running on Pi
      if [ -f "/proc/device-tree/model" ] && grep -q "Raspberry Pi" "/proc/device-tree/model"; then
        PLATFORM="pi"
      else
        PLATFORM="linux"
      fi
      ;;
    Darwin)
      PLATFORM="mac"
      ;;
    MINGW*|MSYS*|CYGWIN*)
      PLATFORM="win"
      ;;
    *)
      echo "Unknown platform, defaulting to Linux mode"
      PLATFORM="linux"
      ;;
  esac
fi

echo "Using platform: $PLATFORM"

# Set up platform-specific configuration
case $PLATFORM in
  mac)
    echo "Setting up macOS audio configuration..."
    
    # Check for Docker Desktop
    if ! command -v docker &> /dev/null; then
      echo "Docker not found. Please install Docker Desktop for Mac."
      exit 1
    fi
    
    if [ "$SETUP_ONLY" = false ]; then
      # Run macOS-specific Docker container
      if [ "$RUN_LOCAL" = false ]; then
        echo "Starting Docker container with macOS configuration..."
        docker-compose --profile mac up
      else
        echo "Running locally on macOS..."
        # Check for Python and dependencies
        if ! command -v python3 &> /dev/null; then
          echo "Python not found. Please install Python 3."
          exit 1
        fi
        
        # Set up virtual environment
        if [ ! -d "venv" ]; then
          echo "Creating virtual environment..."
          python3 -m venv venv
        fi
        source venv/bin/activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Run locally
        PLATFORM=mac AUDIO_DRIVER=pulse python3 device_file_app.py
      fi
    fi
    ;;
    
  win)
    echo "Setting up Windows audio configuration..."
    
    # Check for Docker Desktop
    if ! command -v docker &> /dev/null; then
      echo "Docker not found. Please install Docker Desktop for Windows."
      exit 1
    fi
    
    if [ "$SETUP_ONLY" = false ]; then
      # Run Windows-specific Docker container
      if [ "$RUN_LOCAL" = false ]; then
        echo "Starting Docker container with Windows configuration..."
        docker-compose --profile win up
      else
        echo "Running locally on Windows..."
        # Check for Python and dependencies
        if ! command -v python &> /dev/null; then
          echo "Python not found. Please install Python 3."
          exit 1
        fi
        
        # Set up virtual environment
        if [ ! -d "venv" ]; then
          echo "Creating virtual environment..."
          python -m venv venv
        fi
        source venv/Scripts/activate
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Run locally
        PLATFORM=win AUDIO_DRIVER=pulse python device_file_app.py
      fi
    fi
    ;;
    
  pi|linux)
    echo "Setting up Linux/Pi audio configuration..."
    
    # Run platform audio setup
    ./platform_audio.sh
    
    # Source configuration
    if [ -f config/audio_config.env ]; then
      source config/audio_config.env
    fi
    
    if [ "$DEBUG" = true ]; then
      echo "Audio configuration:"
      cat config/audio_config.env
    fi
    
    if [ "$SETUP_ONLY" = false ]; then
      # Run container or local app
      if [ "$RUN_LOCAL" = false ]; then
        echo "Starting Docker container with Linux configuration..."
        if [ -n "$DOCKER_AUDIO_ARGS" ]; then
          # Set additional environment variables
          export AUDIO_DEVICES='["/dev/snd:/dev/snd"]'
          export PRIVILEGED_MODE=true
          export NETWORK_MODE=host
        else 
          # Set empty array for devices
          export AUDIO_DEVICES='[]'
        fi
        
        docker-compose up
      else
        echo "Running locally on Linux/Pi..."
        # Run the alternate script
        ./alternate_run.sh
      fi
    fi
    ;;
    
  *)
    echo "Unknown platform: $PLATFORM"
    exit 1
    ;;
esac

echo "Done!"