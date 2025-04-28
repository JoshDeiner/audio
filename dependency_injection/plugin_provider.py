"""Plugin provider for the audio application.

This module provides a dependency-injection friendly interface for working with plugins
and maintaining their lifecycle.
"""

import logging
from typing import Dict, List, Optional

from plugins.audio_format_plugin import AudioFormatPlugin
from plugins.output_plugin import OutputPlugin
from plugins.plugin_manager_refactored import PluginManager
from plugins.preprocessing_plugin import PreprocessingPlugin
from plugins.transcription_plugin import TranscriptionPlugin
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)

logger = logging.getLogger(__name__)


class PluginProvider:
    """Provider for managing plugins in a dependency injection context.

    This class wraps the PluginManager to provide a cleaner API and ensure
    proper dependency injection and lifecycle management.
    """

    def __init__(self, config_manager: IConfigurationManager) -> None:
        """Initialize the plugin provider.

        Args:
            config_manager: Configuration manager instance
        """
        self.plugin_manager = PluginManager(config_manager)
        self._initialized = False

    def initialize(self) -> Dict[str, List[str]]:
        """Initialize the plugin system.

        Returns:
            Dict mapping plugin types to lists of plugin IDs
        """
        if not self._initialized:
            result = self.plugin_manager.initialize()
            self._initialized = True
            return result
        return self.plugin_manager.get_available_plugins()

    def get_transcription_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[TranscriptionPlugin]:
        """Get a transcription plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            TranscriptionPlugin instance or None if not found
        """
        self._ensure_initialized()
        return self.plugin_manager.get_transcription_plugin(plugin_id)

    def get_audio_format_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[AudioFormatPlugin]:
        """Get an audio format plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            AudioFormatPlugin instance or None if not found
        """
        self._ensure_initialized()
        return self.plugin_manager.get_audio_format_plugin(plugin_id)

    def get_output_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[OutputPlugin]:
        """Get an output plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            OutputPlugin instance or None if not found
        """
        self._ensure_initialized()
        return self.plugin_manager.get_output_plugin(plugin_id)

    def get_preprocessing_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[PreprocessingPlugin]:
        """Get a preprocessing plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            PreprocessingPlugin instance or None if not found
        """
        self._ensure_initialized()
        return self.plugin_manager.get_preprocessing_plugin(plugin_id)

    def get_available_plugins(
        self, plugin_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get the available plugins.

        Args:
            plugin_type: Optional type to filter by

        Returns:
            Dict mapping plugin types to lists of plugin IDs
        """
        self._ensure_initialized()
        return self.plugin_manager.get_available_plugins(plugin_type)

    def cleanup(self) -> None:
        """Clean up all plugin resources."""
        if self._initialized:
            self.plugin_manager.cleanup()
            self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure the plugin provider is initialized."""
        if not self._initialized:
            self.initialize()
