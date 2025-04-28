"""Enhanced service provider for the audio application.

This module provides a scoped, interface-based approach to service creation and management,
completely replacing the ServiceFactory singleton with proper dependency injection.
"""

import logging
from typing import Any, Dict, Optional, TypeVar, Type, cast

from dependency_injection.container_enhanced import DIContainer, Scope, ServiceLifetime
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import IConfigurationManager
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import IPlatformDetectionService
from services.interfaces.transcription_service_interface import ITranscriptionService

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceProvider:
    """Provider for creating and accessing service implementations.
    
    This class serves as a facade for the DIContainer, providing a clean API
    for resolving service dependencies with proper scoping and lifecycle management.
    """
    
    def __init__(
        self, 
        di_container: DIContainer,
        parent_scope: Optional[Scope] = None
    ) -> None:
        """Initialize the service provider.
        
        Args:
            di_container: Dependency injection container
            parent_scope: Optional parent scope for nested scoping
        """
        self.container = di_container
        self.scope = parent_scope or di_container.create_scope()
        
    def create_scope(self) -> 'ServiceProvider':
        """Create a new scoped service provider.
        
        Returns:
            A new service provider with its own scope
        """
        return ServiceProvider(self.container, self.container.create_scope())
        
    def get_config_manager(self) -> IConfigurationManager:
        """Get the configuration manager service.
        
        Returns:
            Configuration manager implementation
        """
        return self.scope.resolve(IConfigurationManager)
        
    def get_file_service(self) -> IFileService:
        """Get the file service.
        
        Returns:
            File service implementation
        """
        return self.scope.resolve(IFileService)
        
    def get_transcription_service(self) -> ITranscriptionService:
        """Get the transcription service.
        
        Returns:
            Transcription service implementation
        """
        return self.scope.resolve(ITranscriptionService)
        
    def get_audio_recording_service(self) -> IAudioRecordingService:
        """Get the audio recording service.
        
        Returns:
            Audio recording service implementation
        """
        return self.scope.resolve(IAudioRecordingService)
        
    def get_platform_service(self) -> IPlatformDetectionService:
        """Get the platform detection service.
        
        Returns:
            Platform detection service implementation
        """
        return self.scope.resolve(IPlatformDetectionService)
        
    def get(self, service_type: Type[T]) -> T:
        """Generic method to get any registered service by interface.
        
        Args:
            service_type: The interface type to resolve
            
        Returns:
            An instance of the registered implementation
            
        Raises:
            KeyError: If no implementation is registered for the interface
        """
        return self.scope.resolve(service_type)
        
    def get_factory(self, service_type: Type[T]) -> Any:
        """Get a factory function for creating service instances.
        
        Args:
            service_type: Type of service to create factory for
            
        Returns:
            Factory function that creates instances of the service
        """
        return self.container.factory(service_type)
        
    def register_instance(
        self, service_type: Type[T], instance: Any
    ) -> None:
        """Register an instance with the container.
        
        Args:
            service_type: Type of service to register
            instance: Instance to register
        """
        self.container.register(
            service_type, 
            implementation=instance,
            lifetime=ServiceLifetime.SINGLETON
        )
        
    def register_transient(
        self, service_type: Type[T], implementation_type: Type
    ) -> None:
        """Register a transient service with the container.
        
        Args:
            service_type: Type of service to register
            implementation_type: Implementation type to register
        """
        self.container.register(
            service_type,
            implementation_type,
            lifetime=ServiceLifetime.TRANSIENT
        )
        
    def register_scoped(
        self, service_type: Type[T], implementation_type: Type
    ) -> None:
        """Register a scoped service with the container.
        
        Args:
            service_type: Type of service to register
            implementation_type: Implementation type to register
        """
        self.container.register(
            service_type,
            implementation_type,
            lifetime=ServiceLifetime.SCOPED
        )
        
    def register_singleton(
        self, service_type: Type[T], implementation_type: Type
    ) -> None:
        """Register a singleton service with the container.
        
        Args:
            service_type: Type of service to register
            implementation_type: Implementation type to register
        """
        self.container.register(
            service_type,
            implementation_type,
            lifetime=ServiceLifetime.SINGLETON
        )