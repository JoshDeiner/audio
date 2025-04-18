# Audio Transcription Tool

A Python-based tool for recording audio and transcribing it using the faster-whisper model.

## Features

- Record audio from microphone
- Transcribe audio using faster-whisper
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

Run the transcriber:

```bash
python transcriber.py
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
