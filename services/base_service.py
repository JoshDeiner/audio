"""Base interface for audio service architecture.

This module provides the base interface for all service classes in the
audio transcription system, enforcing consistent patterns and methods.

Author: Claude Code
Created: 2025-04-27
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseService(ABC):
    """Base interface for all audio services.

    This abstract class defines the common interface that all services
    should implement, ensuring consistent patterns across the codebase.

    Attributes:
        logger: Logging instance for the service
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service resources.

        This method should be called before using the service to ensure
        all required resources are properly set up.

        Raises:
            AudioServiceError: If initialization fails

        Example:
            ```python
            service = TranscriptionService()
            service.initialize()
            ```
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate service configuration.

        Args:
            config: Configuration dictionary with service options

        Returns:
            bool: True if configuration is valid, False otherwise

        Example:
            ```python
            config = {"model": "small", "language": "en"}
            is_valid = service.validate_config(config)
            ```
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Release resources used by the service.

        This method should be called when the service is no longer needed
        to ensure proper resource cleanup.

        Example:
            ```python
            service.cleanup()
            ```
        """
        pass
