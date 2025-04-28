"""Simple service container with constructor injection.

This module provides a streamlined approach to dependency injection for
prototyping, replacing the more complex enterprise-grade DI container.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar

from services.implementations.audio_service_impl import AudioRecordingService
from services.implementations.configuration_manager_impl import ConfigurationManager
from services.implementations.file_service_impl import FileService
from services.implementations.platform_service_impl import PlatformDetectionService
from services.implementations.text_to_speech_service_impl import TextToSpeechService
from services.implementations.transcription_service_impl import TranscriptionService
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import IConfigurationManager
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import IPlatformDetectionService
from services.interfaces.text_to_speech_service_interface import ITextToSpeechService
from services.interfaces.transcription_service_interface import ITranscriptionService

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AppServices:
    """Simple service container with constructor injection.
    
    This class provides a streamlined approach to dependency injection
    for prototype development, with direct initialization and optional
    dependencies for easier testing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the service container with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        # Direct initialization with configuration
        self.config = config or {}
        
        # Core services
        self.config_manager = ConfigurationManager(self.config)
        self.file_service = FileService()
        self.platform_service = PlatformDetectionService()
        
        # Services with dependencies
        self.audio_service = AudioRecordingService(self.platform_service, self.file_service)
        self.transcription_service = TranscriptionService(self.file_service)
        self.text_to_speech_service = TextToSpeechService()
    
    def get(self, service_type: Type[T]) -> T:
        """Simple service location for testing/overrides.
        
        Args:
            service_type: Type of service to resolve
            
        Returns:
            An instance of the requested service
            
        Raises:
            KeyError: If service is not registered
        """
        service_map = {
            IConfigurationManager: self.config_manager,
            ConfigurationManager: self.config_manager,
            
            IFileService: self.file_service,
            FileService: self.file_service,
            
            IPlatformDetectionService: self.platform_service,
            PlatformDetectionService: self.platform_service,
            
            IAudioRecordingService: self.audio_service,
            AudioRecordingService: self.audio_service,
            
            ITranscriptionService: self.transcription_service,
            TranscriptionService: self.transcription_service,
            
            ITextToSpeechService: self.text_to_speech_service,
            TextToSpeechService: self.text_to_speech_service,
        }
        
        if service_type not in service_map:
            raise KeyError(f"No service of type {service_type.__name__} is registered")
        
        return service_map[service_type]  # type: ignore
    
    def register_instance(self, service_type: Type[T], instance: Any) -> None:
        """Register a service instance for testing/mocking.
        
        Args:
            service_type: Type of service to register
            instance: Service instance to register
        """
        if service_type == IConfigurationManager or service_type == ConfigurationManager:
            self.config_manager = instance
        elif service_type == IFileService or service_type == FileService:
            self.file_service = instance
        elif service_type == IPlatformDetectionService or service_type == PlatformDetectionService:
            self.platform_service = instance
        elif service_type == IAudioRecordingService or service_type == AudioRecordingService:
            self.audio_service = instance
        elif service_type == ITranscriptionService or service_type == TranscriptionService:
            self.transcription_service = instance
        elif service_type == ITextToSpeechService or service_type == TextToSpeechService:
            self.text_to_speech_service = instance
        else:
            logger.warning(f"Unrecognized service type: {service_type.__name__}")

# Create a global instance for easy access
app_services = AppServices()