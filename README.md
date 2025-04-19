# Audio Transcription Tool

A Python-based tool for recording audio and transcribing it using the faster-whisper model.

## Features

- Record audio from microphone
- Transcribe audio using faster-whisper
- Transcribe existing audio files (for testing without a microphone)
- Create dummy audio files for testing
- Save transcriptions to text files
- Cross-platform support (Linux, macOS, Windows, Raspberry Pi)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd audio
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. For development, install development dependencies:
```bash
pip install -r requirements-dev.txt
```

5. Set up pre-commit hooks:
```bash
pre-commit install
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
AUDIO_INPUT_DIR=input
AUDIO_OUTPUT_DIR=output
WHISPER_MODEL=tiny
WHISPER_COMPUTE_TYPE=float32
WHISPER_DEVICE=auto
```

## Usage

### Using Make Commands

The easiest way to use the tool is with the provided Make commands:

```bash
# Run the app in recording mode
make local-run

# Create and transcribe a dummy sine wave file
make test-dummy

# Create and transcribe a dummy speech file
make test-dummy-speech

# Create and transcribe a dummy speech file with English language specified
make test-dummy-en

# Transcribe a specific file
make test-file FILE=input/audio.wav

# Transcribe a specific file with English language specified
make test-file-en FILE=input/audio.wav

# Transcribe all WAV files in a directory
make test-dir DIR=input
```

Run `make help` to see all available commands.

### Using Python Module Directly

#### Recording and Transcribing

Run the transcriber in recording mode (default):

```bash
python -m audio
```

Specify recording duration:

```bash
python -m audio --duration 10
```

#### Transcribing Existing Files

Transcribe a specific WAV file:

```bash
python -m audio --file input/audio.wav
```

Transcribe all WAV files in a directory:

```bash
python -m audio --dir input
```

#### Specifying Language (Skip Detection)

Specify the language to skip detection and speed up transcription:

```bash
python -m audio --file input/audio.wav --language en
```

#### Testing with Dummy Files

Create a dummy sine wave file and transcribe it:

```bash
python -m audio --create-dummy
```

Create a dummy speech file with specific text and transcribe it:

```bash
python -m audio --create-dummy --dummy-text "This is a test of the transcription system."
```

Just create a dummy file without transcribing:

```bash
python -m audio --create-dummy --dummy-text "Hello world" --file ""
```

#### Model Selection

Specify the Whisper model to use:

```bash
python -m audio --model medium
```

## Development

This project follows PEP 8 style guidelines and uses several tools to ensure code quality:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking
- pre-commit for automated checks

To run the formatters manually:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Run linting with flake8
flake8

# Run type checking with mypy
mypy transcriber.py
```

## License

[License information]
