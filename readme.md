# Audio Recording App

This application records audio from a microphone and saves it as a WAV file. It's containerized to run on all major platforms including Raspberry Pi (default), Linux, macOS, and Windows.

## Features

- Records audio from system microphone
- Colorful, interactive countdown display
- Cross-platform compatibility (Pi, Linux, macOS, Windows)
- Containerized for easy deployment
- Multiple audio backend support (ALSA, PulseAudio)
- Flexible input/output directory configuration

## Requirements

- Docker and Docker Compose (for containerized usage)
- Python 3.9+ with pip (for local usage)
- Audio input device (microphone)

## Running the Application

### New Cross-Platform Script (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd audio

# Run with platform auto-detection
./cross_platform_run.sh

# Run on macOS
./cross_platform_run.sh --mac

# Run on Windows
./cross_platform_run.sh --win

# Run on Pi or Linux
./cross_platform_run.sh --pi
./cross_platform_run.sh --linux

# Run locally without Docker
./cross_platform_run.sh --local

# Debug mode
./cross_platform_run.sh --debug
```

### Simple Device Selector (No Docker)

For the simplest approach without Docker:

```bash
# Run interactive device selector
./device_file_app.py
```

This script will show all available audio devices and let you choose which one to use.

### Original Run Script

```bash
# Run with default settings
./run.sh

# Set platform
./run.sh --platform=osx
./run.sh --platform=win
./run.sh --platform=linux

# Custom configuration
./run.sh --input-dir=/path/to/your/input
./run.sh --device=/dev/audio
./run.sh --build

# Run locally
./run.sh --local
```

## Environment Variables

- `PLATFORM`: Operating system platform (pi, linux, osx, win)
- `AUDIO_INPUT_DIR`: Directory for saving audio files
- `AUDIO_DEVICE_PATH`: Path to audio device (for Linux)
- `AUDIO_DRIVER`: Audio backend to use (alsa, pulse)
- `PULSE_SERVER`: PulseAudio server address (for macOS/Windows)

## Platform-Specific Docker Setup

The application can run in Docker on all platforms:

### Linux/Pi
- Uses ALSA device passthrough with `/dev/snd` mapping
- Falls back to PulseAudio socket if available
- Permission handling for audio device access

### macOS
- Uses PulseAudio over TCP to host
- Special host mapping for audio access
- Dedicated container profile with macOS-specific settings

### Windows
- Uses PulseAudio over TCP to host
- Host gateway configuration for audio access
- Dedicated container profile

## Troubleshooting

If you encounter audio recording issues:

1. Try the local mode first: `./device_file_app.py`
2. For Docker issues: `./cross_platform_run.sh --debug`
3. Check microphone permissions and connections
4. On macOS/Windows: Install and start PulseAudio
5. Use the correct platform flag for your system
6. Try running in privileged mode: `docker-compose up --privileged`

## File Structure

- `transcriber.py`: Main application script
- `audio-recording.py`: Alternative recording script
- `device_file_app.py`: Simple device selection app (no Docker)
- `platform_audio.sh`: Platform-specific audio configuration
- `cross_platform_run.sh`: Enhanced cross-platform launcher
- `run.sh`: Original helper script
- `Dockerfile`: Container definition
- `docker-compose.yml`: Container orchestration with platform profiles

## Development

To modify sample rate or recording duration, edit the relevant variables in `transcriber.py`.
