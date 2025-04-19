# Audio Test Data Generation Tools

This directory contains scripts for generating test audio data for the audio transcription system. These tools allow you to create various types of audio files without needing a microphone, which is useful for testing and development.

## Available Scripts

### 1. create_dummy_wav.py

Creates simple sine wave audio files.

```bash
python seed/create_dummy_wav.py --output input/sine_wave.wav --duration 3.0 --frequency 440.0
```

Options:
- `--output`, `-o`: Output file path (default: input/dummy_sine.wav)
- `--duration`, `-d`: Duration in seconds (default: 5.0)
- `--frequency`, `-f`: Frequency in Hz (default: 440.0)
- `--sample-rate`, `-sr`: Sample rate in Hz (default: 16000)

### 2. create_speech_wav.py

Creates speech audio files using Google Text-to-Speech (gTTS).

```bash
python seed/create_speech_wav.py --text "This is a test" --output input/speech.wav --language en
```

Options:
- `--text`, `-t`: Text to convert to speech (required)
- `--output`, `-o`: Output file path (default: input/speech.wav)
- `--language`, `-l`: Language code (default: en)

### 3. create_multi_language_samples.py

Creates speech samples in multiple languages.

```bash
python seed/create_multi_language_samples.py --output-dir input/language_samples
```

Options:
- `--output-dir`, `-o`: Output directory for language samples (default: input/language_samples)
- `--language`, `-l`: Specific language code to generate (default: all languages)
- `--text`, `-t`: Custom text to use (only with --language)

### 4. create_test_suite.py

Creates a comprehensive test suite with various types of audio samples.

```bash
python seed/create_test_suite.py --output-dir input/test_suite
```

Options:
- `--output-dir`, `-o`: Output directory for test samples (default: input/test_suite)

## Requirements

These scripts require the following Python packages:
- numpy
- soundfile
- gtts
- librosa

Install them with:

```bash
pip install numpy soundfile gtts librosa
```

## Usage with Make

You can also use the Make commands to run these scripts:

```bash
# Create a dummy sine wave file
make test-dummy

# Create a dummy speech file
make test-dummy-speech

# Create a dummy speech file with English language specified
make test-dummy-en
```

## Examples

### Create a 5-second sine wave at 440 Hz
```bash
python seed/create_dummy_wav.py --output input/sine_440.wav --duration 5.0 --frequency 440.0
```

### Create speech in Spanish
```bash
python seed/create_speech_wav.py --text "Hola, esto es una prueba" --output input/spanish.wav --language es
```

### Create a complete test suite
```bash
python seed/create_test_suite.py
```
