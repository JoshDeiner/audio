"""Base service class for audio application."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Abstract base class for services.

    This class defines the common interface and functionality for all services
    in the audio application.
    """

    def __init__(
        self, config_manager: Optional[ConfigurationManager] = None
    ) -> None:
        """Initialize the base service.

        Args:
            config_manager: Optional configuration manager instance
        """
        self.config_manager = config_manager or ConfigurationManager
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the service.

        This method should be called before using the service to ensure proper setup.
        It will be implemented by child classes to perform service-specific initialization.
        """
        if self._initialized:
            logger.debug(f"{self.__class__.__name__} already initialized")
            return

        self._do_initialization()
        self._initialized = True
        logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def _do_initialization(self) -> None:
        """Perform service-specific initialization.

        Subclasses must implement this method to initialize their specific resources.
        """
        pass

    def cleanup(self) -> None:
        """Clean up resources used by the service.

        This method should be called when the service is no longer needed.
        It will be implemented by child classes to perform service-specific cleanup.
        """
        if not self._initialized:
            logger.debug(
                f"{self.__class__.__name__} not initialized, nothing to clean up"
            )
            return

        self._do_cleanup()
        self._initialized = False
        logger.info(f"{self.__class__.__name__} cleaned up")

    def _do_cleanup(self) -> None:
        """Perform service-specific cleanup.

        Subclasses should override this method to clean up their specific resources.
        """
        pass

    def is_initialized(self) -> bool:
        """Check if the service is initialized.

        Returns:
            bool: True if the service is initialized, False otherwise
        """
        return self._initialized
