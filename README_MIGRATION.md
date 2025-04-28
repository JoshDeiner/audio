# Dependency Injection Migration Guide

This document provides instructions for migrating to the new dependency injection pattern.

## How to Migrate

To use the new dependency injection system, follow these steps:

### Step 1: Update Your Main Entry Point

Replace your existing main entry point with the DI-enabled version:

```bash
# Use the DI-enabled main entry point
python -m audio.__main__di
```

The DI-enabled main entry point will:
1. Bootstrap the DI container
2. Register all services with their implementations
3. Resolve dependencies automatically
4. Use the Application class as the composition root

### Step 2: Create New Services

When creating new services:

1. Define an interface in `services/interfaces/`
2. Implement the service in `services/implementations/`
3. Register the service in `dependency_injection/bootstrap_updated.py`

Example interface:
```python
from abc import ABC, abstractmethod

class IMyService(ABC):
    @abstractmethod
    def do_something(self) -> str:
        pass
```

Example implementation:
```python
from dependency_injection.module_loader import Injectable
from services.interfaces.my_service_interface import IMyService

@Injectable(interface=IMyService)
class MyService(IMyService):
    def __init__(self, dependency: IDependency) -> None:
        self.dependency = dependency
        
    def do_something(self) -> str:
        return f"Did something with {self.dependency.name}"
```

### Step 3: Update Controllers and Components

Update your controllers to use constructor injection:

```python
class MyController:
    def __init__(
        self,
        config: Dict[str, Any],
        service1: IService1,
        service2: IService2
    ) -> None:
        self.config = config
        self.service1 = service1
        self.service2 = service2
```

### Step 4: Resolve Dependencies

Use the ServiceProvider to get services:

```python
from services.service_provider_enhanced import ServiceProvider

# Create a service provider
service_provider = ServiceProvider(container)

# Get services
service1 = service_provider.get(IService1)
service2 = service_provider.get(IService2)
```

## Key Files

- `/audio/application_enhanced.py` - Enhanced application with DI
- `/audio/__main__di.py` - DI-enabled main entry point
- `/audio/utilities/argument_parser_di.py` - DI-enabled argument parser
- `/dependency_injection/bootstrap_updated.py` - Updated bootstrap with all services
- `/services/service_provider_enhanced.py` - Enhanced service provider

## Testing with DI

The DI system makes testing much easier:

```python
def test_my_controller():
    # Create mock dependencies
    mock_service1 = MockService1()
    mock_service2 = MockService2()
    
    # Create controller with mock dependencies
    controller = MyController({}, mock_service1, mock_service2)
    
    # Test methods
    result = controller.do_something()
    assert result == "expected result"
```

## Benefits

1. **Testability**: Easy to replace real implementations with mocks
2. **Modularity**: Components are decoupled from their dependencies
3. **Maintainability**: Dependencies are explicit in constructor signatures
4. **Flexibility**: Implementation can be changed without affecting clients