"""Dependency injection container for the audio application.

This module provides a centralized dependency injection container
for managing service instances and their dependencies.
"""

import logging
from typing import Any, Dict, Optional, TypeVar, Type, cast

from services.implementations.audio_service_impl import AudioRecordingService
from services.implementations.configuration_manager_impl import ConfigurationManager
from services.implementations.file_service_impl import FileService
from services.implementations.platform_service_impl import PlatformDetectionService
from services.implementations.transcription_service_impl import TranscriptionService

from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import IConfigurationManager
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import IPlatformDetectionService
from services.interfaces.transcription_service_interface import ITranscriptionService

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """Dependency injection container.
    
    This class manages the creation and resolution of service dependencies
    throughout the application, ensuring proper initialization and lifecycle.
    """
    
    def __init__(self) -> None:
        """Initialize the dependency injection container."""
        self._services: Dict[str, Any] = {}
        self._config: Optional[Dict[str, Any]] = None
        
    def configure(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Configure the container with application settings.
        
        Args:
            config: Optional configuration dictionary
        """
        self._config = config
        
    def register(self, interface: Type[T], implementation: Any) -> None:
        """Register a service implementation for a given interface.
        
        Args:
            interface: The interface type to register
            implementation: The implementation instance to use
        """
        self._services[interface.__name__] = implementation
        logger.debug(f"Registered service: {interface.__name__}")
        
    def resolve(self, interface: Type[T]) -> T:
        """Resolve a service implementation for a given interface.
        
        Args:
            interface: The interface type to resolve
            
        Returns:
            An instance of the registered implementation
            
        Raises:
            KeyError: If no implementation is registered for the interface
        """
        if interface.__name__ not in self._services:
            raise KeyError(f"No implementation registered for {interface.__name__}")
            
        return cast(T, self._services[interface.__name__])
        
    def initialize_services(self) -> None:
        """Initialize all registered services in the container.
        
        This method sets up the default service implementations and their dependencies.
        """
        # Create configuration manager first
        config_manager = ConfigurationManager(self._config)
        self.register(IConfigurationManager, config_manager)
        
        # Create file service
        file_service = FileService()
        self.register(IFileService, file_service)
        
        # Create platform service
        platform_service = PlatformDetectionService()
        self.register(IPlatformDetectionService, platform_service)
        
        # Create audio recording service with its dependencies
        audio_service = AudioRecordingService(platform_service, file_service)
        self.register(IAudioRecordingService, audio_service)
        
        # Create transcription service with its dependencies
        transcription_service = TranscriptionService(file_service)
        self.register(ITranscriptionService, transcription_service)
        
        logger.info("All services initialized")


# Create a global container instance for the application
container = DIContainer()