"""Audio format plugin interfaces.

This module defines the interfaces for audio format plugins that can be used
to extend the audio application with support for different audio formats.
"""

import logging
from abc import abstractmethod
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

from plugins.plugin_base import Plugin

logger = logging.getLogger(__name__)


class AudioFormatPlugin(Plugin):
    """Base interface for audio format plugins.

    Plugins that implement this interface can provide support for different 
    audio file formats like MP3, FLAC, etc.
    """
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get the file extensions supported by this plugin.

        Returns:
            List of supported file extensions (e.g., ['.mp3', '.m4a'])
        """
        pass
    
    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """Validate that a file is in the correct format.

        Args:
            file_path: Path to the audio file to validate

        Returns:
            bool: True if the file is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def read_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Read an audio file and convert to numpy array.

        Args:
            file_path: Path to the audio file

        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            AudioFormatError: If reading fails
        """
        pass
    
    @abstractmethod
    def write_file(self, file_path: str, audio_data: np.ndarray, 
                sample_rate: int, **kwargs) -> str:
        """Write audio data to a file.

        Args:
            file_path: Path to save the audio file
            audio_data: Audio data as numpy array
            sample_rate: Sample rate in Hz
            **kwargs: Additional format-specific options

        Returns:
            str: Path to the saved file
            
        Raises:
            AudioFormatError: If writing fails
        """
        pass
    
    @abstractmethod
    def get_format_info(self) -> Dict:
        """Get information about the audio format.

        Returns:
            Dict with format information
        """
        pass