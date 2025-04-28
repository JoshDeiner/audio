"""Transcription service interface for audio transcription tool."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class ITranscriptionService(ABC):
    """Interface for transcribing audio."""

    @abstractmethod
    def transcribe_audio(
        self,
        audio_file_path: str,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio file.

        Args:
            audio_file_path: Path to the audio file to transcribe
            model_size: Model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
            FileOperationError: If file operations fail
        """
        pass
