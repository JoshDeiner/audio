"""Unit tests for AsyncAudioStateMachine.

Tests the state transitions and functionality of the asynchronous state machine
that handles audio input and output cycles.
"""

import asyncio
import os
import logging
from unittest.mock import MagicMock, patch

import pytest

from audio.async_state_machine import AsyncAudioStateMachine, MachineState
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.transcription_service_interface import ITranscriptionService
from services.interfaces.configuration_manager_interface import IConfigurationManager

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
        mock_audio_service.record_audio.return_value = "/path/to/dummy/audio.wav"
        mock_transcription_service.transcribe_audio.return_value = "Hello, world."

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

    # Test: Full Audio-In Completion
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_listening_state_transition(self, mock_services, test_config):
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
        mock_services["transcription_service"].transcribe_audio.assert_called_once()

        # Assert captured text and state transition
        assert state_machine.text_result == "Hello, world."
        assert state_machine.current_state == MachineState.SPEAKING

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
        with patch(
            "services.text_to_speech_service.TextToSpeechService.synthesize",
            return_value=b"mock audio data",
        ), patch(
            "services.audio_playback_service.AudioPlaybackService.play", 
            return_value=None
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
        with patch(
            "services.text_to_speech_service.TextToSpeechService.synthesize",
            return_value=b"mock audio data",
        ), patch(
            "services.audio_playback_service.AudioPlaybackService.play", 
            return_value=None
        ):
            # Run the speaking state logic for the second cycle
            await state_machine._handle_speaking_state()

            # Verify cycle was completed and state transition to STOPPED
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED

    # Test: Waiting state transitions correctly
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_waiting_state_transition(self, mock_services, test_config):
        """Test the WAITING state transitions back to LISTENING."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Set initial state to WAITING
        state_machine.current_state = MachineState.WAITING

        # Run waiting state logic
        await state_machine._handle_waiting_state()

        # Verify state transition to LISTENING
        assert state_machine.current_state == MachineState.LISTENING

    # Test: Audio-In Error Handling
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_listening_state_error_handling(self, mock_services, test_config):
        """Test error handling in the LISTENING state."""
        # Instantiate the state machine
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
        )

        # Make the recording service raise an exception
        mock_services["audio_service"].record_audio.side_effect = Exception("Recording failed")

        # Run LISTENING state logic
        await state_machine._handle_listening_state()

        # Should still transition to SPEAKING with error message
        assert state_machine.current_state == MachineState.SPEAKING
        assert state_machine.text_result == "I couldn't understand what you said."

    # Test: Audio-Out Error Handling
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_speaking_state_error_handling(self, mock_services, test_config):
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
            side_effect=Exception("Synthesis failed")
        ):
            # Run the speaking state logic
            await state_machine._handle_speaking_state()

            # Should still increment cycle and transition appropriately
            assert state_machine.cycles_completed == 1
            assert state_machine.current_state == MachineState.WAITING

    # Test: Full State Machine Run
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_complete_run(self, mock_services, test_config):
        """Test the complete run of the state machine."""
        # Instantiate the state machine with 2 cycles
        state_machine = AsyncAudioStateMachine(
            config=test_config,
            audio_service=mock_services["audio_service"],
            transcription_service=mock_services["transcription_service"],
            config_manager=mock_services["config_manager"],
            cycles=2,
        )

        # Mock all the async calls
        with patch.object(
            state_machine, "_handle_listening_state"
        ) as mock_listening, patch.object(
            state_machine, "_handle_speaking_state"
        ) as mock_speaking, patch.object(
            state_machine, "_handle_waiting_state"
        ) as mock_waiting:
            
            # Configure state transitions for testing
            async def listening_side_effect():
                state_machine.text_result = "Hello, world."
                state_machine.current_state = MachineState.SPEAKING
            
            async def speaking_side_effect():
                state_machine.cycles_completed += 1
                if state_machine.cycles_completed >= state_machine.cycles_target:
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
            assert mock_speaking.call_count == 2   # Two speaking cycles
            assert mock_waiting.call_count == 1    # One waiting cycle
            assert state_machine.cycles_completed == 2
            assert state_machine.current_state == MachineState.STOPPED