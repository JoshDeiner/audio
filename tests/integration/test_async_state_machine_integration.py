"""Integration tests for AsyncAudioStateMachine.

Tests the state machine through complete cycles with minimal mocking,
focusing on the interaction between components.

Author: Claude Code
Created: 2025-04-30
"""

import asyncio
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from audio.async_state_machine import (
    AsyncAudioStateMachine,
    CycleConfigurationError,
    MachineState,
    StateMachineError,
)
from library.bin.dependency_injection.app_services import AppServices
from services.exceptions import AudioServiceError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)

# Setup test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAsyncStateMachineIntegration:
    """Integration tests for the AsyncAudioStateMachine class."""

    @pytest.fixture
    def setup_environment(self):
        """Set up the test environment with required directories and env vars."""
        # Create test directories
        test_input_dir = os.path.join(os.getcwd(), "input")
        test_output_dir = os.path.join(os.getcwd(), "output")

        os.makedirs(test_input_dir, exist_ok=True)
        os.makedirs(test_output_dir, exist_ok=True)

        # Set environment variables
        os.environ["AUDIO_INPUT_DIR"] = test_input_dir
        os.environ["AUDIO_OUTPUT_DIR"] = test_output_dir
        os.environ["WHISPER_MODEL"] = "tiny"  # Use tiny model for faster tests

        yield {"input_dir": test_input_dir, "output_dir": test_output_dir}

    @pytest.fixture
    def test_config(self):
        """Create a test configuration for the state machine."""
        return {
            "duration": 1,  # Keep duration short for tests
            "model": "tiny",  # Use a small model for fast testing
            "language": "en",  # Use English
        }

    @pytest.fixture
    def mock_audio_file(self):
        """Create a mock audio file for testing."""
        test_file = os.path.join(os.getcwd(), "input", "voice.wav")

        # If the test file doesn't exist yet, create a dummy one
        if not os.path.exists(test_file):
            dummy_wav_path = os.path.join(
                os.path.dirname(__file__), "..", "assets", "test_audio.wav"
            )
            if os.path.exists(dummy_wav_path):
                import shutil

                shutil.copy(dummy_wav_path, test_file)
            else:
                # Create an empty WAV file as fallback
                with open(test_file, "wb") as f:
                    f.write(
                        b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                    )

        return test_file

    # Test: Full Two-Cycle Run
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_two_cycle_run(
        self, setup_environment, test_config, mock_audio_file
    ):
        """Test a complete two-cycle run of the state machine."""
        # Create services for testing with DI
        services = AppServices()

        # Create mocks for audio recording and transcription
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure mock behavior
        mock_audio_service.record_audio.return_value = mock_audio_file
        mock_transcription_service.transcribe_audio.side_effect = [
            "First message",  # First cycle
            "Second message",  # Second cycle
        ]

        # Create state machine with 2 cycles (note: state machine enforces even cycles)
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=2,  # Use 2 since the state machine enforces even cycles
        )

        # Mock TTS and audio playback to prevent actual audio output
        with (
            patch(
                "services.text_to_speech_service.TextToSpeechService.synthesize",
                return_value=b"mock audio data",
            ),
            patch(
                "services.audio_playback_service.AudioPlaybackService.play",
                return_value=None,
            ),
        ):
            # Run the complete state machine
            await state_machine.run()

            # Verify expected calls (state machine enforces even cycles, so 2 is used)
            assert mock_audio_service.record_audio.call_count == 2
            assert mock_transcription_service.transcribe_audio.call_count == 2

            # Assert final state
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    # Test: Correct State Transition Sequence
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_state_transition_sequence(
        self, setup_environment, test_config, mock_audio_file
    ):
        """Test that states are visited in the correct sequence."""
        # Create services
        services = AppServices()

        # Create mocks
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure mock behavior
        mock_audio_service.record_audio.return_value = mock_audio_file
        mock_transcription_service.transcribe_audio.return_value = (
            "Test message"
        )

        # Create state machine with 2 cycles (note: state machine enforces even cycles)
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=2,  # Use 2 since the state machine enforces even cycles
        )

        # Track state transitions
        state_sequence = [state_machine.current_state]

        # Monkey patch the state machine methods to track state transitions
        original_listening = state_machine._handle_listening_state
        original_speaking = state_machine._handle_speaking_state
        original_waiting = state_machine._handle_waiting_state

        async def track_listening():
            await original_listening()
            state_sequence.append(state_machine.current_state)

        async def track_speaking():
            await original_speaking()
            state_sequence.append(state_machine.current_state)

        async def track_waiting():
            await original_waiting()
            state_sequence.append(state_machine.current_state)

        state_machine._handle_listening_state = track_listening
        state_machine._handle_speaking_state = track_speaking
        state_machine._handle_waiting_state = track_waiting

        # Mock TTS and audio playback
        with (
            patch(
                "services.text_to_speech_service.TextToSpeechService.synthesize",
                return_value=b"mock audio data",
            ),
            patch(
                "services.audio_playback_service.AudioPlaybackService.play",
                return_value=None,
            ),
        ):
            # Run the complete state machine
            await state_machine.run()

            # Expected sequence for 2 cycles:
            # LISTENING -> SPEAKING -> WAITING -> LISTENING -> SPEAKING -> STOPPED
            expected_sequence = [
                MachineState.LISTENING,  # Initial state
                MachineState.SPEAKING,  # After first listening
                MachineState.WAITING,  # After first speaking
                MachineState.LISTENING,  # After waiting
                MachineState.SPEAKING,  # After second listening
                MachineState.STOPPED,  # After second speaking (2 cycles completed)
            ]

            # Verify the state sequence
            assert state_sequence == expected_sequence

    # Test: Async Timing and Await Behavior
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_async_timing_behavior(self, setup_environment, test_config):
        """Test the asynchronous timing and await behavior of the state machine."""
        # Create services
        services = AppServices()

        # Create mocks with delays
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure mock behavior with DIRECT returns (no asyncio.run nesting)
        mock_audio_service.record_audio.return_value = "/tmp/mock_audio.wav"
        mock_transcription_service.transcribe_audio.return_value = (
            "Test transcription"
        )

        # Create state machine with 2 cycles (using even number to avoid warning)
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=1,
        )

        # Add delays directly in the state handlers to test async waiting properly
        original_listening = state_machine._handle_listening_state
        original_speaking = state_machine._handle_speaking_state

        async def delayed_listening():
            await asyncio.sleep(0.1)  # Add small delay
            await original_listening()

        async def delayed_speaking():
            await asyncio.sleep(0.1)  # Add small delay
            await original_speaking()

        state_machine._handle_listening_state = delayed_listening
        state_machine._handle_speaking_state = delayed_speaking

        # Mock TTS and playback services
        with (
            patch(
                "services.text_to_speech_service.TextToSpeechService.synthesize",
                return_value=b"mock audio data",
            ),
            patch(
                "services.audio_playback_service.AudioPlaybackService.play",
                return_value=None,
            ),
        ):
            # Measure execution time
            start_time = asyncio.get_event_loop().time()
            await state_machine.run()
            end_time = asyncio.get_event_loop().time()

            # Calculate execution time
            execution_time = end_time - start_time

            # The test verifies the async nature, not the exact timing
            # We expect at least 0.4s due to the added delays (0.1s per state x 4 state changes)
            logger.info(f"Execution time: {execution_time} seconds")
            assert execution_time >= 0.4

            # Instead of exact timing, verify number of calls to methods and final state
            assert mock_audio_service.record_audio.call_count == 2
            assert mock_transcription_service.transcribe_audio.call_count == 2
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    # Test: Failure on Second Audio-In
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_failure_on_second_audio_in(
        self, setup_environment, test_config, mock_audio_file
    ):
        """Test handling of failure on the second audio input cycle."""
        # Create services
        services = AppServices()

        # Create mocks
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure first call to succeed, second to fail
        mock_audio_service.record_audio.side_effect = [
            mock_audio_file,  # First call succeeds
            AudioServiceError(
                "Recording failed", error_code="RECORDING_ERROR"
            ),  # Second call fails with specific error
        ]

        mock_transcription_service.transcribe_audio.return_value = (
            "First message"
        )

        # Create state machine with 2 cycles (note: state machine enforces even cycles)
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=2,  # Use 2 since the state machine enforces even cycles
        )

        # Mock TTS and audio playback
        with (
            patch(
                "services.text_to_speech_service.TextToSpeechService.synthesize",
                return_value=b"mock audio data",
            ),
            patch(
                "services.audio_playback_service.AudioPlaybackService.play",
                return_value=None,
            ),
        ):
            # Run the state machine
            await state_machine.run()

            # Verify behavior - should make 2 calls, second one fails
            assert mock_audio_service.record_audio.call_count == 2

            # Should only call transcribe once (first successful call)
            assert mock_transcription_service.transcribe_audio.call_count == 1

            # Should still complete both cycles
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

            # Last text result should be the error message
            assert state_machine.text_result == state_machine.ERROR_MESSAGE
