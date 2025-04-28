"""Application bootstrapper for dependency injection configuration.

This module provides a bootstrapper for configuring the dependency injection
container with all application services.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar

from library.bin.dependency_injection.container import (
    DIContainer,
    ServiceLifetime,
)
from library.bin.dependency_injection.module_loader import (
    auto_register_services,
)
from library.bin.dependency_injection.plugin_provider import PluginProvider
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


class Bootstrapper:
    """Application bootstrapper for dependency injection.

    This class configures the DI container with all required services,
    either manually or through auto-discovery.
    """

    def __init__(self, container: DIContainer) -> None:
        """Initialize the bootstrapper.

        Args:
            container: DI container to configure
        """
        self.container = container

    def bootstrap(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Bootstrap the application with DI configuration.

        Args:
            config: Optional application configuration
        """
        # Configure the container with application settings
        self.container.configure(config)

        # Register core services manually
        self._register_core_services()

        # Auto-register additional services
        self._auto_register_services()

        logger.info("Application bootstrapped with DI container")

    def _register_core_services(self) -> None:
        """Register core application services manually."""
        # Create and register configuration manager
        config_manager = ConfigurationManager(self.container._config)
        self.container.register(
            IConfigurationManager,
            implementation=config_manager,
            lifetime=ServiceLifetime.SINGLETON,
        )

        # Create and register plugin provider
        plugin_provider = PluginProvider(config_manager)
        plugin_provider.initialize()
        self.container.register(
            PluginProvider,
            implementation=plugin_provider,
            lifetime=ServiceLifetime.SINGLETON,
        )

        # Register platform service
        self.container.register(
            IPlatformDetectionService,
            PlatformDetectionService,
            lifetime=ServiceLifetime.SINGLETON,
        )

        # Register file service
        self.container.register(
            IFileService, FileService, lifetime=ServiceLifetime.SINGLETON
        )

        # Register audio recording service
        # Dependencies will be auto-resolved
        self.container.register(
            IAudioRecordingService,
            AudioRecordingService,
            lifetime=ServiceLifetime.SINGLETON,
        )

        # Register transcription service
        # Dependencies will be auto-resolved
        self.container.register(
            ITranscriptionService,
            TranscriptionService,
            lifetime=ServiceLifetime.SINGLETON,
        )

    def _auto_register_services(self) -> None:
        """Auto-register services from annotated modules."""
        # Packages to scan for @Injectable services
        packages = [
            "services.implementations",
            "services.factories",
            "audio.utilities",
            # Add other packages here
        ]

        # Register services from these packages
        results = auto_register_services(self.container, packages)

        logger.info(
            f"Auto-registered {results['interfaces']} interfaces and "
            f"{results['implementations']} implementations from {results['modules']} modules"
        )

    def get_factory(self, service_type: Type[T]) -> Any:
        """Get a factory function for a service.

        Args:
            service_type: Type of service to get factory for

        Returns:
            Factory function for the service
        """
        return self.container.factory(service_type)


# Create a bootstrapper for the global container
bootstrapper = Bootstrapper(DIContainer())


def bootstrap_application(config: Optional[Dict[str, Any]] = None) -> None:
    """Bootstrap the application with DI configuration.

    Args:
        config: Optional application configuration
    """
    bootstrapper.bootstrap(config)
