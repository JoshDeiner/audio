"""Module loader for dependency injection configuration.

This module provides functionality to automatically discover and register
service implementations from modules across the application.
"""

import importlib
import inspect
import logging
import os
import pkgutil
from typing import Any, Dict, Iterable, List, Optional, Set, Type, cast

from library.bin.dependency_injection.container import DIContainer, ServiceLifetime

logger = logging.getLogger(__name__)


class Injectable:
    """Decorator to mark a class as injectable with specific configuration."""

    def __init__(
        self,
        interface: Optional[Type] = None,
        lifetime: str = ServiceLifetime.SINGLETON,
    ) -> None:
        """Initialize the decorator.

        Args:
            interface: Optional interface this class implements
            lifetime: Service lifetime (singleton, scoped, transient)
        """
        self.interface = interface
        self.lifetime = lifetime

    def __call__(self, cls: Type) -> Type:
        """Apply the decorator to a class.

        Args:
            cls: The class to decorate

        Returns:
            The decorated class
        """
        # Store metadata on the class
        setattr(cls, "__injectable__", True)
        setattr(cls, "__inj_interface__", self.interface or cls)
        setattr(cls, "__inj_lifetime__", self.lifetime)

        return cls


class ModuleLoader:
    """Module loader for automatic discovery and registration of services."""

    def __init__(self, container: DIContainer) -> None:
        """Initialize the module loader.

        Args:
            container: DI container to register services with
        """
        self.container = container
        self._processed_modules: Set[str] = set()

    def load_modules(self, package_paths: Iterable[str]) -> Dict[str, int]:
        """Load modules from specified package paths and register services.

        Args:
            package_paths: Iterable of package paths to scan for services

        Returns:
            Dict with counts of registered services by type
        """
        stats = {"interfaces": 0, "implementations": 0, "modules": 0}

        for package_path in package_paths:
            self._load_from_package(package_path, stats)

        return stats

    def _load_from_package(
        self, package_path: str, stats: Dict[str, int]
    ) -> None:
        """Load modules from a package and register services.

        Args:
            package_path: Package path to scan
            stats: Dict with registration statistics
        """
        try:
            # Import the package
            package_name = package_path.replace("/", ".")
            if package_name.startswith("."):
                package_name = package_name[1:]

            # Skip if already processed
            if package_name in self._processed_modules:
                return

            # Add to processed set
            self._processed_modules.add(package_name)

            # Import the package
            package = importlib.import_module(package_name)

            # Register services from the package
            self._register_services_from_module(package, stats)

            # Process subpackages
            for _, subpackage_name, is_pkg in pkgutil.iter_modules(
                package.__path__, package.__name__ + "."
            ):
                if is_pkg:
                    self._load_from_package(subpackage_name, stats)
                else:
                    # Import the module and register services
                    try:
                        module = importlib.import_module(subpackage_name)
                        self._register_services_from_module(module, stats)
                        stats["modules"] += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to import module {subpackage_name}: {e}"
                        )

        except Exception as e:
            logger.warning(f"Failed to process package {package_path}: {e}")

    def _register_services_from_module(
        self, module: Any, stats: Dict[str, int]
    ) -> None:
        """Register services from a module.

        Args:
            module: Module to scan for services
            stats: Dict with registration statistics
        """
        # Get all classes in the module
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip classes not defined in this module
            if obj.__module__ != module.__name__:
                continue

            # Check if the class is marked as injectable
            if hasattr(obj, "__injectable__"):
                interface = getattr(obj, "__inj_interface__")
                lifetime = getattr(obj, "__inj_lifetime__")

                # Register the implementation with its interface
                if interface != obj:
                    try:
                        self.container.register(
                            interface, obj, lifetime=lifetime
                        )
                        stats["implementations"] += 1
                        logger.debug(
                            f"Registered {obj.__name__} as implementation of {interface.__name__}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to register {obj.__name__} for {interface.__name__}: {e}"
                        )
                else:
                    try:
                        self.container.register(obj, obj, lifetime=lifetime)
                        stats["interfaces"] += 1
                        logger.debug(
                            f"Registered self-implementing service: {obj.__name__}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to register {obj.__name__}: {e}"
                        )


def auto_register_services(
    container: DIContainer, package_paths: List[str]
) -> Dict[str, int]:
    """Auto-register services from specified packages.

    Args:
        container: DI container to register services with
        package_paths: List of package paths to scan

    Returns:
        Dict with counts of registered services
    """
    loader = ModuleLoader(container)
    return loader.load_modules(package_paths)
