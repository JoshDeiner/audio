# Environment Variable Refactoring

This document outlines the approach for refactoring direct environment variable access in the application to use a centralized configuration management system.

## Problem Statement

The application currently has the following issues related to environment variables:

1. Direct environment variable access scattered throughout multiple services
2. Inconsistent default values when environment variables are not present
3. No central location for configuration documentation
4. No validation of configuration values
5. Difficulty in testing services due to environment dependencies

## Solution Approach

We've implemented a centralized `ConfigurationManager` class to address these issues:

1. **Centralized Configuration Access**: All configuration values are accessed through a single API
2. **Default Value Management**: Default values are defined once in a central location
3. **Configuration from Multiple Sources**: Values can come from environment variables, config files, or be set programmatically
4. **Directory Management**: Automatic creation of required directories
5. **Dependency Injection**: Services can be provided with a configuration manager for testing

## Implementation Details

### 1. ConfigurationManager Class

Located at `/config/configuration_manager.py`:

```python
class ConfigurationManager:
    """Centralized configuration manager for the audio application."""

    # Default configuration values
    _defaults = {
        # Paths
        "AUDIO_INPUT_DIR": "input",
        "AUDIO_OUTPUT_DIR": "output",

        # Whisper configuration
        "WHISPER_MODEL": "tiny",
        "WHISPER_COMPUTE_TYPE": "int8",
        "WHISPER_DEVICE": "cpu",

        # Platform configuration
        "AUDIO_DRIVER": "",
        "PLATFORM": "",
    }

    # Configuration store
    _config: Dict[str, Any] = {}

    @classmethod
    def initialize(cls, config_file: Optional[str] = None) -> None:
        """Initialize configuration from environment variables and optional config file."""
        # Implementation here...

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        # Implementation here...
```

### 2. Service Refactoring

Services have been refactored to:

1. Accept `ConfigurationManager` through constructor dependency injection
2. Replace direct `os.environ.get()` calls with `config_manager.get()`
3. Convert static methods to instance methods where configuration is needed

Example from TranscriptionService:

```python
def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
    """Initialize the transcription service."""
    self.file_service = FileService()
    self.config_manager = config_manager or ConfigurationManager

def _get_whisper_model_config(self, model_size: Optional[str] = None) -> Dict[str, str]:
    """Get Whisper model configuration."""
    # Get model size from config or use provided value
    if not model_size:
        model_size = self.config_manager.get("WHISPER_MODEL", "tiny")

    # Validate model size
    valid_sizes = ["tiny", "base", "small", "medium", "large"]
    if model_size not in valid_sizes:
        logger.warning(f"Invalid model size: {model_size}. Using 'tiny' instead.")
        model_size = "tiny"

    # Get compute type and device from config
    compute_type = self.config_manager.get("WHISPER_COMPUTE_TYPE", "int8")
    device = self.config_manager.get("WHISPER_DEVICE", "cpu")

    return {
        "model_size": model_size,
        "compute_type": compute_type,
        "device": device,
    }
```

### 3. Application Startup

The main application entry point now initializes the configuration manager:

```python
def main():
    # Initialize configuration
    config_file = "config/audio_config.env"
    ConfigurationManager.initialize(config_file)

    # Rest of the application startup
```

### 4. BaseService Enhancement

An enhanced BaseService class has been created with built-in configuration management:

```python
class BaseService(ABC):
    """Abstract base class for services."""

    def __init__(self, config_manager: Optional[ConfigurationManager] = None) -> None:
        """Initialize the base service."""
        self.config_manager = config_manager or ConfigurationManager
        self._initialized = False

    # Rest of the class implementation...
```

## Benefits

1. **Testability**: Services can be tested with mock configuration
2. **Consistency**: Default values defined in a single location
3. **Maintainability**: Configuration changes only need to be made in one place
4. **Flexibility**: Configuration can be loaded from files or set programmatically
5. **Runtime modifications**: Configuration can be updated during runtime if needed

## Future Improvements

1. **Configuration Validation**: Add type checking and validation for configuration values
2. **Configuration Categories**: Group related configuration settings
3. **Change Notifications**: Allow services to subscribe to configuration changes
4. **Protected Values**: Support for sensitive configuration values
5. **Configuration Profiles**: Support for different configuration profiles (dev, test, prod)
