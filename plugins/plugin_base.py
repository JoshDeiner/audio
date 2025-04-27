"""Base plugin interfaces for the audio application.

This module provides the core interfaces that all plugins must implement,
defining the standard contract for extending the application.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type

from config.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Base interface for all plugins.

    All plugins must inherit from this class and implement its methods.
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Get the unique identifier for this plugin.

        Returns:
            str: Unique plugin identifier
        """
        pass

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Get the human-readable name for this plugin.

        Returns:
            str: Plugin name
        """
        pass

    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Get the version of this plugin.

        Returns:
            str: Plugin version in format major.minor.patch
        """
        pass

    @abstractmethod
    def initialize(
        self, config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """Initialize the plugin with configuration.

        Args:
            config_manager: Configuration manager instance
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the plugin."""
        pass


class PluginRegistry:
    """Registry for managing plugins.

    This class provides methods for registering, discovering, and accessing plugins.
    """

    _plugins: Dict[str, Dict[str, Type[Plugin]]] = {}
    _instances: Dict[str, Dict[str, Plugin]] = {}

    @classmethod
    def register_plugin_class(
        cls, plugin_type: str, plugin_class: Type[Plugin]
    ) -> None:
        """Register a plugin class by type.

        Args:
            plugin_type: The type of plugin (e.g., 'transcription', 'audio_format')
            plugin_class: The plugin class to register
        """
        if plugin_type not in cls._plugins:
            cls._plugins[plugin_type] = {}

        plugin_id = plugin_class.plugin_id  # type: ignore

        if plugin_id in cls._plugins[plugin_type]:
            logger.warning(
                f"Plugin {plugin_id} already registered for type {plugin_type}, overwriting"
            )

        cls._plugins[plugin_type][plugin_id] = plugin_class
        logger.info(
            f"Registered plugin class {plugin_class.__name__} with ID {plugin_id} for type {plugin_type}"
        )

    @classmethod
    def get_plugin_instance(
        cls,
        plugin_type: str,
        plugin_id: str,
        config_manager: Optional[ConfigurationManager] = None,
    ) -> Optional[Plugin]:
        """Get or create a plugin instance.

        Args:
            plugin_type: The type of plugin
            plugin_id: The plugin identifier
            config_manager: Optional configuration manager

        Returns:
            Plugin instance or None if not found
        """
        # Initialize the type dictionaries if they don't exist
        if plugin_type not in cls._instances:
            cls._instances[plugin_type] = {}

        # Return existing instance if available
        if plugin_id in cls._instances[plugin_type]:
            return cls._instances[plugin_type][plugin_id]

        # Create new instance if the class is registered
        if (
            plugin_type in cls._plugins
            and plugin_id in cls._plugins[plugin_type]
        ):
            plugin_class = cls._plugins[plugin_type][plugin_id]
            instance = plugin_class()
            instance.initialize(config_manager)
            cls._instances[plugin_type][plugin_id] = instance
            return instance

        logger.warning(f"Plugin {plugin_id} not found for type {plugin_type}")
        return None

    @classmethod
    def get_plugin_types(cls) -> Set[str]:
        """Get all registered plugin types.

        Returns:
            Set of plugin type strings
        """
        return set(cls._plugins.keys())

    @classmethod
    def get_plugins_for_type(cls, plugin_type: str) -> List[str]:
        """Get all plugin IDs for a specific type.

        Args:
            plugin_type: The type of plugin

        Returns:
            List of plugin IDs
        """
        if plugin_type not in cls._plugins:
            return []
        return list(cls._plugins[plugin_type].keys())

    @classmethod
    def cleanup_all(cls) -> None:
        """Clean up all plugin instances."""
        for plugin_type in cls._instances:
            for plugin_id, instance in cls._instances[plugin_type].items():
                try:
                    instance.cleanup()
                    logger.info(
                        f"Cleaned up plugin {plugin_id} of type {plugin_type}"
                    )
                except Exception as e:
                    logger.error(f"Error cleaning up plugin {plugin_id}: {e}")

        cls._instances = {}
