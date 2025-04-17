#!/bin/bash

echo "Starting audio app with driver: $AUDIO_DRIVER"

# Check if we are using PulseAudio
if [ "$AUDIO_DRIVER" = "pulse" ]; then
    echo "Using PulseAudio driver"
    # Wait for PulseAudio socket to be available
    if [ -S /tmp/pulseaudio.socket ]; then
        echo "PulseAudio socket found"
    else
        echo "Warning: PulseAudio socket not found at /tmp/pulseaudio.socket"
    fi
fi

# Execute the command passed to the script
exec "$@"
