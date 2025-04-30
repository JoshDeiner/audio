# Audio Application

A comprehensive audio processing application for recording, transcription, and synthesis.

## Features

- Audio recording with platform-specific optimizations
- Transcription using Whisper models
- Text-to-speech synthesis
- Asynchronous state machine for conversation workflows
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

## Using Make Commands

The project includes a Makefile with several useful commands:

```bash
# Show all available commands
make help

# Setup the environment
make setup

# Update dependencies
make update

# Update and rebuild the project
make update-all

# Run tests
make test
```

## Documentation

For more detailed documentation, see the `documentation` directory:

- [Detailed README](documentation/README.md)
- [State Machine Documentation](documentation/state_machine.md)
- [Dependency Injection Guide](documentation/README_DEPENDENCY_INJECTION.md)
- [Architecture Overview](documentation/arch.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.