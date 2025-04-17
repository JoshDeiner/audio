#!/bin/bash
# Cross-platform audio for Docker
# This script detects the platform and sets up the appropriate audio configuration

PLATFORM=$(uname -s)
echo "Detected platform: $PLATFORM"

# Get the root directory of the project
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
# Create config directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/config"

case "$PLATFORM" in
  Linux)
    echo "Setting up Linux audio configuration..."
    
    # Check if PulseAudio is installed
    if command -v pulseaudio &> /dev/null; then
      echo "PulseAudio found, using PulseAudio configuration"
      
      # Create PulseAudio client configuration
      cat > "$PROJECT_ROOT/config/pulse-client.conf" <<EOF
default-server = unix:/tmp/pulseaudio.socket
# Prevent a server running in the container
autospawn = no
daemon-binary = /bin/true
# Prevent the use of shared memory
enable-shm = false
EOF
      
      # Create PulseAudio socket if it doesn't exist
      if [ ! -e /tmp/pulseaudio.socket ]; then
        echo "Creating PulseAudio socket..."
        # Get PulseAudio running user
        PULSE_USER=$(ps aux | grep pulseaudio | grep -v grep | head -n 1 | awk '{print $1}')
        
        if [ -n "$PULSE_USER" ]; then
          echo "PulseAudio is running as user: $PULSE_USER"
          if [ "$PULSE_USER" = "$(whoami)" ]; then
            # Try to create socket
            pactl load-module module-native-protocol-unix socket=/tmp/pulseaudio.socket || true
          else
            echo "PulseAudio is running as different user, will use system socket"
          fi
        else
          echo "PulseAudio not running, will use ALSA"
          export AUDIO_DRIVER=alsa
        fi
      fi
      
      # Set environment variables for Docker
      export PULSE_SERVER=unix:/tmp/pulseaudio.socket
      export PULSE_COOKIE=/tmp/pulseaudio.cookie
      export AUDIO_DRIVER=pulse
      
      # Set up Docker run command
      DOCKER_AUDIO_ARGS="-v /tmp/pulseaudio.socket:/tmp/pulseaudio.socket -v $PROJECT_ROOT/config/pulse-client.conf:/etc/pulse/client.conf -e PULSE_SERVER=unix:/tmp/pulseaudio.socket"
      
    else
      echo "PulseAudio not found, falling back to ALSA"
      
      # Check if ALSA device exists
      if [ -e /dev/snd ]; then
        echo "ALSA device found"
        DOCKER_AUDIO_ARGS="--device /dev/snd:/dev/snd --group-add $(getent group audio | cut -d: -f3)"
        export AUDIO_DRIVER=alsa
      else
        echo "No audio devices found"
        DOCKER_AUDIO_ARGS=""
        export AUDIO_DRIVER=null
      fi
    fi
    ;;
    
  Darwin)
    echo "Setting up macOS audio configuration..."
    
    # Check if SoX/rec is installed for audio testing
    if ! command -v brew &> /dev/null; then
      echo "Homebrew not found. Please install Homebrew and then install SoX with: brew install sox"
      exit 1
    fi
    
    if ! command -v sox &> /dev/null; then
      echo "SoX not found. Installing with Homebrew..."
      brew install sox
    fi
    
    # macOS doesn't support direct device access in Docker
    # We need to use a socket-based approach with PulseAudio
    
    # Check if PulseAudio is installed via Homebrew
    if ! command -v pulseaudio &> /dev/null; then
      echo "PulseAudio not found. Installing with Homebrew..."
      brew install pulseaudio
    fi
    
    # Create PulseAudio configuration
    mkdir -p ~/.config/pulse
    cat > ~/.config/pulse/default.pa <<EOF
#!/usr/bin/pulseaudio -nF
load-module module-coreaudio-detect
load-module module-native-protocol-tcp auth-anonymous=1
load-module module-native-protocol-unix auth-anonymous=1
load-module module-always-sink
EOF
    
    # Start PulseAudio if not running
    if ! pulseaudio --check; then
      echo "Starting PulseAudio..."
      pulseaudio --start --exit-idle-time=-1
    fi
    
    # Get host IP for Docker to connect to
    HOST_IP=$(ifconfig en0 | grep inet | grep -v inet6 | awk '{print $2}')
    
    # Set up Docker run command
    DOCKER_AUDIO_ARGS="-e PULSE_SERVER=tcp:$HOST_IP -e AUDIO_DRIVER=pulse"
    ;;
    
  MINGW*|MSYS*|CYGWIN*)
    echo "Setting up Windows audio configuration..."
    
    # Windows doesn't support direct device access in Docker
    # We'll use a network approach using PulseAudio for Windows
    
    # Check if PulseAudio is installed on Windows
    if ! command -v pulseaudio &> /dev/null; then
      echo "PulseAudio not found. Please install from https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/"
      exit 1
    fi
    
    # Start PulseAudio server if not running
    if ! tasklist | grep -q pulseaudio; then
      echo "Starting PulseAudio..."
      pulseaudio -D --exit-idle-time=-1
    fi
    
    # Get the host IP address
    HOST_IP=$(ipconfig | grep IPv4 | head -n 1 | awk '{print $NF}')
    
    # Set up Docker run command
    DOCKER_AUDIO_ARGS="-e PULSE_SERVER=tcp:$HOST_IP -e AUDIO_DRIVER=pulse"
    ;;
    
  *)
    echo "Unknown platform: $PLATFORM"
    DOCKER_AUDIO_ARGS=""
    export AUDIO_DRIVER=null
    ;;
esac

# Save the configuration
echo "DOCKER_AUDIO_ARGS=\"$DOCKER_AUDIO_ARGS\"" > "$PROJECT_ROOT/config/audio_config.env"
echo "AUDIO_DRIVER=$AUDIO_DRIVER" >> "$PROJECT_ROOT/config/audio_config.env"

echo "Audio configuration saved to config/audio_config.env"
echo "To use these settings with Docker, run:"
echo "  docker run \$DOCKER_AUDIO_ARGS your-image"