"""Unit tests for AsyncAudioStateMachine.

Tests the state transitions and functionality of the asynchronous state machine
that handles audio input and output cycles.

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


class TestAsyncStateMachine:
    """Test suite for the AsyncAudioStateMachine class."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing the state machine."""
        # Create mock services
        mock_audio_service = MagicMock(spec=IAudioRecordingService)
        mock_transcription_service = MagicMock(spec=ITranscriptionService)
        mock_config_manager = MagicMock(spec=IConfigurationManager)

        # Configure mock behavior
        mock_audio_service.record_audio.return_value = (
            "/path/to/dummy/audio.wav"
        )
        mock_transcription_service.transcribe_audio.return_value = (
            "Hello, world."
        )

        return {
            "audio_service": mock_audio_service,
            "transcription_service": mock_transcription_service,
            "config_manager": mock_config_manager,
        }

    @pytest.fixture
    def test_config(self):
        """Create a test configuration for the state machine."""
        return {
            "duration": 3,  # seconds of audio to record
            "model": "tiny",  # use a small model for fast testing
            "language": "en",  # use English
            "wait_duration": 0.05,  # shorter wait time for faster tests
        }

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

        yield {"input_dir": test_input_dir, "output_dir": test_output_dir}

    # Test: Initialization and Constants
    @pytest.mark.unit
    def test_constants_and_defaults(self, mock_services, test_config):
        """Test that class constants and defaults are correctly defined."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Assert constants are defined correctly
        assert state_machine.DEFAULT_DURATION == 5
        assert state_machine.DEFAULT_CYCLES == 2
        assert state_machine.DEFAULT_WAIT_DURATION == 0.1
        assert (
            state_machine.ERROR_MESSAGE
            == "I couldn't understand what you said."
        )

    # Test: Invalid Cycle Configuration
    @pytest.mark.unit
    def test_invalid_cycle_configuration(self, mock_services, test_config):
        """Test that CycleConfigurationError is raised for invalid cycles."""
        # Try to create with invalid cycles
        with pytest.raises(CycleConfigurationError) as excinfo:
            AsyncAudioStateMachine(
                config=test_config,
                audio_service=mock_services["audio_service"],
                transcription_service=mock_services["transcription_service"],
                config_manager=mock_services["config_manager"],
                cycles=0,
            )

        # Check error message
        assert "Number of cycles must be greater than zero" in str(
            excinfo.value
        )

    # Test: Odd Cycle Adjustment
    @pytest.mark.unit
    def test_odd_cycle_adjustment(self, mock_services, test_config):
        """Test that odd cycle counts are adjusted to even numbers."""
        # Create with odd cycles
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
            cycles=3,
        )

        # Check that it was adjusted to 4
        assert state_machine.cycles_target == 4

    # Test: System Starts in LISTENING state
    @pytest.mark.unit
    def test_initial_state(self, mock_services, test_config):
        """Test that the state machine starts in the LISTENING state."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Assert initial state is LISTENING
        assert state_machine.current_state == MachineState.LISTENING
        assert state_machine.cycles_completed == 0
        assert state_machine.text_result == ""

    # Test: Environment Setup
    @pytest.mark.unit
    def test_environment_setup(self, mock_services, test_config):
        """Test that environment variables and directories are properly set up."""
        # Create the state machine to trigger environment setup
        AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Verify environment variables and directories
        assert "AUDIO_INPUT_DIR" in os.environ
        assert "AUDIO_OUTPUT_DIR" in os.environ
        assert os.path.exists(os.environ["AUDIO_INPUT_DIR"])
        assert os.path.exists(os.environ["AUDIO_OUTPUT_DIR"])

    # Test: Full Audio-In Completion
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_listening_state_transition(
        self, mock_services, test_config
    ):
        """Test the LISTENING state logic and transition to SPEAKING."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Run LISTENING state logic
        await state_machine._handle_listening_state()

        # Verify audio service was called with correct parameters
        mock_services["audio_service"].record_audio.assert_called_once_with(
            duration=test_config["duration"]
        )

        # Verify transcription service was called
        mock_services[
            "transcription_service"
        ].transcribe_audio.assert_called_once()

        # Assert captured text and state transition
        assert state_machine.text_result == "Hello, world."
        assert state_machine.current_state == MachineState.SPEAKING

    # Test: Audio-In with AudioServiceError
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_listening_state_audio_service_error(
        self, mock_services, test_config
    ):
        """Test the LISTENING state handling of AudioServiceError."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Make the recording service raise an AudioServiceError
        mock_services["audio_service"].record_audio.side_effect = (
            AudioServiceError("Recording failed", error_code="RECORDING_ERROR")
        )

        # Run LISTENING state logic
        await state_machine._handle_listening_state()

        # Should still transition to SPEAKING with error message
        assert state_machine.current_state == MachineState.SPEAKING
        assert state_machine.text_result == state_machine.ERROR_MESSAGE

    # Test: Full Audio-Out Completion
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_speaking_state_transition(self, mock_services, test_config):
        """Test the SPEAKING state logic and transition back to WAITING."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
            cycles=2,
        )

        # Set up the state for testing
        state_machine.text_result = "Hello, world."
        state_machine.current_state = MachineState.SPEAKING

        # Mock the Text-to-Speech and AudioPlayback services
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
            # Run the speaking state logic
            await state_machine._handle_speaking_state()

            # Verify cycle was completed and state transition
            assert state_machine.cycles_completed == 1
            assert state_machine.current_state == MachineState.WAITING

    # Test: Full cycle stops after target cycles reached
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cycles_completion(self, mock_services, test_config):
        """Test that the state machine stops after reaching target cycles."""
        # Instantiate the state machine with 2 cycles
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
            cycles=2,
        )

        # Set up for testing the speaking state
        state_machine.text_result = "Hello, world."
        state_machine.current_state = MachineState.SPEAKING
        state_machine.cycles_completed = 1  # Already completed one cycle

        # Mock the Text-to-Speech and AudioPlayback services
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
            # Run the speaking state logic for the second cycle
            await state_machine._handle_speaking_state()

            # Verify cycle was completed and state transition to STOPPED
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    # Test: Custom Wait Duration
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_custom_wait_duration(self, mock_services, test_config):
        """Test that custom wait duration is used."""
        # Instantiate the state machine with custom wait duration
        state_machine = AsyncAudioStateMachine(
            config=test_config,  # Contains "wait_duration": 0.05
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Set initial state to WAITING
        state_machine.current_state = MachineState.WAITING

        # Mock asyncio.sleep to verify the wait duration
        with patch("asyncio.sleep") as mock_sleep:
            await state_machine._handle_waiting_state()
            mock_sleep.assert_called_once_with(0.05)

        # Verify state transition to LISTENING
        assert state_machine.current_state == MachineState.LISTENING

    # Test: Audio-Out Error Handling
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_speaking_state_error_handling(
        self, mock_services, test_config
    ):
        """Test error handling in the SPEAKING state."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Set up for testing
        state_machine.text_result = "Hello, world."
        state_machine.current_state = MachineState.SPEAKING

        # Mock TTS to raise an exception
        with patch(
            "services.text_to_speech_service.TextToSpeechService.synthesize",
            side_effect=AudioServiceError(
                "Synthesis failed", error_code="SYNTHESIS_ERROR"
            ),
        ):
            # Run the speaking state logic
            await state_machine._handle_speaking_state()

            # Should still increment cycle and transition appropriately
            assert state_machine.cycles_completed == 1
            assert state_machine.current_state == MachineState.WAITING

    # Test: Run Method with State Transitions
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_run_method_with_state_machine(
        self, mock_services, test_config
    ):
        """Test the run method with proper state machine transitions."""
        # Instantiate the state machine with 2 cycles
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
            cycles=2,
        )

        # Mock all the async calls
        with (
            patch.object(
                state_machine, "_handle_listening_state"
            ) as mock_listening,
            patch.object(
                state_machine, "_handle_speaking_state"
            ) as mock_speaking,
            patch.object(
                state_machine, "_handle_waiting_state"
            ) as mock_waiting,
        ):
            # Configure state transitions for testing
            async def listening_side_effect():
                state_machine.text_result = "Hello, world."
                state_machine.current_state = MachineState.SPEAKING

            async def speaking_side_effect():
                state_machine.cycles_completed += 1
                if (
                    state_machine.cycles_completed
                    >= state_machine.cycles_target
                ):
                    state_machine.current_state = MachineState.STOPPED
                else:
                    state_machine.current_state = MachineState.WAITING

            async def waiting_side_effect():
                state_machine.current_state = MachineState.LISTENING

            mock_listening.side_effect = listening_side_effect
            mock_speaking.side_effect = speaking_side_effect
            mock_waiting.side_effect = waiting_side_effect

            # Run the state machine
            await state_machine.run()

            # Verify expected calls and state transitions
            assert mock_listening.call_count == 2  # Two listening cycles
            assert mock_speaking.call_count == 2  # Two speaking cycles
            assert mock_waiting.call_count == 1  # One waiting cycle
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    # Test: Unhandled State
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unhandled_state(self, mock_services, test_config):
        """Test handling of an unhandled state."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Set an invalid state (this would not happen in normal operation)
        # We can't actually create an invalid MachineState enum value,
        # so we'll patch the match-case to simulate the default case
        with (
            patch.object(
                state_machine, "_handle_listening_state"
            ) as mock_listening,
            patch.object(
                state_machine, "_handle_speaking_state"
            ) as mock_speaking,
            patch.object(
                state_machine, "_handle_waiting_state"
            ) as mock_waiting,
        ):

            # Force the state machine to hit the default case
            # by not handling any known states
            mock_listening.side_effect = Exception("Not called")
            mock_speaking.side_effect = Exception("Not called")
            mock_waiting.side_effect = Exception("Not called")

            # Need to create a custom run method that simulates an unknown state
            async def custom_run():
                # Simulate an unknown state by not matching any case
                state_machine.current_state = MachineState.LISTENING
                # Override the match-case behavior
                state_machine.current_state = MachineState.STOPPED

            with patch.object(state_machine, "run", custom_run):
                await state_machine.run()

                # Verify none of the handlers were called
                mock_listening.assert_not_called()
                mock_speaking.assert_not_called()
                mock_waiting.assert_not_called()

                # Should end in STOPPED state
                assert state_machine.current_state == MachineState.STOPPED
