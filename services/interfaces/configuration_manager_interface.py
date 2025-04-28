"""Configuration Manager interface for centralized configuration handling."""

from abc import ABC, abstractmethod
from typing import Any


class IConfigurationManager(ABC):
    """Interface for centralized configuration management.

    This interface defines methods for accessing and managing configuration
    values from various sources such as explicit values, environment variables,
    and default values.
    """

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key to look up
            default: Default value if key is not found in any source

        Returns:
            The configuration value from the highest priority source
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        pass

    @abstractmethod
    def set_default(self, key: str, default_value: Any) -> None:
        """Set a default configuration value if not already set.

        Args:
            key: Configuration key
            default_value: Default value to use if key not found
        """
        pass
