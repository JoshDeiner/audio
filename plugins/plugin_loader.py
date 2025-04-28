"""Plugin loader for the audio application.

This module provides functionality to discover and load plugins dynamically.
"""

import importlib
import importlib.util
import inspect
import logging
import os
import pkgutil
import sys
from typing import Dict, List, Optional

from config.configuration_manager import ConfigurationManager
from plugins.audio_format_plugin import AudioFormatPlugin
from plugins.output_plugin import OutputPlugin
from plugins.plugin_base import Plugin, PluginRegistry
from plugins.preprocessing_plugin import PreprocessingPlugin
from plugins.transcription_plugin import TranscriptionPlugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """Loader for discovering and registering plugins."""

    # Mapping of plugin types to their base classes
    _plugin_types = {
        "transcription": TranscriptionPlugin,
        "audio_format": AudioFormatPlugin,
        "output": OutputPlugin,
        "preprocessing": PreprocessingPlugin,
    }

    @classmethod
    def discover_plugins(
        cls, plugin_dirs: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """Discover and register all available plugins.

        Args:
            plugin_dirs: Optional list of directories to search for plugins.
                         If None, default locations will be used.

        Returns:
            Dict mapping plugin types to lists of plugin IDs
        """
        if plugin_dirs is None:
            # Default locations: built-in plugins and user plugins directory
            plugin_dirs = [
                os.path.join(os.path.dirname(__file__), "builtin"),
                os.path.expanduser("~/.audio/plugins"),
            ]

            # Add application plugin directory based on config if available
            try:
                app_plugin_dir = ConfigurationManager.get("PLUGIN_DIR")
                if app_plugin_dir and os.path.isdir(app_plugin_dir):
                    plugin_dirs.append(app_plugin_dir)
            except Exception:
                pass

        # Create result dictionary
        result: Dict[str, List[str]] = {}
        for plugin_type in cls._plugin_types:
            result[plugin_type] = []

        # Scan each directory for plugins
        for plugin_dir in plugin_dirs:
            if not os.path.isdir(plugin_dir):
                logger.debug(f"Plugin directory not found: {plugin_dir}")
                continue

            logger.info(f"Scanning for plugins in: {plugin_dir}")
            cls._scan_directory(plugin_dir, result)

        return result

    @classmethod
    def _scan_directory(
        cls, directory: str, result: Dict[str, List[str]]
    ) -> None:
        """Scan a directory for plugins.

        Args:
            directory: Directory to scan
            result: Result dictionary to update
        """
        # Add directory to Python path temporarily
        if directory not in sys.path:
            sys.path.insert(0, directory)

        # Get all Python modules in the directory
        for _, name, is_pkg in pkgutil.iter_modules([directory]):
            if is_pkg:
                # Recursively scan packages
                pkg_dir = os.path.join(directory, name)
                cls._scan_directory(pkg_dir, result)
            else:
                try:
                    # Import the module
                    module_name = name
                    if module_name.endswith(".py"):
                        module_name = module_name[:-3]

                    module = importlib.import_module(module_name)

                    # Find and register plugin classes
                    cls._register_plugins_from_module(module, result)
                except Exception as e:
                    logger.error(f"Error loading plugin module {name}: {e}")

    @classmethod
    def _register_plugins_from_module(
        cls, module, result: Dict[str, List[str]]
    ) -> None:
        """Register all plugins found in a module.

        Args:
            module: Module to scan for plugins
            result: Result dictionary to update
        """
        for name, obj in inspect.getmembers(module):
            # Check if it's a class and a plugin
            if (
                not inspect.isclass(obj)
                or not issubclass(obj, Plugin)
                or obj is Plugin
            ):
                continue

            # Determine plugin type
            plugin_type = None
            for type_name, base_class in cls._plugin_types.items():
                if issubclass(obj, base_class) and obj is not base_class:
                    plugin_type = type_name
                    break

            if plugin_type is None:
                continue  # Not a plugin we're interested in

            try:
                # Try to register the plugin
                PluginRegistry.register_plugin_class(plugin_type, obj)

                # Add to result if successful
                plugin_id = obj.plugin_id
                if plugin_id not in result[plugin_type]:
                    result[plugin_type].append(plugin_id)

                logger.info(
                    f"Registered {plugin_type} plugin: {name} ({plugin_id})"
                )
            except Exception as e:
                logger.error(f"Error registering plugin {name}: {e}")
