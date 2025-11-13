"""
Simple Dependency Injection Container

Provides a clean way to manage dependencies without singletons.
Supports both transient and singleton service lifetimes.

REFACTORED: Architecture Modernization - Phase 4
Replaces singleton pattern with proper dependency injection.
"""

import logging
from typing import Any, Callable, Type, TypeVar, Dict, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """
    Simple dependency injection container for managing service lifetimes.

    This replaces the need for singleton patterns by providing a centralized
    way to manage service instances with proper dependency injection.

    Example:
        container = DIContainer()

        # Register a singleton service
        container.register('config', Config, singleton=True)

        # Register a transient service
        container.register('checksum_manager', ChecksumManager, singleton=True)

        # Get service instance
        config = container.get('config')
    """

    def __init__(self):
        """Initialize the DI container."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        service_class: Type[T],
        singleton: bool = True,
        factory: Optional[Callable[..., T]] = None,
    ) -> None:
        """
        Register a service in the container.

        Args:
            name: Name to register the service under
            service_class: Class to instantiate
            singleton: If True, returns same instance; if False, creates new instance each time
            factory: Optional factory function to create instances
        """
        self._services[name] = {
            'class': service_class,
            'factory': factory,
            'singleton': singleton,
        }
        logger.debug(f"Registered service '{name}' as {'singleton' if singleton else 'transient'}")

    def get(self, name: str, *args, **kwargs) -> Any:
        """
        Get a service instance from the container.

        Args:
            name: Name of the service to get
            *args: Arguments to pass to service constructor
            **kwargs: Keyword arguments to pass to service constructor

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        if name not in self._services:
            raise ValueError(f"Service '{name}' not registered in container")

        service_info = self._services[name]

        # Return existing singleton if available
        if service_info['singleton'] and name in self._singletons:
            return self._singletons[name]

        # Create new instance
        factory = service_info['factory']
        service_class = service_info['class']

        if factory:
            instance = factory(*args, **kwargs)
        else:
            instance = service_class(*args, **kwargs)

        # Store singleton if needed
        if service_info['singleton']:
            self._singletons[name] = instance

        return instance

    def has(self, name: str) -> bool:
        """
        Check if a service is registered.

        Args:
            name: Name of the service to check

        Returns:
            True if service is registered
        """
        return name in self._services

    def unregister(self, name: str) -> None:
        """
        Unregister a service.

        Args:
            name: Name of the service to unregister
        """
        if name in self._services:
            del self._services[name]
            if name in self._singletons:
                del self._singletons[name]
            logger.debug(f"Unregistered service '{name}'")

    def clear_singletons(self) -> None:
        """
        Clear all singleton instances.

        Useful for testing to ensure clean state.
        """
        self._singletons.clear()
        logger.debug("Cleared all singleton instances")

    def get_registered_services(self) -> list[str]:
        """
        Get list of all registered service names.

        Returns:
            List of service names
        """
        return list(self._services.keys())


# Global container instance for convenience
# Use container = DIContainer() for isolated containers
_global_container = DIContainer()


def get_container() -> DIContainer:
    """
    Get the global DI container.

    DEPRECATED: Use DIContainer() directly for better testability.
    """
    return _global_container


# Export public API
__all__ = [
    'DIContainer',
    'get_container',
]
