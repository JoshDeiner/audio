"""Unit tests for transcription services."""
import os
import pytest
from pathlib import Path

from services.file_transcription_service import FileTranscriptionService


class TestTranscription:
    """Test class for transcription services."""

    def test_file_transcription(self):
        """Test transcribing a WAV file to text.

        Tests that transcription completes successfully and the output
        contains more than 5 characters.
        """
        # Arrange
        service = FileTranscriptionService()
        test_file = os.path.join("input", "dummy_speech.wav")

        # Ensure the test file exists
        assert os.path.exists(
            test_file
        ), f"Test file {test_file} does not exist"

        # Act
        transcription = service.transcribe_file(
            file_path=test_file,
            model_size="tiny",  # Use smallest model for faster tests
            language="en",  # Specify English to skip language detection
        )

        # Assert
        assert transcription is not None, "Transcription should not be None"
        assert (
            len(transcription) > 5
        ), "Transcription should have more than 5 characters"

        # Verify output file was created (checking most recent file in output dir)
        output_dir = os.environ.get("AUDIO_OUTPUT_DIR", "output")
        output_files = list(Path(output_dir).glob(f"dummy_speech_*.txt"))
        assert len(output_files) > 0, "No output file was created"

        # Verify the content of the most recent output file
        latest_file = max(output_files, key=os.path.getctime)
        with open(latest_file, "r") as f:
            file_content = f.read()

        assert (
            file_content == transcription
        ), "File content should match transcription result"
