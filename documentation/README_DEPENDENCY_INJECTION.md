# Dependency Injection in the Audio Application

This guide explains the dependency injection (DI) system implemented in the audio application, which helps make the code more modular, testable, and maintainable.

## What is Dependency Injection?

Dependency injection is a design pattern that helps decouple components by having them declare their dependencies rather than creating them directly. In our application, this means services accept their dependencies through their constructors instead of instantiating them internally.

## Key Components

### 1. Service Interfaces

All services have interfaces defined in `services/interfaces/`:

```python
# services/interfaces/transcription_service_interface.py
from abc import ABC, abstractmethod

class ITranscriptionService(ABC):
    @abstractmethod
    def transcribe_audio(self, audio_file_path: str, model_size=None, language=None) -> str:
        pass
```

### 2. Service Implementations

Concrete implementations accept dependencies through their constructors:

```python
# services/implementations/transcription_service_impl.py
class TranscriptionService(ITranscriptionService):
    def __init__(self, file_service: IFileService) -> None:
        self.file_service = file_service
        
    def transcribe_audio(self, audio_file_path: str, model_size=None, language=None) -> str:
        # Implementation uses self.file_service rather than creating it
        ...
```

### 3. DI Container

The container manages services and their dependencies:

```python
# Creating and configuring the container
from dependency_injection.bootstrap import bootstrap_application
from dependency_injection.container_enhanced import DIContainer

# Bootstrap the application
container = DIContainer()
bootstrap_application()

# Get a service from the container
transcription_service = container.resolve(ITranscriptionService)
```

### 4. Service Provider

The service provider provides a convenient API for accessing services:

```python
from services.service_provider_enhanced import ServiceProvider

# Create a service provider
service_provider = ServiceProvider(container)

# Get services by interface
file_service = service_provider.get_file_service()
audio_service = service_provider.get_audio_recording_service()
```

## Using the DI System

### In Scripts & Main Application

```python
from audio.application import Application

# The Application class handles DI container setup
app = Application()
await app.initialize()
await app.run()
```

### In Controllers & Services

```python
class AudioPipelineController:
    def __init__(
        self,
        config: Dict[str, Any],
        config_manager: IConfigurationManager,
        transcription_service: ITranscriptionService,
        file_service: IFileService,
        audio_service: IAudioRecordingService,
    ) -> None:
        # Dependencies received through constructor
        self.config = config
        self.config_manager = config_manager
        self.transcription_service = transcription_service
        self.file_service = file_service
        self.audio_service = audio_service
```

### Creating Scopes

For request handling or other scenarios where scopes are needed:

```python
# Create a parent service provider
root_provider = ServiceProvider(container)

# Create a scoped provider for a specific request
request_scope = root_provider.create_scope()
scoped_service = request_scope.get(SomeServiceInterface)
```

## Registering Services

### Manual Registration

```python
container.register(
    ITranscriptionService,
    TranscriptionService,
    lifetime=ServiceLifetime.SINGLETON
)
```

### Using Decorators (Auto-Registration)

```python
from dependency_injection.module_loader import Injectable

@Injectable(interface=IFileService, lifetime=ServiceLifetime.SINGLETON)
class FileService(IFileService):
    def __init__(self) -> None:
        # Implementation
        pass
```

## Benefits

1. **Testability**: Easy to substitute mock implementations for tests
2. **Decoupling**: Components depend on abstractions, not concrete implementations
3. **Maintainability**: Dependencies are explicit in constructor signatures
4. **Flexibility**: Service implementations can be changed without modifying client code
5. **Lifetime Management**: The container handles creating and disposing services

## Advanced Features

- **Service Lifetimes**: Singleton, Scoped, and Transient services
- **Factory Methods**: For complex service creation
- **Auto-Discovery**: Register services by scanning modules
- **Scoping**: Group services for specific contexts or requests

For more details, see the full documentation in `/home/jd01/audio/dependency_injection_implementation.md`.