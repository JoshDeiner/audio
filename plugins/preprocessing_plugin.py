"""Audio preprocessing plugin interfaces.

This module defines the interfaces for preprocessing plugins that can be used
to extend the audio application with custom audio processing steps.
"""

import logging
from abc import abstractmethod
from typing import Dict, Optional, Tuple

import numpy as np

from plugins.plugin_base import Plugin

logger = logging.getLogger(__name__)


class PreprocessingPlugin(Plugin):
    """Base interface for audio preprocessing plugins.

    Plugins that implement this interface can provide custom audio processing
    functionality like noise reduction, normalization, etc.
    """
    
    @abstractmethod
    def process_audio(self, audio_data: np.ndarray, sample_rate: int,
                    options: Optional[Dict] = None) -> Tuple[np.ndarray, int]:
        """Process audio data.

        Args:
            audio_data: Audio data as numpy array
            sample_rate: Sample rate in Hz
            options: Additional processing options

        Returns:
            Tuple of (processed_audio_data, sample_rate)
            
        Raises:
            PreprocessingError: If processing fails
        """
        pass
    
    @abstractmethod
    def get_default_options(self) -> Dict:
        """Get default processing options.

        Returns:
            Dict of default options
        """
        pass
    
    @abstractmethod
    def get_processing_info(self) -> Dict:
        """Get information about the processing capabilities.

        Returns:
            Dict with processor information
        """
        pass