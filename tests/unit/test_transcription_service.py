import pytest
from services.file_transcription_service import FileTranscriptionService


@pytest.mark.unit
class TestFileTranscriptionUnit:
    """Unit tests for FileTranscriptionService."""

    def test_transcribe_file_called_correctly(self, mocker):
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

    def test_handles_missing_file_gracefully(self):
        from services.exceptions import FileOperationError

        service = FileTranscriptionService()
        fake_path = "nonexistent.wav"

        with pytest.raises(FileOperationError):
            service.transcribe_file(fake_path)
