"""Plugin manager for the audio application.

This module provides a high-level interface for managing and using plugins.
"""

import logging
import os
from typing import Dict, List, Optional

from plugins.audio_format_plugin import AudioFormatPlugin
from plugins.output_plugin import OutputPlugin
from plugins.plugin_base import Plugin, PluginRegistry
from plugins.plugin_loader import PluginLoader
from plugins.preprocessing_plugin import PreprocessingPlugin
from plugins.transcription_plugin import TranscriptionPlugin
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)

logger = logging.getLogger(__name__)


class PluginManager:
    """Manager for audio application plugins.

    This class provides a high-level interface for discovering, loading,
    and using plugins in the audio application.
    """

    # Singleton instance - kept for compatibility but will be phased out
    _instance = None

    @classmethod
    def get_instance(cls) -> Optional["PluginManager"]:
        """Get the singleton instance if it exists.

        Returns:
            The singleton instance or None if not initialized
        """
        return cls._instance

    def __init__(self, config_manager: IConfigurationManager):
        """Initialize the plugin manager.

        Args:
            config_manager: Configuration manager instance
        """
        # Set singleton instance for backward compatibility
        if PluginManager._instance is None:
            PluginManager._instance = self

        self.config_manager = config_manager
        self._discovered_plugins: Dict[str, List[str]] = {}
        self._active_plugins: Dict[str, Plugin] = {}
        self._initialized = False

    def initialize(self) -> Dict[str, List[str]]:
        """Initialize the plugin system.

        Returns:
            Dict mapping plugin types to lists of plugin IDs
        """
        if self._initialized:
            return self._discovered_plugins

        # Get plugin directories from configuration
        plugin_dirs = self._get_plugin_directories()

        # Discover available plugins
        self._discovered_plugins = PluginLoader.discover_plugins(plugin_dirs)

        # Load default plugins if configured
        self._load_default_plugins()

        logger.info("Plugin manager initialized")
        self._initialized = True
        return self._discovered_plugins

    def _get_plugin_directories(self) -> List[str]:
        """Get the directories to search for plugins.

        Returns:
            List of directory paths
        """
        plugin_dirs = []

        # Add built-in plugins directory
        import plugins

        builtin_dir = os.path.join(
            os.path.dirname(plugins.__file__), "builtin"
        )
        plugin_dirs.append(builtin_dir)

        # Add user plugins directory
        user_dir = os.path.expanduser("~/.audio/plugins")
        plugin_dirs.append(user_dir)

        # Add directory from configuration
        config_dir = self.config_manager.get("PLUGIN_DIR")
        if config_dir:
            plugin_dirs.append(config_dir)

        return plugin_dirs

    def _load_default_plugins(self) -> None:
        """Load the default plugins based on configuration."""
        # Get default plugin IDs from configuration
        default_transcription = self.config_manager.get(
            "DEFAULT_TRANSCRIPTION_PLUGIN", "whisper_transcription"
        )
        default_audio_format = self.config_manager.get(
            "DEFAULT_AUDIO_FORMAT_PLUGIN", "wav_audio_format"
        )
        default_output = self.config_manager.get(
            "DEFAULT_OUTPUT_PLUGIN", "file_output"
        )

        # Load default plugins
        if default_transcription:
            self.get_transcription_plugin(default_transcription)

        if default_audio_format:
            self.get_audio_format_plugin(default_audio_format)

        if default_output:
            self.get_output_plugin(default_output)

    def get_transcription_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[TranscriptionPlugin]:
        """Get a transcription plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            TranscriptionPlugin instance or None if not found
        """
        # Use default if not specified
        if plugin_id is None:
            plugin_id = self.config_manager.get(
                "DEFAULT_TRANSCRIPTION_PLUGIN", "whisper_transcription"
            )

        return self._get_plugin_instance("transcription", plugin_id)

    def get_audio_format_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[AudioFormatPlugin]:
        """Get an audio format plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            AudioFormatPlugin instance or None if not found
        """
        # Use default if not specified
        if plugin_id is None:
            plugin_id = self.config_manager.get(
                "DEFAULT_AUDIO_FORMAT_PLUGIN", "wav_audio_format"
            )

        return self._get_plugin_instance("audio_format", plugin_id)

    def get_output_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[OutputPlugin]:
        """Get an output plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            OutputPlugin instance or None if not found
        """
        # Use default if not specified
        if plugin_id is None:
            plugin_id = self.config_manager.get(
                "DEFAULT_OUTPUT_PLUGIN", "file_output"
            )

        return self._get_plugin_instance("output", plugin_id)

    def get_preprocessing_plugin(
        self, plugin_id: Optional[str] = None
    ) -> Optional[PreprocessingPlugin]:
        """Get a preprocessing plugin instance.

        Args:
            plugin_id: ID of the plugin to get, or None for the default

        Returns:
            PreprocessingPlugin instance or None if not found
        """
        # Use default if not specified
        if plugin_id is None:
            plugin_id = self.config_manager.get("DEFAULT_PREPROCESSING_PLUGIN")
            if not plugin_id:
                return None

        return self._get_plugin_instance("preprocessing", plugin_id)

    def _get_plugin_instance(
        self, plugin_type: str, plugin_id: str
    ) -> Optional[Plugin]:
        """Get a plugin instance of the specified type.

        Args:
            plugin_type: Type of plugin
            plugin_id: ID of the plugin

        Returns:
            Plugin instance or None if not found
        """
        # Check if we already have an instance
        key = f"{plugin_type}:{plugin_id}"
        if key in self._active_plugins:
            return self._active_plugins[key]

        # Get a new instance from the registry
        instance = PluginRegistry.get_plugin_instance(
            plugin_type, plugin_id, self.config_manager
        )

        if instance:
            self._active_plugins[key] = instance

        return instance

    def get_available_plugins(
        self, plugin_type: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Get the available plugins.

        Args:
            plugin_type: Optional type to filter by

        Returns:
            Dict mapping plugin types to lists of plugin IDs
        """
        if not self._initialized:
            self.initialize()

        if plugin_type:
            return {plugin_type: self._discovered_plugins.get(plugin_type, [])}
        else:
            return self._discovered_plugins

    def cleanup(self) -> None:
        """Clean up all active plugins."""
        for key, instance in self._active_plugins.items():
            try:
                instance.cleanup()
                logger.info(f"Cleaned up plugin: {key}")
            except Exception as e:
                logger.error(f"Error cleaning up plugin {key}: {e}")

        self._active_plugins = {}
        self._initialized = False
