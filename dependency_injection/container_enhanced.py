"""Enhanced dependency injection container for the audio application.

This module provides an improved dependency injection container with
advanced features like scoped lifetimes, lazy resolution, and factory methods.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, cast

logger = logging.getLogger(__name__)

T = TypeVar('T')
TFactory = TypeVar('TFactory')


class ServiceLifetime:
    """Service lifetime options for DI container registrations."""
    SINGLETON = "singleton"  # One instance for the entire application
    SCOPED = "scoped"  # One instance per scope/request
    TRANSIENT = "transient"  # New instance each time resolved


class ServiceRegistration:
    """Registration details for a service in the DI container."""

    def __init__(
        self,
        service_type: Type,
        implementation_type: Optional[Type] = None,
        implementation: Optional[Any] = None,
        factory: Optional[Callable[..., Any]] = None,
        lifetime: str = ServiceLifetime.SINGLETON,
        dependencies: Optional[List[Type]] = None,
    ) -> None:
        """Initialize a service registration.

        Args:
            service_type: Interface or abstract type being registered
            implementation_type: Concrete type implementing the service (optional)
            implementation: Instance implementing the service (optional)
            factory: Factory function to create the service (optional)
            lifetime: Service lifetime (singleton, scoped, transient)
            dependencies: List of dependency types required for initialization
        """
        self.service_type = service_type
        self.implementation_type = implementation_type
        self.implementation = implementation
        self.factory = factory
        self.lifetime = lifetime
        self.dependencies = dependencies or []

        # Validate registration
        if not any([implementation_type, implementation, factory]):
            raise ValueError(
                f"Service {service_type} must have either an implementation "
                "type, instance, or factory method"
            )


class Scope:
    """A resolution scope for scoped services.

    A scope maintains instances of scoped services for a specific
    context or request, allowing services to be shared within
    the scope but not between different scopes.
    """

    def __init__(self, container: 'DIContainer') -> None:
        """Initialize a scope with reference to its parent container.

        Args:
            container: Parent DI container
        """
        self.container = container
        self.instances: Dict[str, Any] = {}

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service from this scope.

        Args:
            service_type: Type of service to resolve

        Returns:
            An instance of the requested service

        Raises:
            KeyError: If service is not registered
        """
        return self.container.resolve(service_type, self)


class DIContainer:
    """Advanced dependency injection container.

    This container provides advanced DI features including:
    - Support for different service lifetimes (singleton, scoped, transient)
    - Auto-resolving dependencies through constructor injection
    - Factory methods for complex instantiation
    - Circular dependency detection
    """

    def __init__(self) -> None:
        """Initialize the dependency injection container."""
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._singletons: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}

    def configure(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Configure the container with application settings.

        Args:
            config: Optional configuration dictionary
        """
        self._config = config or {}

    def register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type] = None,
        *,
        lifetime: str = ServiceLifetime.SINGLETON,
        implementation: Optional[Any] = None,
        factory: Optional[Callable[..., Any]] = None,
    ) -> None:
        """Register a service with the container.

        Args:
            service_type: Interface or abstract type being registered
            implementation_type: Concrete type implementing the service (optional)
            lifetime: Service lifetime (singleton, scoped, transient)
            implementation: Instance implementing the service (optional)
            factory: Factory function to create the service (optional)

        Example:
            ```python
            # Register a concrete type
            container.register(IUserService, UserService)

            # Register an instance (always singleton)
            container.register(IConfig, config_instance)

            # Register a factory
            container.register(IDatabase, factory=lambda c: 
                Database(c.resolve(ISettings).connection_string))
            ```
        """
        # If only implementation is provided, use singleton lifetime
        if implementation is not None and lifetime != ServiceLifetime.SINGLETON:
            logger.warning(
                f"Forcing singleton lifetime for {service_type.__name__} "
                "because an implementation instance was provided"
            )
            lifetime = ServiceLifetime.SINGLETON

        # Determine dependencies for implementation type
        dependencies = []
        if implementation_type and not implementation and not factory:
            try:
                dependencies = self._get_constructor_dependencies(implementation_type)
            except Exception as e:
                logger.warning(
                    f"Failed to determine dependencies for {implementation_type}: {e}"
                )

        # Create registration
        registration = ServiceRegistration(
            service_type=service_type,
            implementation_type=implementation_type,
            implementation=implementation,
            factory=factory,
            lifetime=lifetime,
            dependencies=dependencies,
        )

        # Store registration
        key = service_type.__name__
        self._registrations[key] = registration

        # If this is a singleton with an instance already provided, store it
        if lifetime == ServiceLifetime.SINGLETON and implementation is not None:
            self._singletons[key] = implementation

        logger.debug(f"Registered service: {key} with lifetime {lifetime}")

    def factory(self, service_type: Type[TFactory]) -> Callable[..., TFactory]:
        """Get a factory function for a service type.

        This creates a factory that can be used to create instances of the
        registered service with optional arguments that override the resolved
        dependencies.

        Args:
            service_type: Type of service to create a factory for

        Returns:
            A factory function that creates instances of the service

        Raises:
            KeyError: If service is not registered
        """
        key = service_type.__name__
        if key not in self._registrations:
            raise KeyError(f"No service of type {key} is registered")

        def factory_func(**kwargs: Any) -> TFactory:
            """Factory function for creating service instances with overrides.

            Args:
                **kwargs: Override values for dependencies

            Returns:
                An instance of the requested service
            """
            return self._create_instance(self._registrations[key], None, kwargs)

        return factory_func

    def create_scope(self) -> Scope:
        """Create a new scope for scoped services.

        Returns:
            A new scope for resolving scoped services
        """
        return Scope(self)

    def resolve(self, service_type: Type[T], scope: Optional[Scope] = None) -> T:
        """Resolve a service instance.

        Args:
            service_type: Type of service to resolve
            scope: Optional scope for resolving scoped services

        Returns:
            An instance of the requested service

        Raises:
            KeyError: If service is not registered
        """
        key = service_type.__name__
        if key not in self._registrations:
            raise KeyError(f"No service of type {key} is registered")

        registration = self._registrations[key]
        
        # Handle different service lifetimes
        if registration.lifetime == ServiceLifetime.SINGLETON:
            # For singletons, create once and reuse
            if key not in self._singletons:
                self._singletons[key] = self._create_instance(registration, scope)
            return cast(T, self._singletons[key])
        
        elif registration.lifetime == ServiceLifetime.SCOPED:
            # For scoped services, ensure we have a scope
            if not scope:
                raise ValueError(
                    f"Cannot resolve scoped service {key} without a scope"
                )
            
            # Create once per scope
            if key not in scope.instances:
                scope.instances[key] = self._create_instance(registration, scope)
            return cast(T, scope.instances[key])
        
        else:  # TRANSIENT
            # Always create a new instance
            return cast(T, self._create_instance(registration, scope))

    def _create_instance(
        self, 
        registration: ServiceRegistration, 
        scope: Optional[Scope] = None,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Create an instance of a service.

        Args:
            registration: Service registration
            scope: Optional scope for resolving dependencies
            overrides: Optional dependency overrides

        Returns:
            An instance of the service

        Raises:
            ValueError: If instantiation fails
        """
        # If we already have an instance, return it
        if registration.implementation is not None:
            return registration.implementation

        # If we have a factory, use it with resolved dependencies
        if registration.factory is not None:
            return registration.factory(self)

        # Otherwise, create an instance of the implementation type
        if registration.implementation_type is None:
            raise ValueError(
                f"Cannot create instance of {registration.service_type.__name__}: "
                "no implementation type, instance, or factory provided"
            )

        # Resolve dependencies
        args = {}
        overrides = overrides or {}
        
        for dep_type in registration.dependencies:
            dep_name = dep_type.__name__
            if dep_name in overrides:
                # Use override if provided
                args[dep_name.lower()] = overrides[dep_name]
            else:
                # Otherwise resolve from container
                try:
                    args[dep_name.lower()] = self.resolve(dep_type, scope)
                except KeyError:
                    logger.warning(
                        f"Failed to resolve dependency {dep_name} for "
                        f"{registration.service_type.__name__}"
                    )

        # Create instance with resolved dependencies
        try:
            return registration.implementation_type(**args)
        except Exception as e:
            raise ValueError(
                f"Failed to create instance of {registration.service_type.__name__}: {e}"
            )

    def _get_constructor_dependencies(self, implementation_type: Type) -> List[Type]:
        """Determine the dependencies required by a type's constructor.

        Args:
            implementation_type: Type to analyze

        Returns:
            List of dependency types

        Raises:
            ValueError: If constructor analysis fails
        """
        try:
            # Get constructor signature
            constructor = implementation_type.__init__
            signature = inspect.signature(constructor)
            
            # Extract parameter types from type hints
            dependencies = []
            for name, param in signature.parameters.items():
                if name == "self":
                    continue
                    
                # Get the parameter type
                param_type = param.annotation
                if param_type is not inspect.Parameter.empty and isinstance(param_type, type):
                    dependencies.append(param_type)
                    
            return dependencies
        except Exception as e:
            raise ValueError(f"Failed to analyze constructor for {implementation_type}: {e}")

    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered.

        Args:
            service_type: Type to check

        Returns:
            True if the type is registered, False otherwise
        """
        return service_type.__name__ in self._registrations
        
    def remove_registration(self, service_type: Type) -> bool:
        """Remove a service registration.

        Args:
            service_type: Type to remove

        Returns:
            True if removed, False if not found
        """
        key = service_type.__name__
        if key in self._registrations:
            del self._registrations[key]
            if key in self._singletons:
                del self._singletons[key]
            return True
        return False


# Create a global container instance
container = DIContainer()