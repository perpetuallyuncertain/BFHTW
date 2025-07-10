"""
Data source registry for managing all available data sources.

Provides a centralized way to register, configure, and access different data sources
while maintaining the unified interface defined by BaseDataSource.
"""

from typing import Dict, Type, Optional, List
from dataclasses import dataclass
from pathlib import Path
import importlib
import inspect

from BFHTW.pipelines.data_sources.base_source import BaseDataSource, DataSourceConfig
from BFHTW.utils.logs import get_logger

L = get_logger()

@dataclass
class DataSourceRegistration:
    """Registration information for a data source."""
    name: str
    source_class: Type[BaseDataSource]
    config_class: Type[DataSourceConfig]
    description: str
    enabled: bool = True

class DataSourceRegistry:
    """
    Central registry for all data sources.
    
    Manages registration, configuration, and instantiation of data sources
    while ensuring they all comply with the unified interface.
    """
    
    def __init__(self):
        self._sources: Dict[str, DataSourceRegistration] = {}
        self._instances: Dict[str, BaseDataSource] = {}
        self._auto_register_builtin_sources()
    
    def register(
        self,
        name: str,
        source_class: Type[BaseDataSource],
        config_class: Type[DataSourceConfig],
        description: str = "",
        enabled: bool = True
    ) -> None:
        """
        Register a data source.
        
        Args:
            name: Unique identifier for the data source
            source_class: Class implementing BaseDataSource
            config_class: Configuration class for the data source
            description: Human-readable description
            enabled: Whether the source is enabled by default
        """
        # Validate that source_class is a proper subclass
        if not issubclass(source_class, BaseDataSource):
            raise ValueError(f"Source class {source_class.__name__} must inherit from BaseDataSource")
        
        if not issubclass(config_class, DataSourceConfig):
            raise ValueError(f"Config class {config_class.__name__} must inherit from DataSourceConfig")
        
        if name in self._sources:
            L.warning(f"Data source '{name}' already registered, overwriting")
        
        self._sources[name] = DataSourceRegistration(
            name=name,
            source_class=source_class,
            config_class=config_class,
            description=description,
            enabled=enabled
        )
        
        L.info(f"Registered data source: {name}")
    
    def get_source(self, name: str, config: Optional[DataSourceConfig] = None) -> Optional[BaseDataSource]:
        """
        Get a data source instance.
        
        Args:
            name: Name of the data source
            config: Optional configuration (uses default if not provided)
            
        Returns:
            BaseDataSource instance or None if not found
        """
        if name not in self._sources:
            L.error(f"Data source '{name}' not registered")
            return None
        
        registration = self._sources[name]
        
        if not registration.enabled:
            L.warning(f"Data source '{name}' is disabled")
            return None
        
        # Use cached instance if available and no custom config
        if config is None and name in self._instances:
            return self._instances[name]
        
        # Create new instance
        try:
            if config is None:
                # Create default config
                config = registration.config_class(name=name)
            
            instance = registration.source_class(config)
            
            # Cache instance if using default config
            if config.name == name:
                self._instances[name] = instance
            
            return instance
            
        except Exception as e:
            L.error(f"Failed to create data source '{name}': {str(e)}")
            return None
    
    def list_sources(self, enabled_only: bool = True) -> List[str]:
        """
        List all registered data sources.
        
        Args:
            enabled_only: Only return enabled sources
            
        Returns:
            List of source names
        """
        sources = []
        for name, registration in self._sources.items():
            if not enabled_only or registration.enabled:
                sources.append(name)
        return sources
    
    def get_source_info(self, name: str) -> Optional[DataSourceRegistration]:
        """
        Get information about a registered data source.
        
        Args:
            name: Name of the data source
            
        Returns:
            DataSourceRegistration or None if not found
        """
        return self._sources.get(name)
    
    def is_registered(self, name: str) -> bool:
        """Check if a data source is registered."""
        return name in self._sources
    
    def enable_source(self, name: str) -> bool:
        """Enable a data source."""
        if name not in self._sources:
            L.error(f"Data source '{name}' not registered")
            return False
        
        self._sources[name].enabled = True
        L.info(f"Enabled data source: {name}")
        return True
    
    def disable_source(self, name: str) -> bool:
        """Disable a data source."""
        if name not in self._sources:
            L.error(f"Data source '{name}' not registered")
            return False
        
        self._sources[name].enabled = False
        # Remove cached instance
        if name in self._instances:
            del self._instances[name]
        
        L.info(f"Disabled data source: {name}")
        return True
    
    def validate_source(self, name: str) -> bool:
        """
        Validate a data source connection.
        
        Args:
            name: Name of the data source
            
        Returns:
            True if validation passes
        """
        source = self.get_source(name)
        if not source:
            return False
        
        try:
            return source.validate_connection()
        except Exception as e:
            L.error(f"Validation failed for data source '{name}': {str(e)}")
            return False
    
    def _auto_register_builtin_sources(self):
        """Auto-register built-in data sources."""
        try:
            # Register PMC source
            from BFHTW.pipelines.data_sources.pmc_source import PMCDataSource, PMCConfig
            self.register(
                name="pmc",
                source_class=PMCDataSource,
                config_class=PMCConfig,
                description="PubMed Central (PMC) data source for biomedical articles"
            )
            
            # TODO: Add other built-in sources as they're implemented
            # - ArXiv source
            # - Local file source
            # - Custom API sources
            
        except ImportError as e:
            L.warning(f"Failed to auto-register some built-in data sources: {str(e)}")
    
    def discover_sources(self, module_path: str) -> int:
        """
        Discover and register data sources from a module path.
        
        Args:
            module_path: Python module path to search for data sources
            
        Returns:
            Number of sources discovered and registered
        """
        discovered = 0
        
        try:
            module = importlib.import_module(module_path)
            
            # Find all classes that inherit from BaseDataSource
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, BaseDataSource) and 
                    obj != BaseDataSource and 
                    not inspect.isabstract(obj)):
                    
                    # Try to find corresponding config class
                    config_class_name = f"{name}Config"
                    config_class = getattr(module, config_class_name, None)
                    
                    if config_class and issubclass(config_class, DataSourceConfig):
                        source_name = name.lower().replace("datasource", "")
                        self.register(
                            name=source_name,
                            source_class=obj,
                            config_class=config_class,
                            description=f"Auto-discovered source from {module_path}"
                        )
                        discovered += 1
            
            L.info(f"Discovered {discovered} data sources from {module_path}")
            
        except Exception as e:
            L.error(f"Failed to discover data sources from {module_path}: {str(e)}")
        
        return discovered

# Global registry instance
_registry = DataSourceRegistry()

def get_registry() -> DataSourceRegistry:
    """Get the global data source registry."""
    return _registry

def register_source(
    name: str,
    source_class: Type[BaseDataSource],
    config_class: Type[DataSourceConfig],
    description: str = "",
    enabled: bool = True
) -> None:
    """Register a data source with the global registry."""
    _registry.register(name, source_class, config_class, description, enabled)

def get_source(name: str, config: Optional[DataSourceConfig] = None) -> Optional[BaseDataSource]:
    """Get a data source instance from the global registry."""
    return _registry.get_source(name, config)

def list_sources(enabled_only: bool = True) -> List[str]:
    """List all registered data sources."""
    return _registry.list_sources(enabled_only)
