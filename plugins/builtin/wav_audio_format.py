"""Built-in WAV audio format plugin.

This module provides an audio format plugin for WAV files.
"""

import logging
import os
import wave
from typing import Dict, List, Tuple

import numpy as np
import soundfile as sf

from plugins.audio_format_plugin import AudioFormatPlugin
from services.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class WavAudioFormatPlugin(AudioFormatPlugin):
    """WAV audio format plugin.

    This plugin provides support for WAV audio files.
    """
    
    @property
    def plugin_id(self) -> str:
        return "wav_audio_format"
    
    @property
    def plugin_name(self) -> str:
        return "WAV Audio Format"
    
    @property
    def plugin_version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config_manager=None) -> None:
        """Initialize the plugin with configuration.

        Args:
            config_manager: Configuration manager instance (unused for this plugin)
        """
        logger.info("Initialized WAV audio format plugin")
    
    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        logger.info("Cleaned up WAV audio format plugin")
    
    def get_supported_extensions(self) -> List[str]:
        """Get the file extensions supported by this plugin.

        Returns:
            List of supported file extensions
        """
        return [".wav"]
    
    def validate_file(self, file_path: str) -> bool:
        """Validate that a file is a proper WAV file.

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
    
    def read_file(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Read a WAV file and convert to numpy array.

        Args:
            file_path: Path to the audio file

        Returns:
            Tuple of (audio_data, sample_rate)
            
        Raises:
            AudioFormatError: If reading fails
        """
        try:
            data, sample_rate = sf.read(file_path)
            logger.info(f"Read WAV file: {file_path} (sample rate: {sample_rate}Hz)")
            return data, sample_rate
        except Exception as e:
            error_msg = f"Failed to read WAV file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def write_file(self, file_path: str, audio_data: np.ndarray, 
                sample_rate: int, **kwargs) -> str:
        """Write audio data to a WAV file.

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
        try:
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                
            # Add .wav extension if not present
            if not file_path.lower().endswith(".wav"):
                file_path += ".wav"
                
            # Save using soundfile
            sf.write(file_path, audio_data, sample_rate)
            logger.info(f"Saved WAV file: {file_path}")
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to save WAV file: {e}"
            logger.error(error_msg)
            raise FileOperationError(error_msg)
    
    def get_format_info(self) -> Dict:
        """Get information about the audio format.

        Returns:
            Dict with format information
        """
        return {
            "format_name": "WAV",
            "extensions": [".wav"],
            "description": "Waveform Audio File Format",
            "max_channels": "unlimited",
            "max_bit_depth": 32,
            "compression": "uncompressed",
        }