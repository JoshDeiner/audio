"""Updated application bootstrapper for dependency injection configuration.

This module provides a more comprehensive bootstrapper that registers all service implementations.
"""

import logging
from typing import Any, Dict, Optional

from dependency_injection.container_enhanced import DIContainer, ServiceLifetime

# Import all interfaces
from services.interfaces.audio_service_interface import IAudioRecordingService
from services.interfaces.configuration_manager_interface import IConfigurationManager
from services.interfaces.file_service_interface import IFileService
from services.interfaces.platform_service_interface import IPlatformDetectionService
from services.interfaces.transcription_service_interface import ITranscriptionService
from services.interfaces.text_to_speech_service_interface import ITextToSpeechService
from services.interfaces.audio_playback_service_interface import IAudioPlaybackService
from services.interfaces.application_service_interface import IApplicationService
from services.interfaces.file_transcription_service_interface import IFileTranscriptionService

# Import all implementations
from services.implementations.audio_service_impl import AudioRecordingService
from services.implementations.configuration_manager_impl import ConfigurationManager
from services.implementations.file_service_impl import FileService
from services.implementations.platform_service_impl import PlatformDetectionService
from services.implementations.transcription_service_impl import TranscriptionService
from services.implementations.text_to_speech_service_impl import TextToSpeechService
from services.implementations.audio_playback_service_impl import AudioPlaybackService
from services.implementations.application_service_impl import ApplicationService
from services.implementations.file_transcription_service_impl import FileTranscriptionService

from plugins.plugin_manager_refactored import PluginManager
from dependency_injection.plugin_provider import PluginProvider

logger = logging.getLogger(__name__)


def bootstrap_application(container: DIContainer, config: Optional[Dict[str, Any]] = None) -> None:
    """Bootstrap the application with DI configuration.
    
    Args:
        container: DI container to configure
        config: Optional application configuration
    """
    # Configure the container with application settings
    container.configure(config)
    
    # Register services with their implementations
    
    # Core services
    container.register(
        IConfigurationManager, 
        ConfigurationManager, 
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        IPlatformDetectionService,
        PlatformDetectionService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        IFileService,
        FileService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    # Audio Services
    container.register(
        IAudioRecordingService,
        AudioRecordingService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        ITranscriptionService,
        TranscriptionService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        ITextToSpeechService,
        TextToSpeechService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        IAudioPlaybackService,
        AudioPlaybackService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    # Application services
    container.register(
        IApplicationService,
        ApplicationService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    container.register(
        IFileTranscriptionService,
        FileTranscriptionService,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    # Create plugin provider
    config_manager = container.resolve(IConfigurationManager)
    plugin_provider = PluginProvider(config_manager)
    plugin_provider.initialize()
    container.register(
        PluginProvider,
        implementation=plugin_provider,
        lifetime=ServiceLifetime.SINGLETON
    )
    
    logger.info("Application bootstrapped with all service registrations")


def cleanup_container(container: DIContainer) -> None:
    """Clean up resources held by services in the container.
    
    Args:
        container: The DI container to clean up
    """
    # Get plugin manager and clean up plugins
    plugin_manager = PluginManager.get_instance()
    if plugin_manager:
        plugin_manager.cleanup()
    
    logger.info("Container resources cleaned up")