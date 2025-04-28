"""File transcription service interface for audio transcription tool."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IFileTranscriptionService(ABC):
    """Interface for transcribing audio files without recording."""

    @abstractmethod
    def transcribe_file(
        self,
        file_path: str,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe a single audio file.

        Args:
            file_path: Path to the audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.

        Returns:
            str: Path to the transcription file

        Raises:
            FileOperationError: If file operations fail
        """
        pass

    @abstractmethod
    def transcribe_directory(
        self,
        directory: Optional[str] = None,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
        parallel: bool = False,
        num_processes: Optional[int] = None,
    ) -> List[str]:
        """Transcribe all WAV files in a directory.

        Args:
            directory: Directory containing WAV files (defaults to AUDIO_INPUT_DIR)
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English).
                If provided, skips language detection.
            parallel: Whether to use parallel processing
            num_processes: Number of parallel processes to use (defaults to CPU count)

        Returns:
            List[str]: List of paths to transcription files

        Raises:
            FileOperationError: If directory operations fail
        """
        pass

    @abstractmethod
    def process_files_parallel(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        num_processes: Optional[int] = None,
        model_size: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[str]:
        """Process multiple audio files in parallel using multiprocessing.

        Args:
            input_dir: Directory containing audio files to process
            output_dir: Directory to save processed output (uses AUDIO_OUTPUT_DIR env var if None)
            num_processes: Number of parallel processes to use (defaults to CPU count)
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English)

        Returns:
            List[str]: List of successful transcriptions

        Raises:
            FileOperationError: If directory operations fail
        """
        pass
