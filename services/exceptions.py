"""Custom exceptions for audio transcription services."""

from typing import Any, Dict, Optional


class AudioServiceError(Exception):
    """Base exception for all audio service errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception with error details.

        Args:
            message: The error message
            error_code: Optional error code for categorization
            details: Optional additional error context
        """
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class SecurityError(AudioServiceError):
    """Raised when a security violation is detected."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = "SECURITY_VIOLATION",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize security error with details.

        Args:
            message: The error message
            error_code: Optional error code for categorization
            details: Optional additional error context
        """
        super().__init__(message, error_code, details)


class AudioRecordingError(AudioServiceError):
    """Raised when audio recording fails."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize recording error with details.

        Args:
            message: The error message
            error_code: Optional error code for categorization
            details: Optional additional error context
        """
        super().__init__(message, error_code, details)


class TranscriptionError(AudioServiceError):
    """Raised when transcription fails."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize transcription error with details.

        Args:
            message: The error message
            error_code: Optional error code for categorization
            details: Optional additional error context
        """
        super().__init__(message, error_code, details)


class FileOperationError(AudioServiceError):
    """Raised when file operations fail."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize file operation error with details.

        Args:
            message: The error message
            error_code: Optional error code for categorization
            details: Optional additional error context
        """
        super().__init__(message, error_code, details)
