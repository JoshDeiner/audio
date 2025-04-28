"""Sample code demonstrating the dependency injection pattern.

This file shows practical examples of how to use the DI system in various scenarios.
"""

import asyncio
from typing import Dict

# Import controllers and other components
from audio.audio_pipeline_controller import AudioPipelineController

# Import DI components
from dependency_injection.bootstrap import bootstrap_application
from dependency_injection.container import (
    DIContainer,
    ServiceLifetime,
)

# Import interfaces
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
from services.service_provider import ServiceProvider


# Sample 1: Basic DI setup and service resolution
def basic_di_example():
    """Basic example of setting up DI and resolving services."""
    # Initialize the container
    container = DIContainer()

    # Bootstrap the application (registers all services)
    bootstrap_application()

    # Create a service provider
    service_provider = ServiceProvider(container)

    # Get services by specific accessor methods
    file_service = service_provider.get_file_service()
    audio_service = service_provider.get_audio_recording_service()

    # Get services by generic interface
    transcription_service = service_provider.get(ITranscriptionService)

    # Use the services
    print(f"File service: {file_service}")
    print(f"Audio service: {audio_service}")
    print(f"Transcription service: {transcription_service}")

    return service_provider


# Sample 2: Using DI in a controller
async def controller_example(
    service_provider: ServiceProvider, args: Dict[str, str]
):
    """Example of using DI with a controller."""
    # Get the required services
    config_manager = service_provider.get_config_manager()
    transcription_service = service_provider.get_transcription_service()
    file_service = service_provider.get_file_service()
    audio_service = service_provider.get_audio_recording_service()

    # Create controller with injected dependencies
    controller = AudioPipelineController(
        args,
        config_manager,
        transcription_service,
        file_service,
        audio_service,
    )

    # Use the controller
    transcription = await controller.handle_audio_in()
    print(f"Transcription result: {transcription}")


# Sample 3: Service registration
def service_registration_example():
    """Example of registering services with different lifetimes."""
    container = DIContainer()

    # Register a singleton service (one instance for the entire application)
    container.register(
        IConfigurationManager,
        implementation_type=MockConfigManager,
        lifetime=ServiceLifetime.SINGLETON,
    )

    # Register a transient service (new instance each time resolved)
    container.register(
        IFileService,
        implementation_type=MockFileService,
        lifetime=ServiceLifetime.TRANSIENT,
    )

    # Register a scoped service (one instance per scope)
    container.register(
        ITranscriptionService,
        implementation_type=MockTranscriptionService,
        lifetime=ServiceLifetime.SCOPED,
    )

    # Register a service with a factory function
    container.register(
        IPlatformDetectionService,
        factory=lambda c: MockPlatformService(
            c.resolve(IConfigurationManager)
        ),
        lifetime=ServiceLifetime.SINGLETON,
    )

    # Create a service provider
    service_provider = ServiceProvider(container)
    return service_provider


# Sample 4: Scoped services
def scoped_services_example(service_provider: ServiceProvider):
    """Example of using scoped services."""
    # Root provider has its own set of scoped services
    root_scoped_service = service_provider.get(ITranscriptionService)

    # Create a new scope for a request
    request_scope = service_provider.create_scope()

    # This is a different instance than root_scoped_service
    request_scoped_service = request_scope.get(ITranscriptionService)

    # Singletons are the same across scopes
    root_singleton = service_provider.get(IConfigurationManager)
    request_singleton = request_scope.get(IConfigurationManager)

    print(f"Root scoped service: {root_scoped_service}")
    print(f"Request scoped service: {request_scoped_service}")
    print(
        f"Same instance? {root_scoped_service is request_scoped_service}"
    )  # False

    print(f"Root singleton: {root_singleton}")
    print(f"Request singleton: {request_singleton}")
    print(f"Same instance? {root_singleton is request_singleton}")  # True


# Sample mock implementations for the examples
class MockConfigManager:
    def __init__(self):
        self.config = {"mock": True}

    def get(self, key, default=None):
        return self.config.get(key, default)


class MockFileService:
    def __init__(self):
        pass

    def read_text(self, file_path):
        return f"Mock content from {file_path}"


class MockTranscriptionService:
    def __init__(self, file_service: IFileService = None):
        self.file_service = file_service

    def transcribe_audio(self, audio_path, model_size=None, language=None):
        return f"Mock transcription of {audio_path}"


class MockPlatformService:
    def __init__(self, config_manager: IConfigurationManager):
        self.config_manager = config_manager

    def get_platform(self):
        return "mock-platform"


# Entry point
async def main():
    print("DI Sample 1: Basic DI Example")
    service_provider = basic_di_example()
    print()

    print("DI Sample 2: Controller Example")
    args = {"duration": "5", "model": "tiny"}
    try:
        await controller_example(service_provider, args)
    except Exception as e:
        print(f"Controller example failed: {e}")
    print()

    print("DI Sample 3: Service Registration")
    custom_provider = service_registration_example()
    print()

    print("DI Sample 4: Scoped Services")
    scoped_services_example(custom_provider)
    print()


if __name__ == "__main__":
    asyncio.run(main())
