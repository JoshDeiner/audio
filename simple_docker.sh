#!/bin/bash
# Simplest possible Docker run script

echo "=== Simple Docker Audio ===";

# Create input directory
mkdir -p input

# Build the image
echo "Building Docker image..."
docker build -t audio-app .

# Run with direct device access
echo "Running Docker container with audio device access...";
docker run -it --rm \
  --device /dev/snd:/dev/snd \
  --group-add $(getent group audio | cut -d: -f3) \
  -v "$(pwd)/input:/app/input" \
  -e AUDIO_DRIVER=alsa \
  -e PLATFORM=pi \
  --privileged \
  audio-app