# Tests for Audio Transcription Tool

This directory contains tests for the audio transcription tool.

## Running Tests

To run the tests, use:

```bash
# Run all tests
python -m pytest tests/

# Run only integration tests
python -m pytest tests/integration/

# Run only unit tests
python -m pytest tests/unit/

# Run with verbose output
python -m pytest -v tests/
```

## Test Files

### Unit Tests
- `unit/test_async_state_machine.py`: Tests for the async state machine component
- `unit/test_plugin_system.py`: Tests for the plugin system
- `unit/test_transcription_service.py`: Tests for the transcription service

### Integration Tests
- `integration/test_async_state_machine_integration.py`: Tests for the async state machine with services
- `integration/test_audio_pipeline_integration.py`: Tests for the audio pipeline
- `integration/test_audio_recording.py`: Tests for audio recording
- `integration/test_transcription_service.py`: Tests for transcription service integration
- `integration/test_conversation_state_machine.py`: Tests for conversation loop with machine-initiated flow

## Test Data

The tests use sample audio files from the `tests/assets` directory:
- `test_audio.wav`: Sample audio file for testing transcription and playback

## Conversation State Machine Testing

The conversation state machine tests (`test_conversation_state_machine.py`) verify a complete conversation loop where:

1. The machine initiates conversation with an audio output (SPEAKING state)
2. The user responds (LISTENING state)
3. The machine responds to the user's input, completing the loop

This test ensures that:
- State transitions occur in the correct sequence
- Audio services are called correctly
- The machine properly processes user input
- The conversation completes at least one full loop

Mock services are used to avoid actual audio recording/playback during tests.
