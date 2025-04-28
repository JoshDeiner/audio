"""Migration utilities for transitioning from the complex DI to simplified DI.

This module provides utilities to help migrate code from the complex
enterprise-grade DI container to the simplified AppServices approach.
"""

import logging
from typing import Any, Dict, Optional, Type, TypeVar

from library.bin.dependency_injection.app_services import AppServices
from library.bin.dependency_injection.container import (
    DIContainer,
    ServiceLifetime,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DIContainerAdapter:
    """Adapter to make the simplified AppServices look like a DIContainer.

    This adapter allows existing code that depends on the DIContainer
    to work with the simplified AppServices without modification.
    """

    def __init__(self, app_services: AppServices) -> None:
        """Initialize the adapter with AppServices.

        Args:
            app_services: The simplified service container
        """
        self.app_services = app_services
        self._config: Dict[str, Any] = app_services.config

    def configure(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Configure the container with application settings.

        Args:
            config: Optional configuration dictionary
        """
        if config:
            self.app_services.config.update(config)

    def register(
        self,
        service_type: Type[T],
        implementation_type: Optional[Type] = None,
        *,
        lifetime: str = ServiceLifetime.SINGLETON,
        implementation: Optional[Any] = None,
        factory: Optional[Any] = None,
    ) -> None:
        """Register a service with the container.

        Args:
            service_type: Interface or abstract type being registered
            implementation_type: Concrete type implementing the service (optional)
            lifetime: Service lifetime (ignored in simplified DI)
            implementation: Instance implementing the service (optional)
            factory: Factory function to create the service (ignored in simplified DI)
        """
        if implementation:
            self.app_services.register_instance(service_type, implementation)
            logger.info(f"Registered instance for {service_type.__name__}")
        elif implementation_type:
            # Create an instance of the implementation type
            instance = implementation_type()
            self.app_services.register_instance(service_type, instance)
            logger.info(
                f"Registered implementation for {service_type.__name__}"
            )

    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance.

        Args:
            service_type: Type of service to resolve

        Returns:
            An instance of the requested service

        Raises:
            KeyError: If service is not registered
        """
        return self.app_services.get(service_type)


def create_adapter(
    app_services: Optional[AppServices] = None,
) -> DIContainerAdapter:
    """Create a DIContainerAdapter from AppServices.

    Args:
        app_services: Optional AppServices instance

    Returns:
        A DIContainerAdapter that wraps the AppServices
    """
    services = app_services or AppServices()
    return DIContainerAdapter(services)


def migrate_container(container: DIContainer) -> AppServices:
    """Migrate a DIContainer to AppServices.

    Args:
        container: The existing DIContainer

    Returns:
        An AppServices instance with services from the container
    """
    # Create a new AppServices with the same config
    app_services = AppServices(container._config)

    # Unfortunately we can't easily extract registered services from the
    # DIContainer, so we just log that manual service registration might
    # be needed
    logger.warning(
        "DIContainer to AppServices migration: cannot automatically migrate "
        "service registrations. Manual service registration might be needed."
    )

    return app_services
