"""Output plugin interfaces.

This module defines the interfaces for output plugins that can be used
to extend the audio application with different output handlers.
"""

import logging
from abc import abstractmethod
from typing import Any, Dict, Optional

from plugins.plugin_base import Plugin

logger = logging.getLogger(__name__)


class OutputPlugin(Plugin):
    """Base interface for output plugins.

    Plugins that implement this interface can provide different ways to handle
    transcription results, such as saving to databases, sending to APIs, etc.
    """
    
    @abstractmethod
    def handle_transcription(self, transcription: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Process a transcription result.

        Args:
            transcription: The transcribed text
            metadata: Optional metadata about the transcription (e.g., source file, timestamp)

        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            OutputError: If processing fails
        """
        pass
    
    @abstractmethod
    def supports_batch(self) -> bool:
        """Check if this plugin supports batch processing.

        Returns:
            bool: True if batch processing is supported, False otherwise
        """
        pass
    
    @abstractmethod
    def handle_batch(self, items: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Process multiple transcription results in batch.

        Args:
            items: Dictionary mapping IDs to dictionaries with 'text' and optional 'metadata'

        Returns:
            Dict mapping IDs to success status
            
        Raises:
            OutputError: If batch processing fails
        """
        pass