"""Integration test for audio recording and transcription.

This module tests the complete audio recording and transcription pipeline
to ensure it works correctly with the improved confidence settings.
"""

import logging
import os
from unittest.mock import patch

import pytest

from audio.audio_pipeline_controller import AudioPipelineController
from library.bin.dependency_injection.app_services import AppServices
from services.exceptions import AudioRecordingError

# Setup test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAudioRecording:
    """Test suite for audio recording and transcription."""

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

        # No teardown needed, keep the directories

    @pytest.fixture
    def mock_audio_recording(self):
        """Mock the audio recording to return a predefined file."""
        # Path to a test audio file
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

    @pytest.mark.asyncio
    async def test_audio_pipeline_recording_with_mocked_audio(
        self, setup_environment, mock_audio_recording
    ):
        """Test audio pipeline with mocked audio recording."""
        # Initialize services
        services = AppServices()

        # Configure pipeline
        config = {
            "duration": 3,
            "model": "tiny",
            "language": "en",
            "save_transcript": True,
            "output_path": os.path.join(
                setup_environment["output_dir"], "test_transcript.txt"
            ),
        }

        # Create controller
        controller = AudioPipelineController.from_services(config, services)

        # Mock the _record_audio_async method to return our test file
        with patch.object(
            controller,
            "_record_audio_async",
            return_value=mock_audio_recording,
        ):
            # Run the pipeline
            try:
                transcription = await controller.handle_audio_in()

                # Basic validation
                assert transcription is not None
                assert isinstance(transcription, str)
                assert len(transcription) > 0

                logger.info(f"Transcription result: {transcription}")

                # Check that output file was created
                assert os.path.exists(config["output_path"])

            except AudioRecordingError as e:
                pytest.fail(f"Audio recording failed: {e}")
            except Exception as e:
                pytest.fail(f"Unexpected error: {e}")

    @pytest.mark.asyncio
    async def test_audio_pipeline_quality_validation(
        self, setup_environment, mock_audio_recording
    ):
        """Test audio quality validation in the pipeline."""
        # Initialize services
        services = AppServices()

        # Configure pipeline
        config = {"duration": 3, "model": "tiny", "language": "en"}

        # Create controller
        controller = AudioPipelineController.from_services(config, services)

        # Test that the audio service has the validation method
        assert hasattr(
            services.audio_service, "_validate_audio_quality"
        ), "Audio service missing quality validation method"

        # Try to validate an empty frame list (should fail)
        validation_result = services.audio_service._validate_audio_quality([])
        assert (
            validation_result is False
        ), "Empty frames should fail validation"

        # Mock recording to test the full pipeline with quality checks
        with patch.object(
            controller,
            "_record_audio_async",
            return_value=mock_audio_recording,
        ):
            # Run the pipeline
            try:
                transcription = await controller.handle_audio_in()
                assert (
                    transcription is not None
                ), "Transcription should not be None"

            except AudioRecordingError as e:
                pytest.fail(f"Audio recording failed: {e}")
            except Exception as e:
                pytest.fail(f"Unexpected error: {e}")
