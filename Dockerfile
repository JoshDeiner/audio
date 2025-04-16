FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for PyAudio and ALSA
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    portaudio19-dev \
    python3-dev \
    python3-pyaudio \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variable for audio input directory
ENV AUDIO_INPUT_DIR=/app/input

# Run the transcriber
CMD ["python", "transcriber.py"]