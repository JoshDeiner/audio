"""Container configuration for the audio application.

This module provides the configuration for the dependency injection container,
registering all service implementations and their dependencies.
"""

import logging
from typing import Any, Dict, Optional

from library.bin.dependency_injection.container import DIContainer
from library.bin.dependency_injection.plugin_provider import PluginProvider
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


def configure_container(
    container: DIContainer, config: Optional[Dict[str, Any]] = None
) -> None:
    """Configure the dependency injection container with service registrations.

    Args:
        container: The DI container to configure
        config: Optional configuration dictionary
    """
    # Configure the container with application settings
    container.configure(config)

    # Create configuration manager first
    config_manager = ConfigurationManager(config)
    container.register(IConfigurationManager, config_manager)

    # Create plugin provider with configuration manager
    plugin_provider = PluginProvider(config_manager)
    plugin_provider.initialize()

    # Create file service
    file_service = FileService()
    container.register(IFileService, file_service)

    # Create platform service
    platform_service = PlatformDetectionService()
    container.register(IPlatformDetectionService, platform_service)

    # Create audio recording service with its dependencies
    audio_service = AudioRecordingService(platform_service, file_service)
    container.register(IAudioRecordingService, audio_service)

    # Create transcription service with its dependencies
    transcription_service = TranscriptionService(file_service)
    container.register(ITranscriptionService, transcription_service)

    logger.info("Container configured with all service registrations")


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
