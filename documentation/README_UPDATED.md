# Audio Processing Application

This application processes audio from various sources, performing transcription, text-to-speech conversion, and other audio operations. It's containerized to run on all major platforms including Raspberry Pi (default), Linux, macOS, and Windows.

## Features

- Records audio from system microphone
- Transcribes audio using Whisper models
- Text-to-speech synthesis
- Extensible plugin architecture
- Cross-platform compatibility (Pi, Linux, macOS, Windows)
- Containerized for easy deployment
- Multiple audio backend support (ALSA, PulseAudio)
- Flexible input/output directory configuration
- Asynchronous processing support

## Requirements

- Docker and Docker Compose (for containerized usage)
- Python 3.9+ with pip (for local usage)
- Audio input device (microphone)

## Plugin Architecture

The application features a robust plugin architecture that allows extending functionality without modifying core code:

### Plugin Types

1. **Transcription Plugins**
   - Implement different speech-to-text engines
   - Default: Whisper model via faster-whisper
   - Extensible for other models or cloud APIs

2. **Audio Format Plugins**
   - Handle different audio file formats
   - Default: WAV format
   - Extensible for MP3, FLAC, and other formats

3. **Preprocessing Plugins**
   - Apply audio processing before transcription
   - Implement noise reduction, normalization, etc.
   - Create custom audio enhancement pipelines

4. **Output Plugins**
   - Handle transcription results
   - Default: Save to text files
   - Extensible for databases, APIs, messaging systems

### Creating Plugins

To create a custom plugin:

1. Inherit from the appropriate base class:
   - `TranscriptionPlugin` for transcription engines
   - `AudioFormatPlugin` for audio format handlers
   - `PreprocessingPlugin` for audio preprocessing
   - `OutputPlugin` for output handling

2. Implement required methods:
   - Plugin identification methods:
     ```python
     @property
     def plugin_id(self) -> str:
         return "my_plugin_id"

     @property
     def plugin_name(self) -> str:
         return "My Plugin Name"

     @property
     def plugin_version(self) -> str:
         return "1.0.0"
     ```
   - Functionality-specific methods
   - Lifecycle methods (initialize/cleanup)

3. Place in one of these locations:
   - Built-in plugins directory (`plugins/builtin/`)
   - User plugins directory (`~/.audio/plugins`)
   - Custom directory specified in configuration

### Using Plugins

Plugins can be specified in configuration:

```python
config = {
    "transcription_plugin": "whisper_transcription",
    "pre_processing_plugins": ["noise_reduction", "normalize"],
    "output_plugins": ["file_output", "database_output"]
}
controller = AudioPipelineController(config)
```

## Running the Application

### Command-line Interface

The application uses a subcommand-based CLI with three main commands:

#### Audio-In (Transcription)

Record or process audio files and transcribe them:

```bash
# Record from microphone and transcribe
python -m audio audio-in --record --duration 5

# Transcribe a specific audio file
python -m audio audio-in --file path/to/audio.wav

# Transcribe with a specific model
python -m audio audio-in --file path/to/audio.wav --model medium

# Transcribe with a specific language
python -m audio audio-in --file path/to/audio.wav --language en

# Save the transcription to a file
python -m audio audio-in --file path/to/audio.wav --output path/to/output.txt
```

#### Audio-Out (Text-to-Speech)

Convert text to speech:

```bash
# Convert text directly to speech
python -m audio audio-out --data-source "This is a test of the text-to-speech system."

# Convert text from a file to speech
python -m audio audio-out --data-source path/to/input.txt

# Save the audio to a specific file
python -m audio audio-out --data-source "Hello world" --output path/to/output.wav

# Play the audio after generating it
python -m audio audio-out --data-source "Testing audio playback" --play
```

#### Conversation Mode

Start an interactive conversation loop:

```bash
# Start a conversation with default settings
python -m audio conversation

# Specify the number of turns
python -m audio conversation --turns 10

# Set the recording duration per turn
python -m audio conversation --duration 10
```

### Cross-Platform Script

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

### Using Seed Functionality

The tool includes integrated seed functionality to generate test audio files:

```bash
# Create a sine wave audio file
python -m audio --seed --seed-type sine --frequency 440.0 --duration 5.0

# Create a speech audio file
python -m audio --seed --seed-type speech --dummy-text "This is a test"

# Create multi-language samples
python -m audio --seed --seed-type multi-language

# Create a comprehensive test suite
python -m audio --seed --seed-type test-suite
```

## Environment Variables

- `PLATFORM`: Operating system platform (pi, linux, osx, win)
- `AUDIO_INPUT_DIR`: Directory for saving audio files
- `AUDIO_OUTPUT_DIR`: Directory for output files
- `AUDIO_DEVICE_PATH`: Path to audio device (for Linux)
- `AUDIO_DRIVER`: Audio backend to use (alsa, pulse)
- `PULSE_SERVER`: PulseAudio server address (for macOS/Windows)
- `WHISPER_MODEL`: Whisper model size (tiny, base, small, medium, large)
- `WHISPER_COMPUTE_TYPE`: Compute type for Whisper (int8, fp16, fp32)
- `WHISPER_DEVICE`: Device for Whisper (cpu, cuda)
- `PLUGIN_DIR`: Custom directory for plugins
- `DEFAULT_TRANSCRIPTION_PLUGIN`: Default transcription plugin to use
- `DEFAULT_AUDIO_FORMAT_PLUGIN`: Default audio format plugin to use
- `DEFAULT_OUTPUT_PLUGIN`: Default output plugin to use

## File Structure

### Main Application
- `audio/`: Main package directory
  - `__main__.py`: Entry point
  - `audio_pipeline_controller.py`: Core controller
  - `refactored_pipeline_controller.py`: Plugin-aware controller
  - `utilities/`: Utility modules
    - `argument_parser.py`: Command-line argument parsing

### Services
- `services/`: Service components
  - `audio_service.py`: Audio recording
  - `transcription_service.py`: Transcription
  - `text_to_speech_service.py`: Text-to-speech
  - `file_service.py`: File operations
  - `services_factory.py`: Service creation

### Plugin System
- `plugins/`: Plugin architecture
  - `plugin_base.py`: Core plugin interfaces
  - `transcription_plugin.py`: Transcription plugin interface
  - `audio_format_plugin.py`: Audio format plugin interface
  - `preprocessing_plugin.py`: Audio preprocessing interface
  - `output_plugin.py`: Output handler interface
  - `plugin_loader.py`: Dynamic plugin discovery
  - `plugin_manager.py`: Plugin lifecycle management
  - `builtin/`: Built-in plugins
    - `whisper_transcription.py`: Default Whisper plugin
    - `wav_audio_format.py`: WAV format support
    - `file_output.py`: File output handler

### Configuration
- `config/`: Configuration components
  - `configuration_manager.py`: Centralized config
  - `audio_config.env`: Environment config

### Development
- `tests/`: Test suite
- `documentation/`: Documentation
- `docker-compose.yml`: Container orchestration with platform profiles
- `Dockerfile`: Container definition

## Development

### Running Tests

```bash
# Run all tests
source venv/bin/activate  # Activate virtual environment
python -m pytest tests

# Run specific test categories
python -m pytest tests/unit
python -m pytest tests/integration

# Run with Makefile
make test
make test-unit
make test-integration
```

### Troubleshooting

If you encounter audio recording issues:

1. Try the local mode first: `./device_file_app.py`
2. For Docker issues: `./cross_platform_run.sh --debug`
3. Check microphone permissions and connections
4. On macOS/Windows: Install and start PulseAudio
5. Use the correct platform flag for your system
6. Try running in privileged mode: `docker-compose up --privileged`

### Common Plugin Issues

If you encounter issues with plugins:

1. Check that the plugin is registered correctly
2. Make sure `plugin_id` property is implemented correctly
3. Verify the plugin is in a directory that's searched by `PluginLoader`
4. Check the plugin is of the correct type
