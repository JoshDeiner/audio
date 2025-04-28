# Audio Application

A comprehensive audio processing application for recording, transcription, and synthesis.

## Features

- Audio recording with platform-specific optimizations
- Transcription using whisper models
- Text-to-speech synthesis
- Pluggable architecture for extensibility
- Dependency injection for improved testability and maintainability

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Recording and Transcribing Audio

```bash
# Record audio and transcribe
python -m audio audio-in --duration 5 --model tiny

# Transcribe an existing audio file
python -m audio audio-in --audio_path /path/to/audio.wav --model small
```

### Text-to-Speech

```bash
# Convert text to speech
python -m audio audio-out --data_source "Hello, world!"

# Convert text from a file to speech
python -m audio audio-out --data_source /path/to/text.txt
```

### Conversation Mode

```bash
# Start a conversation (record, transcribe, respond, and synthesize)
python -m audio conversation --turns 3
```

## Architecture

The application follows clean architecture principles with a focus on:

1. **Dependency Injection**: All components receive their dependencies instead of creating them
2. **Interface-Based Design**: Components depend on interfaces, not concrete implementations
3. **Plugin System**: Extensible through plugins for transcription, audio formats, and more
4. **Async Processing**: Uses asyncio for concurrent audio processing pipelines

### Key Components

- **Services**: Core functionality like file operations, transcription, recording
- **Plugins**: Extensibility points for transcription, formatting, output
- **Controllers**: Orchestrate service interactions for specific workflows
- **DI Container**: Manages component instantiation and dependencies

## Documentation

Detailed documentation is available in the `documentation` folder:

- [Dependency Injection](documentation/README_DEPENDENCY_INJECTION.md)
- [Plugin System](documentation/plugins.md)
- [Architecture](documentation/arch.md)

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit
pytest tests/integration
```

### Adding New Features

When adding new features:

1. Define interfaces in `services/interfaces`
2. Implement in `services/implementations`
3. Register with the DI container in `dependency_injection/bootstrap.py`

### Plugin Development

See the [Plugin System documentation](documentation/plugins.md) for details on creating plugins.

## License

This project is licensed under the MIT License - see the LICENSE file for details.