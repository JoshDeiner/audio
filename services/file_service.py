"""File service for audio transcription tool."""
import glob
import logging
import os
import time
import wave
from typing import Optional, Tuple, Union

import numpy as np
import soundfile as sf

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

    @staticmethod
    def save_text(text: str, file_path: str) -> str:
        """Save text to a file.

        Args:
            text: The text to save
            file_path: Path to the output file

        Returns:
            str: Path to the saved file

        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Create parent directory if it doesn't exist
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                FileService.prepare_directory(parent_dir)

            # Save text to file
            with open(file_path, "w") as f:
                f.write(text)

            logger.info(f"Text saved to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save text file: {e}")
            raise FileOperationError(f"Failed to save text file: {e}")

    @staticmethod
    def save(
        audio_data: Union[np.ndarray, Tuple[np.ndarray, int]], file_path: str
    ) -> str:
        """Save audio data to a file.

        Args:
            audio_data: Audio data as numpy array or tuple of (data, rate)
            file_path: Path to the output file

        Returns:
            str: Path to the saved file

        Raises:
            FileOperationError: If saving fails
        """
        try:
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                FileService.prepare_directory(parent_dir)

            # Extract audio data and sample rate if provided as a tuple
            if isinstance(audio_data, tuple) and len(audio_data) == 2:
                data, sample_rate = audio_data
            else:
                data = audio_data  # type: ignore
                sample_rate = 16000  # Default sample rate

            # Save using soundfile
            sf.write(file_path, data, sample_rate)
            logger.info(f"Audio saved to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            raise FileOperationError(f"Failed to save audio file: {e}")

    @staticmethod
    def generate_temp_output_path() -> str:
        """Generate a temporary output file path.

        Returns:
            str: Path to the temporary output file
        """
        # Get output directory from environment or use default
        output_dir = FileService.sanitize_path(
            os.environ.get("AUDIO_OUTPUT_DIR", "output")
        )
        # Create the output directory if it doesn't exist
        FileService.prepare_directory(output_dir)
        # Generate a unique filename based on timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        return os.path.join(output_dir, f"audio_out_{timestamp}.wav")

    @staticmethod
    def load_latest_transcription() -> Optional[str]:
        """Load the latest transcription file.

        Returns:
            Optional[str]: The content of the latest transcription file or None if not found
        """
        # Get output directory from environment or use default
        output_dir = FileService.sanitize_path(
            os.environ.get("AUDIO_OUTPUT_DIR", "output")
        )
        if not os.path.exists(output_dir):
            logger.warning(f"Output directory not found: {output_dir}")
            return None
        # Find all transcription files
        transcript_files = glob.glob(os.path.join(output_dir, "*.txt"))
        if not transcript_files:
            logger.info("No transcription files found")
            return None
        # Get the most recent file
        latest_file = max(transcript_files, key=os.path.getctime)
        try:
            # Read and return the content
            with open(latest_file, "r") as f:
                content = f.read().strip()
            logger.info(f"Loaded latest transcription from: {latest_file}")
            return content
        except Exception as e:
            logger.error(f"Failed to read transcription file: {e}")
            return None
