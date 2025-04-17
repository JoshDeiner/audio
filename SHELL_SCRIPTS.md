# Audio Service Shell Scripts

This document provides an overview of the various shell scripts in the audio service project and their purposes.

## Script Overview

| Script Name | Purpose | When to Use |
|-------------|---------|------------|
| `cross_platform_run.sh` | **Recommended** multi-platform launcher with auto-detection | For most users; automatically detects OS and configures audio |
| `run.sh` | Original run script with granular options | When you need specific customization options |
| `easy_record.sh` | Simple local execution with no Docker | For quick local testing with device selection UI |
| `simple_docker.sh` | Minimal Docker setup for direct ALSA access | For basic Docker usage on Linux |
| `platform_audio.sh` | Audio configuration setup for different platforms | Used by other scripts; sets up audio backends |
| `alternate_run.sh` | No-frills local Python execution | For direct local execution without Docker |

## Detailed Descriptions

### `cross_platform_run.sh`
**Purpose**: Multi-platform launcher with intelligent platform detection
- Automatically detects your OS (Linux, macOS, Windows, Raspberry Pi)
- Configures appropriate audio settings for your platform
- Supports both Docker and local execution modes
- Provides debug options for troubleshooting

**Usage**:
```bash
# Auto-detect platform
./scripts/cross_platform_run.sh

# Specific platforms
./scripts/cross_platform_run.sh --mac
./scripts/cross_platform_run.sh --win
./scripts/cross_platform_run.sh --pi
./scripts/cross_platform_run.sh --linux

# Run locally without Docker
./scripts/cross_platform_run.sh --local

# Show extra debug info
./scripts/cross_platform_run.sh --debug
```

### `run.sh`
**Purpose**: Original run script with granular configuration options
- Provides detailed command-line options for customization
- Handles audio group permissions for Linux systems
- Supports both local and Docker execution
- Enables forcing Docker image rebuilds

**Usage**:
```bash
# Default execution
./scripts/run.sh

# Set specific platform
./scripts/run.sh --platform=osx|win|linux|pi

# Custom directories and devices
./scripts/run.sh --input-dir=/path/to/input
./scripts/run.sh --device=/dev/audio

# Force Docker rebuild
./scripts/run.sh --build

# Run locally without Docker
./scripts/run.sh --local
```

### `easy_record.sh`
**Purpose**: Simple launcher for the interactive device selector
- Runs the application directly without Docker
- Sets up Python environment automatically
- Launches the device selection UI for choosing audio inputs
- Ideal for first-time users or testing different microphones

**Usage**:
```bash
./scripts/easy_record.sh
```

### `simple_docker.sh`
**Purpose**: Minimal Docker execution with direct ALSA access
- Builds and runs the Docker container with minimal configuration
- Provides direct device access to audio hardware
- Primarily designed for Linux/Raspberry Pi systems
- Uses ALSA audio backend by default

**Usage**:
```bash
./scripts/simple_docker.sh
```

### `platform_audio.sh`
**Purpose**: Platform-specific audio configuration setup
- Detects the current OS and configures audio appropriately
- Sets up PulseAudio sockets and configuration on Linux
- Configures network audio on macOS and Windows
- Creates configuration files used by other scripts
- Outputs Docker arguments for audio device access

**Usage**:
```bash
# Usually called by other scripts, but can be run directly
./scripts/platform_audio.sh
```

### `alternate_run.sh`
**Purpose**: Simplified direct Python execution
- Bypasses all Docker configuration
- Sets up a Python virtual environment
- Installs required dependencies
- Runs the transcriber.py script directly
- Designed for systems where Docker isn't available

**Usage**:
```bash
./scripts/alternate_run.sh
```

## When to Use Which Script

1. **First-time user**: Start with `cross_platform_run.sh`
2. **Need device selection UI**: Use `easy_record.sh`
3. **Need detailed customization**: Use `run.sh` with options
4. **Linux with ALSA access**: `simple_docker.sh` works well
5. **No Docker available**: Use `alternate_run.sh`
6. **Audio configuration issues**: Run `platform_audio.sh` directly to debug