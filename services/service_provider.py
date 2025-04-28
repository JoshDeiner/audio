"""Service provider for the audio application.

This module provides a cleaner, interface-based approach to service creation and management,
replacing the ServiceFactory singleton with proper dependency injection.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, cast

from dependency_injection import container
from dependency_injection.container import DIContainer
from plugins.plugin_manager import PluginManager
from services.implementations.audio_service_impl import AudioRecordingService
from services.implementations.configuration_manager_impl import (
    ConfigurationManager,
)
from services.implementations.file_service_impl import FileService
from services.implementations.platform_service_impl import (
    PlatformDetectionService,
)
from services.implementations.transcription_service_impl import (
    TranscriptionService,
)
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import (
    IConfigurationManager,
)
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import (
    IPlatformDetectionService,
)
from services.interfaces.transcription_service_interface import (
    ITranscriptionService,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceProvider:
    """Provider for creating and accessing service implementations.

    This class serves as a facade for the DIContainer, providing a clean API
    for resolving service dependencies and managing service lifecycles.
    """

    def __init__(self, di_container: Optional[DIContainer] = None) -> None:
        """Initialize the service provider.

        Args:
            di_container: Optional dependency injection container. If None, the global container is used.
        """
        self.container = di_container or container

    def configure(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Configure the service provider with application settings.

        Args:
            config: Optional configuration dictionary
        """
        # Configure the container
        self.container.configure(config)

        # Initialize the services
        self.container.initialize_services()

        logger.info("Service provider configured")

    def get_config_manager(self) -> IConfigurationManager:
        """Get the configuration manager service.

        Returns:
            Configuration manager implementation
        """
        return self.container.resolve(IConfigurationManager)

    def get_file_service(self) -> IFileService:
        """Get the file service.

        Returns:
            File service implementation
        """
        return self.container.resolve(IFileService)

    def get_transcription_service(self) -> ITranscriptionService:
        """Get the transcription service.

        Returns:
            Transcription service implementation
        """
        return self.container.resolve(ITranscriptionService)

    def get_audio_recording_service(self) -> IAudioRecordingService:
        """Get the audio recording service.

        Returns:
            Audio recording service implementation
        """
        return self.container.resolve(IAudioRecordingService)

    def get_platform_service(self) -> IPlatformDetectionService:
        """Get the platform detection service.

        Returns:
            Platform detection service implementation
        """
        return self.container.resolve(IPlatformDetectionService)

    def get(self, interface: Type[T]) -> T:
        """Generic method to get any registered service by interface.

        Args:
            interface: The interface type to resolve

        Returns:
            An instance of the registered implementation

        Raises:
            KeyError: If no implementation is registered for the interface
        """
        return self.container.resolve(interface)

    def cleanup(self) -> None:
        """Clean up and release all services."""
        # Clean up plugin manager resources if needed
        plugin_manager = PluginManager.get_instance()
        if plugin_manager:
            plugin_manager.cleanup()

        logger.info("Service provider cleaned up")


# Create a global service provider instance for convenience
# This is not a singleton - applications can create their own instances if needed
service_provider = ServiceProvider()
