"""Built-in file output plugin.

This module provides an output plugin that saves transcription results to files.
"""

import logging
import os
import time
from typing import Any, Dict, Optional

from config.configuration_manager import ConfigurationManager
from plugins.output_plugin import OutputPlugin
from services.exceptions import FileOperationError

logger = logging.getLogger(__name__)


class FileOutputPlugin(OutputPlugin):
    """File output plugin.

    This plugin saves transcription results to text files.
    """

    @property
    def plugin_id(self) -> str:
        """Get the unique identifier for this plugin.

        Returns:
            str: Unique plugin identifier
        """
        return "file_output"

    @property
    def plugin_name(self) -> str:
        """Get the human-readable name for this plugin.

        Returns:
            str: Plugin name
        """
        return "File Output"

    @property
    def plugin_version(self) -> str:
        """Get the version of this plugin.

        Returns:
            str: Plugin version in format major.minor.patch
        """
        return "1.0.0"

    def __init__(self) -> None:
        """Initialize the plugin."""
        self._output_dir = None
        self._file_prefix = "transcript_"
        self._file_extension = ".txt"

    def initialize(
        self, config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """Initialize the plugin with configuration.

        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigurationManager

        # Get output directory from configuration
        self._output_dir = self.config_manager.get(
            "AUDIO_OUTPUT_DIR", "output"
        )

        # Create directory if it doesn't exist
        if not os.path.exists(self._output_dir):
            try:
                os.makedirs(self._output_dir, exist_ok=True)
                logger.info(f"Created output directory: {self._output_dir}")
            except Exception as e:
                logger.error(f"Failed to create output directory: {e}")
                raise FileOperationError(
                    f"Failed to create output directory: {e}"
                )

        # Get optional file prefix from configuration
        custom_prefix = self.config_manager.get("FILE_OUTPUT_PREFIX")
        if custom_prefix:
            self._file_prefix = custom_prefix

        logger.info(
            f"Initialized file output plugin (dir: {self._output_dir})"
        )

    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        logger.info("Cleaned up file output plugin")

    def handle_transcription(
        self, transcription: str, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save a transcription to a file.

        Args:
            transcription: The transcribed text
            metadata: Optional metadata about the transcription

        Returns:
            bool: True if successful, False otherwise

        Raises:
            OutputError: If saving fails
        """
        try:
            # Generate filename
            timestamp = time.strftime("%Y%m%d-%H%M%S")

            # Use source filename from metadata if available
            source_file = None
            if metadata and "source_file" in metadata:
                source_file = os.path.basename(metadata["source_file"])
                source_name = os.path.splitext(source_file)[0]
                filename = f"{self._file_prefix}{source_name}_{timestamp}{self._file_extension}"
            else:
                filename = (
                    f"{self._file_prefix}{timestamp}{self._file_extension}"
                )

            # Full output path
            output_path = os.path.join(self._output_dir, filename)

            # Save to file
            with open(output_path, "w") as f:
                f.write(transcription)

                # Add metadata as comments if available
                if metadata:
                    f.write("\n\n# Metadata:\n")
                    for key, value in metadata.items():
                        f.write(f"# {key}: {value}\n")

            logger.info(f"Saved transcription to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            raise FileOperationError(f"Failed to save transcription: {e}")

    def supports_batch(self) -> bool:
        """Check if this plugin supports batch processing.

        Returns:
            bool: True since file output supports batch processing
        """
        return True

    def handle_batch(
        self, items: Dict[str, Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Process multiple transcription results in batch.

        Args:
            items: Dictionary mapping IDs to dictionaries with 'text' and optional 'metadata'

        Returns:
            Dict mapping IDs to success status

        Raises:
            OutputError: If batch processing fails
        """
        results = {}

        for item_id, item_data in items.items():
            try:
                text = item_data.get("text", "")
                metadata = item_data.get("metadata")

                success = self.handle_transcription(text, metadata)
                results[item_id] = success
            except Exception as e:
                logger.error(f"Failed to process item {item_id}: {e}")
                results[item_id] = False

        return results
