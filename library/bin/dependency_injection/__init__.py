"""Dependency injection package for the audio application.

This package provides dependency injection functionality for managing
service instances and their dependencies across the application.
"""

from library.bin.dependency_injection.container import DIContainer, container

__all__ = ["container", "DIContainer"]
