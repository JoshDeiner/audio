"""File-based transcription service for audio transcription tool."""
import logging
import os
from typing import List, Optional

from colorama import Fore, Style  # type: ignore

from services.exceptions import FileOperationError
from services.file_service import FileService
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class FileTranscriptionService:
    """Service for transcribing audio files without recording."""

    def __init__(self):
        """Initialize the file transcription service."""
        self.file_service = FileService()
        self.transcription_service = TranscriptionService()

    def transcribe_file(
        self, 
        file_path: str, 
        model_size: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """Transcribe a single audio file.

        Args:
            file_path: Path to the audio file
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English). If provided, skips language detection.

        Returns:
            str: Path to the transcription file

        Raises:
            FileOperationError: If file operations fail
        """
        # Validate file path
        if not os.path.exists(file_path):
            raise FileOperationError(f"File not found: {file_path}")

        # Validate audio file
        if not self.file_service.validate_audio_file(file_path):
            raise FileOperationError(f"Invalid audio file: {file_path}")

        # Transcribe the file
        print(f"{Fore.CYAN}Transcribing file: {Fore.YELLOW}{file_path}{Style.RESET_ALL}")
        transcription = self.transcription_service.transcribe_audio(file_path, model_size, language)
        
        # The transcription_service already saves the file and returns the text
        print(f"\n{Fore.GREEN}Transcription:{Style.RESET_ALL}\n{transcription}\n")
        
        return transcription

    def transcribe_directory(
        self, 
        directory: Optional[str] = None, 
        model_size: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """Transcribe all WAV files in a directory.

        Args:
            directory: Directory containing WAV files (defaults to AUDIO_INPUT_DIR)
            model_size: Whisper model size (tiny, base, small, medium, large)
            language: Language code to use (e.g., 'en' for English). If provided, skips language detection.

        Returns:
            List[str]: List of paths to transcription files

        Raises:
            FileOperationError: If directory operations fail
        """
        # Use provided directory or get from environment
        if not directory:
            directory = os.environ.get("AUDIO_INPUT_DIR", "input")

        # Validate directory
        if not os.path.isdir(directory):
            raise FileOperationError(f"Directory not found: {directory}")

        # Find all WAV files in the directory
        wav_files = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith(".wav")
        ]

        if not wav_files:
            print(f"{Fore.YELLOW}No WAV files found in {directory}{Style.RESET_ALL}")
            return []

        # Transcribe each file
        transcriptions = []
        for wav_file in wav_files:
            try:
                transcription = self.transcribe_file(wav_file, model_size, language)
                transcriptions.append(transcription)
            except Exception as e:
                logger.error(f"Error transcribing {wav_file}: {e}")
                print(f"{Fore.RED}Error transcribing {wav_file}: {e}{Style.RESET_ALL}")

        return transcriptions
