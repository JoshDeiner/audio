FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PyAudio and multiple audio backends
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    portaudio19-dev \
    python3-dev \
    python3-pyaudio \
    alsa-utils \
    libasound2-dev \
    pulseaudio \
    pulseaudio-utils \
    libpulse-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install sounddevice scipy pulsectl  # Add all audio dependencies

# Copy application files
COPY . .

# Create input and output directories
RUN mkdir -p /app/input && chmod 777 /app/input
RUN mkdir -p /app/output && chmod 777 /app/output

# Configure ALSA
COPY asound.conf /etc/asound.conf

# Set environment variables
ENV AUDIO_INPUT_DIR=/app/input
ENV AUDIO_OUTPUT_DIR=/app/output
# Fallback to null device if hardware not available
ENV AUDIODEV=null

# Create entrypoint script for platform detection
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'echo "Starting audio app with driver: $AUDIO_DRIVER"' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Check if we are using PulseAudio' >> /app/entrypoint.sh && \
    echo 'if [ "$AUDIO_DRIVER" = "pulse" ]; then' >> /app/entrypoint.sh && \
    echo '    echo "Using PulseAudio driver"' >> /app/entrypoint.sh && \
    echo '    # Wait for PulseAudio socket to be available' >> /app/entrypoint.sh && \
    echo '    if [ -S /tmp/pulseaudio.socket ]; then' >> /app/entrypoint.sh && \
    echo '        echo "PulseAudio socket found"' >> /app/entrypoint.sh && \
    echo '    else' >> /app/entrypoint.sh && \
    echo '        echo "Warning: PulseAudio socket not found at /tmp/pulseaudio.socket"' >> /app/entrypoint.sh && \
    echo '    fi' >> /app/entrypoint.sh && \
    echo 'fi' >> /app/entrypoint.sh && \
    echo '' >> /app/entrypoint.sh && \
    echo '# Execute the command passed to the script' >> /app/entrypoint.sh && \
    echo 'exec "$@"' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "transcriber.py"]

