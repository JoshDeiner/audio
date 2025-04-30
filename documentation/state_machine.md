# Asynchronous State Machine

The `AsyncAudioStateMachine` provides an asynchronous state-driven approach to audio processing workflows. It implements a cycle of listening (recording and transcribing), speaking (synthesizing and playing audio), and optional waiting phases.

## Balanced Cycles

The state machine requires an even number of cycles to ensure balanced listen/speak operation. This ensures that:

1. Every listening state is paired with a speaking state
2. The conversation always ends after the system has responded to the user
3. The state machine maintains a consistent pattern: listen → speak → listen → speak → ...

If an odd number of cycles is provided, the state machine automatically increases it to the next even number and notifies the user of this adjustment.

## States

The state machine implements four distinct states:

1. **LISTENING**: Records audio from microphone and transcribes it
2. **SPEAKING**: Generates a response and plays it via text-to-speech
3. **WAITING**: (Optional) Pauses briefly between cycles
4. **STOPPED**: Final state when all cycles are complete

## Usage

```bash
# Run the state machine with default settings (2 cycles)
python -m audio state-machine

# Run the state machine with 4 cycles, recording for 5 seconds per cycle
python -m audio state-machine --cycles 4 --duration 5

# If an odd number is provided, it will be automatically adjusted to the next even number
# This example will actually run 4 cycles
python -m audio state-machine --cycles 3 --duration 5

# Specify the transcription model
python -m audio state-machine --model small

# Set language for transcription
python -m audio state-machine --language en
```

You can also use the Makefile commands for convenience:

```bash
# Run state machine with default settings (2 cycles)
make state-machine

# Run with 4 cycles, recording for 3 seconds each
make state-machine CYCLES=4 DURATION=3

# Run with English language and tiny model
make state-machine LANGUAGE=en MODEL=tiny

# Update dependencies before running
make update && make state-machine
```

## State Transitions

The state machine follows this transition pattern:

```
LISTENING → SPEAKING → WAITING → LISTENING → ... → STOPPED
```

After completing the specified number of cycles, the state machine transitions to the STOPPED state and exits.

## Implementation

The state machine is implemented in `audio/async_state_machine.py` and follows these key principles:

1. **Asynchronous**: Uses `asyncio` for non-blocking operation
2. **State-Driven**: Explicit state management with transitions
3. **Error Tolerant**: Handles errors gracefully to maintain the workflow
4. **Service-Based**: Uses injectable services for audio operations

## Customization

To extend the state machine with custom behavior:

1. Subclass `AsyncAudioStateMachine`
2. Override the state handler methods (`_handle_listening_state`, etc.)
3. Implement custom logic while maintaining the state transition pattern

Example:

```python
class CustomStateMachine(AsyncAudioStateMachine):
    async def _handle_listening_state(self) -> None:
        # Custom listening implementation
        pass

    async def _handle_speaking_state(self) -> None:
        # Custom speaking implementation
        pass
```

## Integration with Other Components

The state machine works with other application components:

- Uses `IAudioRecordingService` for audio recording
- Uses `ITranscriptionService` for speech-to-text
- Uses `TextToSpeechService` for text-to-speech
- Uses `AudioPlaybackService` for audio playback

## Error Handling

The state machine includes error handling to ensure robust operation:

- Recording errors are caught and handled with fallback text
- Transcription errors are caught and handled with fallback responses
- Audio synthesis and playback errors are caught and logged
- The state machine continues to the next state even if errors occur
