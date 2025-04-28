# Dependency Injection Issues in the Codebase

## 1. Hard-coded Dependencies in Services

### TranscriptionService (services/transcription_service.py)
- Line 22: `self.file_service = FileService()` - Direct instantiation of FileService within constructor
- No ability to inject mocks or alternative implementations for testing

### TranscriptionService Refactored (services/transcription_service_refactored.py)
- Line 33: `self.file_service = FileService()` - Still directly instantiating FileService
- Line 34: Uses `config_manager or ConfigurationManager` - Falls back to using ConfigurationManager directly

## 2. Hard-coded Dependencies in Controllers

### AudioPipelineController (audio/audio_pipeline_controller.py)
- Line 62-63: 
  ```python
  self.transcription_service = TranscriptionService()
  self.file_service = FileService()
  ```
- Direct instantiation of services in controller constructor
- Line 109: `recording_service = AudioRecordingService()` - Creating service instance inside method
- Line 291: `TextToSpeechService.synthesize` - Static method calls 
- Line 317: `AudioPlaybackService.play` - Static method calls with no DI
- Line 248 & 301: Static method calls to FileService with no DI

## 3. Singleton Pattern Overuse

### ServiceFactory (services/services_factory.py)
- Uses singleton pattern (Lines 29-40)
- Self-instantiates ConfigurationManager when not provided (Line 52)
- Creates a tightly coupled dependency to PluginManager (Line 53)

### PluginManager (plugins/plugin_manager.py)
- Uses singleton pattern (Lines 27-39)
- Self-instantiates ConfigurationManager when not provided (Line 51)

## 4. Tight Coupling Between Components

- Services directly instantiate dependencies rather than receiving them via constructor
- Concrete implementations are used instead of interfaces or abstract classes
- ServiceFactory creates specific service implementations directly with no interface abstraction
- Strong coupling between services and configuration management

## 5. Plugin System Issues

### PluginRegistry (plugins/plugin_base.py)
- Static design with class variables and methods
- Creates temporary plugin instances during registration (Line 92)
- No dependency injection in plugin instantiation (Line 136)

### PluginLoader (plugins/plugin_loader.py)
- Directly accesses ConfigurationManager (Line 58)
- Uses hardcoded plugin base classes (Lines 29-34)
- Tight coupling to PluginRegistry

## 6. Global Configuration Access

- Many classes directly access ConfigurationManager
- No consistent dependency injection for configuration
- Environment variables accessed directly in multiple places

## 7. No Clear Service Interfaces

- Base classes exist (BaseService) but are not consistently used
- No clear separation between interface and implementation
- Inconsistent inheritance patterns

## 8. Missing Factory Method Patterns

- Direct instantiation instead of using factories consistently
- ServiceFactory exists but isn't used uniformly throughout codebase
- Static methods used instead of proper instantiation and DI

## Recommendations

1. Use constructor dependency injection consistently across all services
2. Create interfaces for all services and implement against those interfaces
3. Use a proper DI container instead of singletons and static methods
4. Eliminate direct instantiation of dependencies within classes
5. Make service factories the single source for creating service instances
6. Use interface-based design for better testability and loose coupling
7. Inject configuration rather than accessing it directly
8. Create a more modular design where components can be replaced without changing other code