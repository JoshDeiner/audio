"""Integration test for a conversation state machine between machine and user.

This tests a state machine that simulates a conversation loop between machine
and user, with machine initiating the first message and capturing user response.

Author: Claude Code
Created: 2025-05-01
"""

import asyncio
import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from audio.async_state_machine import AsyncAudioStateMachine, MachineState
from library.bin.dependency_injection.app_services import AppServices
from services.exceptions import AudioServiceError
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)

# Setup test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestConversationStateMachine:
    """Integration tests for conversation loop using the AsyncAudioStateMachine."""

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
            "wait_duration": 0.1,  # Fast wait time for tests
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

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_conversation_loop_machine_initiates(
        self, setup_environment, test_config, mock_audio_file
    ):
        """Test a complete conversation loop with machine initiating first message.

        This test verifies the state machine:
        1. Starts with machine-generated message (audio_out)
        2. Captures user's response (audio_in)
        3. Completes a full loop by re-entering audio_out with user input
        """
        # Create services for testing
        services = AppServices()

        # Create mocks for audio recording and transcription
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure mock behavior
        mock_audio_service.record_audio.return_value = mock_audio_file
        mock_transcription_service.transcribe_audio.return_value = (
            "Hello, this is a test user response"
        )

        # Create a custom state machine that starts with SPEAKING state (audio_out)
        # instead of the default LISTENING state (audio_in)

        # Create state machine with just enough cycles for one complete loop
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=2,  # One full cycle: machine speaks -> user responds -> machine speaks again
        )

        # Modify the initial state to be SPEAKING (audio_out) instead of LISTENING (audio_in)
        state_machine.current_state = MachineState.SPEAKING

        # Create variables to track the conversation flow
        state_sequence = []
        machine_responses = []
        user_inputs = []

        # Store the original handler methods
        original_speaking = state_machine._handle_speaking_state
        original_listening = state_machine._handle_listening_state

        # Create wrapper for speaking state to capture machine outputs
        async def track_speaking_state():
            state_sequence.append("SPEAKING")
            # Capture the response text before calling the original method
            response = f"Machine speaking: {state_machine.text_result}"
            machine_responses.append(response)
            await original_speaking()

        # Create wrapper for listening state to capture user inputs
        async def track_listening_state():
            state_sequence.append("LISTENING")
            await original_listening()
            # Capture the text result after transcription
            user_input = f"User said: {state_machine.text_result}"
            user_inputs.append(user_input)

        # Replace the original methods with our tracking wrappers
        state_machine._handle_speaking_state = track_speaking_state
        state_machine._handle_listening_state = track_listening_state

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

            # Verify machine initiated first (SPEAKING state first)
            assert state_sequence[0] == "SPEAKING"

            # Verify expected state transitions for a full loop
            assert state_sequence == ["SPEAKING", "LISTENING", "SPEAKING"]

            # Verify both services were called appropriately
            assert mock_audio_service.record_audio.call_count == 1
            assert mock_transcription_service.transcribe_audio.call_count == 1

            # Verify the machine responded to user input in the second response
            assert len(machine_responses) == 2
            assert (
                "Hello, this is a test user response" in machine_responses[1]
            )

            # Verify user input was captured correctly
            assert len(user_inputs) == 1
            assert "Hello, this is a test user response" in user_inputs[0]

            # Assert final state
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_conversation_loop_with_audio_service_error(
        self, setup_environment, test_config
    ):
        """Test conversation loop resilience when audio service encounters an error."""
        # Create services for testing
        services = AppServices()

        # Create mocks with errors
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)

        # Configure mock behavior - audio service fails
        mock_audio_service.record_audio.side_effect = AudioServiceError(
            "Mock recording error", error_code="TEST_ERROR"
        )

        # Create state machine starting with SPEAKING state
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_audio_service,
            transcription_service=mock_transcription_service,
            config_manager=services.config_manager,
            cycles=2,
        )

        # Modify the initial state to be SPEAKING
        state_machine.current_state = MachineState.SPEAKING

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

            # Verify audio service was called
            assert mock_audio_service.record_audio.call_count == 1

            # Verify transcription was not called (due to audio error)
            assert mock_transcription_service.transcribe_audio.call_count == 0

            # Verify state machine completed despite error
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

            # Verify error message was stored
            assert state_machine.text_result == state_machine.ERROR_MESSAGE
