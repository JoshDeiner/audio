# Stage 1: Base image with dependencies
FROM python:3.9-slim AS audio-base

WORKDIR /app

# Layer 1: System dependencies (rarely change)
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

# Layer 2: Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install sounddevice scipy pulsectl

# Layer 3: Configuration files (change infrequently)
COPY asound.conf /etc/asound.conf

# Layer 4: Directory structure (rarely changes)
RUN mkdir -p /app/input && chmod 755 /app/input
RUN mkdir -p /app/output && chmod 755 /app/output

# Layer 5: Environment variables (may change occasionally)
ENV AUDIO_INPUT_DIR=/app/input
ENV AUDIO_OUTPUT_DIR=/app/output
ENV AUDIODEV=null

# Stage 2: Final image with application code
FROM audio-base AS audio-app

WORKDIR /app

# Layer 6: Entrypoint script (rarely changes)
COPY cicd/entrypoint.sh /app/entrypoint.sh

# Layer 7: Application code (changes most frequently)
COPY . .

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["python", "transcriber.py"]
