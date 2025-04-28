"""Simple plugin loader for audio transcription tool.

This module provides a simplified plugin loading mechanism without complex
registries or dependency injection requirements.
"""

import importlib
import logging
import os
from typing import Any, Dict, Optional

from services.implementations.configuration_manager_impl import (
    ConfigurationManager,
)

logger = logging.getLogger(__name__)


class SimplePluginLoader:
    """Simple plugin loading without complex registries."""

    def __init__(
        self, config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """Initialize the plugin loader.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager or ConfigurationManager()
        self.default_plugins = {
            "transcription": "whisper_transcription",
            "audio_format": "wav_audio_format",
            "output": "file_output",
        }

    def load_plugin(
        self, plugin_type: str, plugin_id: Optional[str] = None
    ) -> Any:
        """Load a plugin by type and ID.

        Args:
            plugin_type: Type of plugin to load
            plugin_id: ID of the plugin to load (uses default if None)

        Returns:
            The instantiated plugin

        Raises:
            ImportError: If the plugin cannot be imported
            AttributeError: If the plugin class cannot be found
        """
        # If no plugin ID specified, use default
        if not plugin_id:
            plugin_id = self.default_plugins.get(plugin_type)
            if not plugin_id:
                raise ValueError(f"No default plugin for type '{plugin_type}'")

        # Get plugin configuration from environment if available
        plugin_config: Dict[str, Any] = {}
        env_prefix = f"PLUGIN_{plugin_type.upper()}_"
        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix) :].lower()
                plugin_config[config_key] = value

        # Try to load from builtin plugins first
        try:
            module_name = f"plugins.builtin.{plugin_id}"
            module = importlib.import_module(module_name)
            class_name = "".join(
                word.capitalize() for word in plugin_id.split("_")
            )
            plugin_class = getattr(module, class_name)

            # Instantiate the plugin
            logger.info(
                f"Loaded builtin plugin: {plugin_id} for type {plugin_type}"
            )
            return plugin_class(**plugin_config)
        except (ImportError, AttributeError) as e:
            logger.debug(f"Builtin plugin not found: {e}")

        # Try custom plugins directory
        try:
            module_name = f"plugins.custom.{plugin_id}"
            module = importlib.import_module(module_name)
            class_name = "".join(
                word.capitalize() for word in plugin_id.split("_")
            )
            plugin_class = getattr(module, class_name)

            # Instantiate the plugin
            logger.info(
                f"Loaded custom plugin: {plugin_id} for type {plugin_type}"
            )
            return plugin_class(**plugin_config)
        except (ImportError, AttributeError) as e:
            logger.error(
                f"Failed to load plugin {plugin_id} for type {plugin_type}: {e}"
            )
            raise ImportError(
                f"Plugin {plugin_id} for type {plugin_type} not found"
            )

    def get_plugin_list(self, plugin_type: str) -> Dict[str, str]:
        """Get a list of available plugins of a specific type.

        Args:
            plugin_type: Type of plugins to list

        Returns:
            Dict mapping plugin IDs to plugin names
        """
        plugins: Dict[str, str] = {}

        # Add default plugin if it exists
        default_id = self.default_plugins.get(plugin_type)
        if default_id:
            plugins[default_id] = f"{default_id} (default)"

        # Look for builtin plugins
        builtin_dir = os.path.join(os.path.dirname(__file__), "builtin")
        if os.path.isdir(builtin_dir):
            for filename in os.listdir(builtin_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    plugin_id = filename[:-3]  # Remove .py extension
                    # Only include plugins that match the requested type
                    if plugin_type in plugin_id:
                        if plugin_id not in plugins:
                            plugins[plugin_id] = plugin_id

        # Look for custom plugins
        custom_dir = os.path.join(os.path.dirname(__file__), "custom")
        if os.path.isdir(custom_dir):
            for filename in os.listdir(custom_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    plugin_id = filename[:-3]  # Remove .py extension
                    # Only include plugins that match the requested type
                    if plugin_type in plugin_id:
                        if plugin_id not in plugins:
                            plugins[plugin_id] = f"{plugin_id} (custom)"

        return plugins


# Create a global instance for convenience
plugin_loader = SimplePluginLoader()
