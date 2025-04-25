"""Unit tests for FileTranscriptionService."""
from typing import Any

import pytest

from services.file_transcription_service import FileTranscriptionService


@pytest.mark.unit
class TestFileTranscriptionUnit:
    """Unit tests for FileTranscriptionService."""

    def test_transcribe_file_called_correctly(self, mocker: Any) -> None:
        """Test that transcribe_file method is called with correct parameters."""
        service = FileTranscriptionService()
        file_path = "fake/path.wav"

        mock_transcribe = mocker.patch.object(
            FileTranscriptionService,
            "transcribe_file",
            return_value="mocked text",
        )

        result = service.transcribe_file(
            file_path, model_size="tiny", language="en"
        )

        mock_transcribe.assert_called_once_with(
            file_path, model_size="tiny", language="en"
        )
        assert result == "mocked text"

    def test_handles_missing_file_gracefully(self) -> None:
        """Test that service raises appropriate exception for missing files."""
        from services.exceptions import FileOperationError

        service = FileTranscriptionService()
        fake_path = "nonexistent.wav"

        with pytest.raises(FileOperationError):
            service.transcribe_file(fake_path)
