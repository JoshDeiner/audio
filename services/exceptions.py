"""Custom exceptions for audio transcription services."""


class AudioServiceError(Exception):
    """Base exception for all audio service errors."""

    pass


class AudioRecordingError(AudioServiceError):
    """Raised when audio recording fails."""

    pass


class TranscriptionError(AudioServiceError):
    """Raised when transcription fails."""

    pass


class FileOperationError(AudioServiceError):
    """Raised when file operations fail."""

    pass
