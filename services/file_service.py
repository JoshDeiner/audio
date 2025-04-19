"""File service for audio transcription tool."""
import logging
import os
import wave
from typing import Optional

from services.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class FileService:
    """Service for file operations."""

    @staticmethod
    def sanitize_path(path: Optional[str]) -> str:
        """Sanitize and normalize a file path.

        Args:
            path: Input path string, may be None

        Returns:
            str: Sanitized path or empty string if input was None
        """
        if not path:
            return ""

        # Expand user directory (~/...)
        path = os.path.expanduser(path)

        # Normalize path separators and resolve relative paths
        return os.path.normpath(path)

    @staticmethod
    def validate_audio_file(file_path: str) -> bool:
        """Validate that the file is a proper audio file.

        Args:
            file_path: Path to the audio file to validate

        Returns:
            bool: True if the file is a valid WAV file, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False

        try:
            with wave.open(file_path, "rb") as wf:
                # Check basic WAV file properties
                if wf.getnchannels() < 1:
                    logger.error(f"Invalid audio channels in {file_path}")
                    return False

                if wf.getsampwidth() < 1:
                    logger.error(f"Invalid sample width in {file_path}")
                    return False

                if wf.getframerate() < 1:
                    logger.error(f"Invalid frame rate in {file_path}")
                    return False

                return True
        except wave.Error as e:
            logger.error(f"WAV file format error: {e}")
            return False
        except (IOError, OSError) as e:
            logger.error(f"File I/O error during audio validation: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during audio validation: {e}")
            return False

    @staticmethod
    def prepare_directory(dir_path: str) -> str:
        """Prepare a directory for file operations.

        Args:
            dir_path: Path to the directory

        Returns:
            str: Path to the prepared directory

        Raises:
            FileOperationError: If directory cannot be created or accessed
        """
        if not dir_path:
            raise FileOperationError("Directory path cannot be empty")

        # Try to create directory if it doesn't exist
        if not os.path.isdir(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            except (IOError, OSError) as e:
                logger.error(f"Failed to create directory: {e}")
                raise FileOperationError(
                    f"Failed to create directory: {dir_path}"
                )

        return dir_path
