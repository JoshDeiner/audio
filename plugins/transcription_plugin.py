"""Transcription plugin interfaces.

This module defines the interfaces for transcription plugins that can be used
to extend the audio application with different transcription implementations.
"""

import logging
from abc import abstractmethod
from typing import Dict, Optional

from config.configuration_manager import ConfigurationManager
from plugins.plugin_base import Plugin

logger = logging.getLogger(__name__)


class TranscriptionPlugin(Plugin):
    """Base interface for transcription plugins.

    Plugins that implement this interface can provide different transcription engines
    for the audio application.
    """

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        options: Optional[Dict] = None,
    ) -> str:
        """Transcribe audio file to text.

        Args:
            audio_path: Path to the audio file
            language: Optional language code
            options: Additional options for the transcription engine

        Returns:
            str: Transcribed text

        Raises:
            TranscriptionError: If transcription fails
        """
        pass

    @abstractmethod
    def supports_language(self, language_code: str) -> bool:
        """Check if this plugin supports the given language.

        Args:
            language_code: ISO language code

        Returns:
            bool: True if supported, False otherwise
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages.

        Returns:
            Dict mapping language codes to language names
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        """Get information about the transcription model.

        Returns:
            Dict with model information
        """
        pass
