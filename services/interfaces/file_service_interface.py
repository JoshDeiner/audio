"""File service interface for audio transcription tool."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

import numpy as np


class IFileService(ABC):
    """Interface for file operations."""

    @abstractmethod
    def sanitize_path(self, path: Optional[str]) -> str:
        """Sanitize and normalize a file path.

        Args:
            path: Input path string, may be None

        Returns:
            str: Sanitized path or empty string if input was None
        """
        pass

    @abstractmethod
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate that the file is a proper audio file.

        Args:
            file_path: Path to the audio file to validate

        Returns:
            bool: True if the file is a valid audio file, False otherwise
        """
        pass

    @abstractmethod
    def prepare_directory(self, dir_path: str) -> str:
        """Prepare a directory for file operations.

        Args:
            dir_path: Path to the directory

        Returns:
            str: Path to the prepared directory

        Raises:
            FileOperationError: If directory cannot be created or accessed
        """
        pass

    @abstractmethod
    def save_text(self, text: str, file_path: str) -> str:
        """Save text to a file.

        Args:
            text: The text to save
            file_path: Path to the output file

        Returns:
            str: Path to the saved file

        Raises:
            FileOperationError: If saving fails
        """
        pass

    @abstractmethod
    def save(
        self,
        audio_data: Union[np.ndarray, Tuple[np.ndarray, int]],
        file_path: str,
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
        pass

    @abstractmethod
    def generate_temp_output_path(self) -> str:
        """Generate a temporary output file path.

        Returns:
            str: Path to the temporary output file
        """
        pass

    @abstractmethod
    def read_text(self, file_path: str) -> str:
        """Read text from a file.

        Args:
            file_path: Path to the text file

        Returns:
            str: The text content of the file

        Raises:
            FileOperationError: If reading fails
        """
        pass

    @abstractmethod
    def load_latest_transcription(self) -> Optional[str]:
        """Load the latest transcription file.

        Returns:
            Optional[str]: The content of the latest transcription file or None if not found
        """
        pass
