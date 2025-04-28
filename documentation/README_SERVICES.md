# Audio Application Service System

This guide explains the service system in the audio application, including how to create and consume services using our dependency injection framework.

## Service Architecture

The audio application uses a clean architecture approach with service interfaces and implementations to promote loose coupling and testability.

### Key Components

1. **Service Interfaces**: Define contracts for functionality
2. **Service Implementations**: Provide concrete implementations of interfaces
3. **Dependency Injection Container**: Manages service instantiation and dependencies
4. **Service Provider**: Provides a clean API for accessing services

## Creating a New Service

### 1. Define the Interface

Create a new interface in `services/interfaces/` that defines the contract for your service:

```python
# services/interfaces/my_new_service_interface.py
from abc import ABC, abstractmethod

class IMyNewService(ABC):
    """Interface for my new service."""

    @abstractmethod
    def process_data(self, input_data: str) -> str:
        """Process some data.

        Args:
            input_data: The data to process

        Returns:
            The processed data
        """
        pass
```

### 2. Create the Implementation

Create a concrete implementation in `services/implementations/` that fulfills the interface contract:

```python
# services/implementations/my_new_service_impl.py
from library.bin.dependency_injection.module_loader import Injectable
from services.interfaces.my_new_service_interface import IMyNewService
from services.interfaces.file_service_interface import IFileService

@Injectable(interface=IMyNewService, lifetime="SINGLETON")
class MyNewService(IMyNewService):
    """Implementation of my new service."""

    def __init__(self, file_service: IFileService) -> None:
        """Initialize with dependencies.

        Args:
            file_service: File service dependency
        """
        self.file_service = file_service

    def process_data(self, input_data: str) -> str:
        """Process the input data.

        Args:
            input_data: The data to process

        Returns:
            The processed data
        """
        # Implementation using dependencies
        return f"Processed: {input_data}"
```

The `@Injectable` decorator automatically registers your service with the DI container.

### 3. Service Lifetime Options

When registering services, you can specify their lifetime:

- **SINGLETON**: One instance for the entire application
- **SCOPED**: One instance per scope (e.g., per request)
- **TRANSIENT**: New instance each time it's requested

Example:
```python
@Injectable(interface=IMyNewService, lifetime="SINGLETON")
```

## Consuming Services

### Standard Approach

Using the ServiceProvider's getter methods:

```python
from services.service_provider import ServiceProvider

# Get a service provider
provider = ServiceProvider(container)

# Get services using getter methods
file_service = provider.get_file_service()
my_service = provider.get_my_new_service()  # If you added a helper method

# Or using the generic get method
my_service = provider.get(IMyNewService)
```

### Enhanced Approach (Direct Property Access)

Our enhanced ServiceProvider allows accessing services via property notation:

```python
# Access services directly as properties
file_service = provider.file_service
my_service = provider.my_new_service

# No helper method needed for new services
```

### In Application Components

Services are injected through constructors:

```python
class MyComponent:
    def __init__(
        self,
        my_service: IMyNewService,
        file_service: IFileService
    ) -> None:
        self.my_service = my_service
        self.file_service = file_service

    def do_something(self, data: str) -> str:
        return self.my_service.process_data(data)
```

## Testing with Services

For unit tests, you can easily mock services:

```python
# Mock implementation
class MockMyService(IMyNewService):
    def process_data(self, input_data: str) -> str:
        return "MOCK: " + input_data

# In your test
def test_component():
    mock_service = MockMyService()
    mock_file_service = MockFileService()

    component = MyComponent(mock_service, mock_file_service)
    result = component.do_something("test")

    assert result == "MOCK: test"
```

## Registering Services Manually

If needed, you can register services manually:

```python
from library.bin.dependency_injection.container import ServiceLifetime

# Register a singleton
provider.register_singleton(IMyNewService, MyNewService)

# Register a transient service
provider.register_transient(IMyNewService, MyNewService)

# Register a scoped service
provider.register_scoped(IMyNewService, MyNewService)

# Register an instance directly
my_service_instance = MyNewService(file_service)
provider.register_instance(IMyNewService, my_service_instance)
```

## Creating Service Scopes

For operations that require their own service scope:

```python
# Create a parent service provider
root_provider = ServiceProvider(container)

# Create a scoped provider
request_scope = root_provider.create_scope()

# Get scoped services
scoped_service = request_scope.my_service
```

## Adding to AppServices

For core application services, you may need to add your service to the AppServices class:

```python
# In library/bin/dependency_injection/app_services.py
class AppServices:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        # Existing services...

        # Add your new service
        self.my_new_service = MyNewService(self.file_service)

    def get(self, service_type: Type[T]) -> T:
        service_map = {
            # Existing mappings...

            # Add your service mappings
            IMyNewService: self.my_new_service,
            MyNewService: self.my_new_service,
        }
        # ...
```

## Benefits of Our Service Architecture

1. **Modular Design**: Services are self-contained and focused on specific responsibilities
2. **Testability**: Clean interfaces make mocking dependencies straightforward
3. **Flexibility**: Implementations can be changed without affecting consumers
4. **Maintainability**: Dependencies are explicit and code is more readable
5. **Consistency**: Standard patterns for service creation and consumption
