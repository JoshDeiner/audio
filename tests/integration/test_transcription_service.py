import os
from pathlib import Path

import pytest

from services.file_transcription_service import FileTranscriptionService


@pytest.mark.integration
class TestFileTranscriptionIntegration:
    """Integration tests for FileTranscriptionService."""

    def test_transcribe_real_file_to_output(self, tmp_path):
        # Arrange
        service = FileTranscriptionService()
        # Using absolute path from project root
        input_file = (
            Path(__file__).parent.parent / "assets" / "dummy_speech.wav"
        )
        assert input_file.exists(), f"Missing test asset: {input_file}"

        output_dir = tmp_path / "output"
        os.environ["AUDIO_OUTPUT_DIR"] = str(output_dir)

        # Act
        transcription = service.transcribe_file(
            file_path=str(input_file), model_size="tiny", language="en"
        )

        # Assert
        assert transcription is not None
        assert len(transcription) > 5

        output_files = list(output_dir.glob("dummy_speech_*.txt"))
        assert output_files, "Expected output file not found"

        latest_file = max(output_files, key=os.path.getctime)
        assert latest_file.read_text() == transcription
