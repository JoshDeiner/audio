"""Base service interface for audio application."""

from abc import ABC, abstractmethod


class IBaseService(ABC):
    """Interface for all services in the audio application.

    This interface defines the common methods that all service classes
    should implement to ensure consistent behavior across the application.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the service.

        This method should be called before using the service to ensure proper setup.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the service.

        This method should be called when the service is no longer needed.
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the service is initialized.

        Returns:
            bool: True if the service is initialized, False otherwise
        """
        pass
