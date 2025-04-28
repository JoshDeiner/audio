# Dependency Injection Migration Guide

This guide shows how to migrate existing code to use the new dependency injection pattern.

## Code That Needs to Be Updated

The following files and components should be updated to use the new DI pattern:

1. **Entry Point (`__main__.py`)**: Update to use the Application class or ServiceProvider
2. **Controllers**: Update to accept dependencies through constructor
3. **Services**: Remove direct instantiation of dependencies
4. **Utilities**: Ensure utility classes accept dependencies where needed

## Before and After Examples

### 1. Main Entry Point

#### Before:

```python
# audio/__main__.py
async def handle_audio_in_command(args: Dict[str, str]) -> None:
    try:
        controller = AudioPipelineController(args)  # Direct instantiation
        transcription = await controller.handle_audio_in()
        print(f"\nTranscription result: {transcription}\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
```

#### After:

```python
# audio/__main___refactored.py
async def handle_audio_in_command(args: Dict[str, str]) -> None:
    try:
        # Get services from the DI container via service provider
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
            audio_service
        )
        
        transcription = await controller.handle_audio_in()
        print(f"\nTranscription result: {transcription}\n")
    except AudioServiceError as e:
        logger.error(f"Audio service error: {e}")
        print(f"Error: {e}")
```

### 2. Controllers

#### Before:

```python
# audio/audio_pipeline_controller.py
class AudioPipelineController:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.transcription_service = TranscriptionService()  # Direct instantiation
        self.file_service = FileService()  # Direct instantiation
```

#### After:

```python
# audio/audio_pipeline_controller_refactored.py
class AudioPipelineController:
    def __init__(
        self,
        config: Dict[str, Any],
        config_manager: IConfigurationManager,
        transcription_service: ITranscriptionService,
        file_service: IFileService,
        audio_service: IAudioRecordingService,
    ) -> None:
        self.config = config
        self.config_manager = config_manager
        self.transcription_service = transcription_service
        self.file_service = file_service
        self.audio_service = audio_service
```

### 3. Services

#### Before:

```python
# services/transcription_service.py
class TranscriptionService:
    def __init__(self) -> None:
        self.file_service = FileService()  # Direct instantiation

    def transcribe_audio(self, audio_file_path: str, ...) -> str:
        # Use self.file_service
```

#### After:

```python
# services/implementations/transcription_service_impl.py
class TranscriptionService(ITranscriptionService):
    def __init__(self, file_service: IFileService) -> None:
        self.file_service = file_service  # Dependency injection

    def transcribe_audio(self, audio_file_path: str, ...) -> str:
        # Use self.file_service
```

### 4. Factory Usage

#### Before:

```python
# Using ServiceFactory singleton
from services.services_factory import ServiceFactory

factory = ServiceFactory()
file_service = factory.create_file_service()
transcription_service = factory.create_transcription_service()
```

#### After:

```python
# Using dependency injection
from dependency_injection.bootstrap import bootstrap_application
from services.service_provider_enhanced import ServiceProvider

# Bootstrap the application
bootstrap_application()

# Create a service provider
service_provider = ServiceProvider(container)

# Get services by interface
file_service = service_provider.get_file_service()
transcription_service = service_provider.get_transcription_service()
```

## Steps to Migrate a File

1. **Identify Dependencies**: Determine what external services the component uses
2. **Add Interfaces**: Make sure interfaces exist for all dependencies
3. **Update Constructor**: Change constructor to accept dependencies
4. **Remove Direct Instantiation**: Replace with injected dependencies
5. **Update Callers**: Update all code that creates this component to provide dependencies

## Testing with DI

The DI pattern makes testing much easier:

```python
# Testing a controller with mocked dependencies
def test_audio_pipeline_controller():
    # Create mock dependencies
    mock_config_manager = MockConfigManager()
    mock_transcription_service = MockTranscriptionService()
    mock_file_service = MockFileService()
    mock_audio_service = MockAudioService()
    
    # Create controller with mock dependencies
    controller = AudioPipelineController(
        {"test": True},
        mock_config_manager,
        mock_transcription_service,
        mock_file_service,
        mock_audio_service
    )
    
    # Test controller methods with mocked dependencies
    result = await controller.handle_audio_in()
    assert result == "expected transcription"
```