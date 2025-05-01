# Testing the Audio Transcription Tool

This guide explains how to test the audio transcription tool using various methods.

## Setup

1. Make sure you have installed all the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gtts librosa  # For speech synthesis testing
   ```

2. Ensure your `.env` file is properly configured:
   ```
   AUDIO_INPUT_DIR=input
   AUDIO_OUTPUT_DIR=output
   WHISPER_MODEL=tiny
   WHISPER_COMPUTE_TYPE=float32
   WHISPER_DEVICE=auto
   ```

## Automated Tests

### Running All Tests

To run all tests:

```bash
python -m pytest
```

### Unit Tests

Run the unit tests to verify individual components:

```bash
python -m pytest tests/unit/
```

These tests verify:
- State machine functionality
- Plugin system
- Transcription service

### Integration Tests

Run the integration tests to verify component interactions:

```bash
python -m pytest tests/integration/
```

These tests verify:
- Audio pipeline integration
- Async state machine integration
- Transcription service integration
- Conversation flow integration

### State Machine Conversation Tests

Test the conversation state machine specifically:

```bash
python -m pytest tests/integration/test_conversation_state_machine.py -v
```

This test verifies:
- Machine initiates the conversation with audio output
- User's response is captured and processed
- Machine responds to the user's input
- Complete conversation loop occurs with correct state transitions

### Test Options

- `-v`: Verbose mode - shows detailed test progress
- `--capture=no`: Shows print output during test execution
- `-k "test_name"`: Run specific tests that match the given name

### Sample Test Output

```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-7.3.1, pluggy-1.5.0
rootdir: /home/jd01/audio
collected 2 items

tests/integration/test_conversation_state_machine.py::TestConversationStateMachine::test_conversation_loop_machine_initiates PASSED [ 50%]
tests/integration/test_conversation_state_machine.py::TestConversationStateMachine::test_conversation_loop_with_audio_service_error PASSED [100%]

============================== 2 passed in 2.14s ===============================
```

## Testing Options

### Option 1: Automated Test Script

Run the automated test script that creates dummy files and processes them:

```bash
./test_transcription.sh
```

This script will:
1. Create a sine wave WAV file
2. Create a speech WAV file (if gtts and librosa are installed)
3. Run the transcription on these files
4. Save the results to the output directory

### Option 2: Manual Testing

#### Step 1: Create Dummy WAV Files

Create a simple sine wave WAV file:
```bash
python create_dummy_wav.py --output input/sine_wave.wav --duration 3.0 --frequency 440.0
```

Create a speech WAV file:
```bash
python create_speech_wav.py --text "This is a test of the audio transcription system." --output input/test_speech.wav
```

#### Step 2: Run the Transcription

Process all WAV files in the input directory:
```bash
python file_transcriber.py
```

Or process specific files:
```bash
python file_transcriber.py input/test_speech.wav
```

### Option 3: Use Your Own WAV Files

1. Place your WAV files in the `input` directory
2. Run the transcription:
   ```bash
   python file_transcriber.py
   ```

## Expected Results

After running the transcription, check the `output` directory for text files containing the transcriptions. Each file will be named after the original WAV file with a timestamp.

For speech files, you should see the transcribed text. For sine wave files, the results may vary as they don't contain actual speech.

## Troubleshooting

- **Missing dependencies**: Make sure all required packages are installed
- **File not found errors**: Ensure the input directory exists and contains WAV files
- **Transcription errors**: Try using a different Whisper model by changing the `WHISPER_MODEL` in your `.env` file

## Next Steps

Once you've verified that the transcription works with dummy files, you can:

1. Integrate this functionality into your main application
2. Experiment with different Whisper models for better accuracy
3. Add support for more audio formats
4. Implement batch processing for multiple files
