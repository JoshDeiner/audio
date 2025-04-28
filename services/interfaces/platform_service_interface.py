"""Platform detection service interface for audio transcription tool."""

from abc import ABC, abstractmethod


class IPlatformDetectionService(ABC):
    """Interface for detecting platform and audio driver configuration."""

    @abstractmethod
    def get_platform(self) -> str:
        """Detect platform and audio driver configuration.

        This method determines the platform or audio driver to use for audio recording.
        It checks for environment variables first, then falls back to auto-detection.

        Returns:
            str: Identifier for the platform or audio driver.
        """
        pass