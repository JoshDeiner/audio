"""Configuration Manager implementation for centralized configuration handling."""

import logging
import os
from typing import Any, Dict, Optional

from services.interfaces.configuration_manager_interface import IConfigurationManager

logger = logging.getLogger(__name__)


class ConfigurationManager(IConfigurationManager):
    """Centralized configuration management for the application.

    This class handles loading and providing access to configuration values
    from various sources, prioritizing them in the following order:
    1. Explicitly provided values (during initialization)
    2. Environment variables
    3. Default values
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the configuration manager.

        Args:
            config_dict: Optional dictionary with configuration values
                that take precedence over environment variables
        """
        self._config: Dict[str, Any] = config_dict or {}

        # Load configuration defaults
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default configuration settings."""
        # Audio input/output configuration
        self.set_default("AUDIO_INPUT_DIR", "input")
        self.set_default("AUDIO_OUTPUT_DIR", "output")

        # Whisper model configuration
        self.set_default("WHISPER_MODEL", "tiny")
        self.set_default("WHISPER_COMPUTE_TYPE", "int8")
        self.set_default("WHISPER_DEVICE", "cpu")

        # Text-to-speech configuration
        self.set_default("TTS_LANGUAGE", "en")
        self.set_default("TTS_SPEED", "normal")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key to look up
            default: Default value if key is not found in any source

        Returns:
            The configuration value from the highest priority source
        """
        # Check if value exists in explicit configuration
        if key in self._config:
            return self._config[key]

        # Check environment variables
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value

        # Use provided default if key not found anywhere
        return default

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        logger.debug(f"Configuration set: {key}={value}")

    def set_default(self, key: str, default_value: Any) -> None:
        """Set a default configuration value if not already set.

        Args:
            key: Configuration key
            default_value: Default value to use if key not found
        """
        if key not in self._config and key not in os.environ:
            self._config[key] = default_value
            logger.debug(f"Default configuration set: {key}={default_value}")