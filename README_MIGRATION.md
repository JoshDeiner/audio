# Dependency Injection Migration Guide

This document provides instructions for migrating to the simplified dependency injection pattern.

## Simplified vs. Enterprise DI

This project now supports two approaches to dependency injection:

1. **Enterprise DI (Original)**: Full-featured DI with interface/implementation separation,
   complex container, and formal lifecycle management. Suitable for large teams and complex applications.

2. **Simplified DI (New)**: Streamlined approach with direct service initialization,
   optional dependencies, and minimal configuration. Suitable for prototyping and smaller applications.

## How to Migrate to Simplified DI

To use the simplified dependency injection system, follow these steps:

### Step 1: Use the Simplified AppServices Container

```python
from dependency_injection.app_services import AppServices

# Create services with optional configuration
config = {"WHISPER_MODEL": "tiny", "DEBUG": True}
services = AppServices(config)

# Access services directly
file_service = services.file_service
transcription_service = services.transcription_service
```

### Step 2: Create New Services with Optional Dependencies

When creating new services, make dependencies optional with default instantiation:

```python
class MyService:
    def __init__(self, dependency=None):
        # Use provided dependency or create a new instance
        self.dependency = dependency or Dependency()

    def do_something(self) -> str:
        return f"Did something with {self.dependency.name}"
```

### Step 3: Use Services in Controllers

Use constructor injection with direct service access:

```python
from dependency_injection.app_services import AppServices

class MyController:
    def __init__(
        self,
        config,
        service1,
        service2
    ):
        self.config = config
        self.service1 = service1
        self.service2 = service2

    @classmethod
    def from_services(cls, config, services):
        # Factory method for easy creation from AppServices
        return cls(
            config,
            services.service1,
            services.service2
        )
```

### Step 4: For Legacy Code Using the Old DI System

Use the migration adapter to help transitioning:

```python
from dependency_injection.migration import create_adapter
from dependency_injection.app_services import AppServices

# Create AppServices
services = AppServices()

# Create an adapter that makes AppServices look like the old DIContainer
container_adapter = create_adapter(services)

# Legacy code can continue to use 'container_adapter' instead of 'container'
```

## Key Files for Simplified DI

- `/dependency_injection/app_services.py` - Core simplified service container
- `/audio/application.py` - Updated application using simplified DI
- `/plugins/simple_plugin_loader.py` - Simplified plugin loading system
- `/dependency_injection/migration.py` - Utilities for transitioning from complex to simplified DI
- `/samples/simplified_di_usage.py` - Sample code showing simplified DI usage

## Testing with Simplified DI

The simplified DI system makes testing even easier:

```python
def test_my_controller():
    # Create AppServices with mock implementations
    services = AppServices()

    # Register mock services
    services.register_instance(Service1, MockService1())
    services.register_instance(Service2, MockService2())

    # Create controller with mock services
    controller = MyController.from_services({}, services)

    # Test methods
    result = controller.do_something()
    assert result == "expected result"
```

## Benefits of Simplified DI

1. **Faster Development**: Fewer files to modify when making changes
2. **Easier Onboarding**: Simpler architecture for new developers to understand
3. **Maintained Testability**: Still supports mocking and testing
4. **Reduced Complexity**: Less boilerplate code
5. **Future Flexibility**: Can evolve to enterprise patterns as needed

## When to Use Enterprise DI

Consider using or returning to the enterprise DI approach when:

1. The team size grows beyond 3-5 developers
2. The codebase exceeds ~10k lines of code
3. Multiple deployment contexts require different implementations
4. Formal testing requirements emerge

For prototyping and small projects, the simplified DI approach provides most benefits
with significantly less overhead.
