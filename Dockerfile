# Stage 1: Base image with system dependencies
FROM python:3.10-slim AS audio-base

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

COPY requirements.txt .
COPY asound.conf /etc/asound.conf

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Layer 3: Directory structure (rarely changes)
RUN mkdir -p /app/input && chmod 755 /app/input
RUN mkdir -p /app/output && chmod 755 /app/output

# Layer 4: Environment variables (may change occasionally)
ENV AUDIO_INPUT_DIR=/app/input
ENV AUDIO_OUTPUT_DIR=/app/output
ENV AUDIODEV=null

# Stage 2: Final image with application code and dependencies
FROM audio-base AS audio-app

WORKDIR /app

# Layer 5: Download model before runtime
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', download_root='/root/.cache/huggingface/hub')" || echo "Model will be downloaded at runtime"

# Layer 7: Entrypoint configuration
ENTRYPOINT ["/app/cicd/entrypoint.sh"]

# Default to running the main.py file
CMD ["python", "-m", "audio"]
