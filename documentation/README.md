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

### Asynchronous State Machine

```bash
# Run the asynchronous state machine with specific cycles (must be even)
python -m audio state-machine --cycles 4 --duration 5 --model tiny

# Run with default parameters (2 cycles)
python -m audio state-machine

# Odd numbers are automatically increased to the next even number
# This will actually run 4 cycles
python -m audio state-machine --cycles 3

# Use a specific transcription model
python -m audio state-machine --model small --cycles 2

# Specify language for more accurate transcription
python -m audio state-machine --language en
```

You can also use the provided make command:

```bash
# Run state machine with default settings
make state-machine

# Run with custom cycles and duration
make state-machine CYCLES=3 DURATION=5

# Run with a specific model
make state-machine MODEL=small
```

The state machine transitions through four states:
- **LISTENING**: Records audio and transcribes it
- **SPEAKING**: Synthesizes and plays response to the transcription
- **WAITING**: Optional pause between cycles
- **STOPPED**: Final state when all cycles are complete

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
- **State Machine**: Manages audio processing workflow states and transitions
- **DI Container**: Manages component instantiation and dependencies

## Documentation

Detailed documentation is available in the `documentation` folder:

- [Dependency Injection](documentation/README_DEPENDENCY_INJECTION.md)
- [Plugin System](documentation/plugins.md)
- [Architecture](documentation/arch.md)
- [State Machine](documentation/state_machine.md)

## Development

### Managing Dependencies

```bash
# Update dependencies in the virtual environment
make update

# Update dependencies and rebuild the project
make update-all
```

The project provides two commands for keeping dependencies up-to-date:

- `make update`: Updates all dependencies in requirements.txt to their latest versions
- `make update-all`: Updates dependencies and reinstalls the project in development mode (if setup.py exists)

### Running Tests

```bash
# Run all tests
make test
# or directly with pytest
pytest

# Run specific test categories
make test-unit     # Unit tests only
make test-integration  # Integration tests only
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
