"""
Plugin system for the Xeo framework.

This module provides a plugin architecture that allows extending the framework's
functionality without modifying the core code.
"""
from typing import Dict, Type, Any, Optional, Protocol, runtime_checkable
from pathlib import Path
import importlib
import pkgutil
import inspect
from dataclasses import dataclass
from enum import Enum

class PluginType(str, Enum):
    """Types of plugins supported by the framework."""
    LLM_PROVIDER = "llm_provider"
    TOOL = "tool"
    MEMORY = "memory"
    WORKFLOW = "workflow"
    UI = "ui"
    INTEGRATION = "integration"

@runtime_checkable
class XeoPlugin(Protocol):
    """Base protocol that all plugins must implement."""
    
    @property
    def plugin_type(self) -> PluginType:
        """The type of this plugin."""
        ...
    
    def initialize(self, **kwargs) -> None:
        """Initialize the plugin.
        
        Args:
            **kwargs: Plugin-specific initialization parameters
        """
        ...
    
    def cleanup(self) -> None:
        """Clean up any resources used by the plugin."""
        ...

@dataclass
class PluginInfo:
    """Metadata about a plugin."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    url: str = ""
    type: Optional[PluginType] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginInfo':
        """Create a PluginInfo instance from a dictionary."""
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            url=data.get("url", ""),
            type=PluginType(data["type"]) if "type" in data else None
        )

class PluginManager:
    """Manages the loading and initialization of plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, XeoPlugin] = {}
        self._initialized = False
    
    def register_plugin(self, plugin: XeoPlugin) -> None:
        """Register a plugin instance.
        
        Args:
            plugin: The plugin instance to register
            
        Raises:
            ValueError: If a plugin with the same name is already registered
        """
        if not hasattr(plugin, 'plugin_info') or not isinstance(plugin.plugin_info, PluginInfo):
            raise ValueError("Plugin must have a valid plugin_info attribute")
            
        if plugin.plugin_info.name in self._plugins:
            raise ValueError(f"Plugin '{plugin.plugin_info.name}' is already registered")
            
        self._plugins[plugin.plugin_info.name] = plugin
    
    def load_plugins_from_path(self, path: str) -> None:
        """Load plugins from a directory path.
        
        Args:
            path: Path to the directory containing plugin modules
        """
        module_path = Path(path).resolve()
        if not module_path.exists():
            return
            
        # Import all modules in the directory
        for _, name, _ in pkgutil.iter_modules([str(module_path)]):
            try:
                module = importlib.import_module(f"{module_path.name}.{name}")
                self._register_plugins_from_module(module)
            except ImportError as e:
                print(f"Failed to load plugin module {name}: {e}")
    
    def _register_plugins_from_module(self, module) -> None:
        """Register all plugins found in a module."""
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if (inspect.isclass(obj) and 
                issubclass(obj, XeoPlugin) and 
                obj != XeoPlugin):
                try:
                    plugin = obj()
                    self.register_plugin(plugin)
                except Exception as e:
                    print(f"Failed to register plugin {obj.__name__}: {e}")
    
    def initialize_plugins(self, **kwargs) -> None:
        """Initialize all registered plugins."""
        if self._initialized:
            return
            
        for plugin in self._plugins.values():
            try:
                plugin.initialize(**kwargs.get(plugin.plugin_info.name, {}))
            except Exception as e:
                print(f"Failed to initialize plugin {plugin.plugin_info.name}: {e}")
        
        self._initialized = True
    
    def get_plugin(self, name: str) -> Optional[XeoPlugin]:
        """Get a plugin by name.
        
        Args:
            name: Name of the plugin to retrieve
            
        Returns:
            The plugin instance, or None if not found
        """
        return self._plugins.get(name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> Dict[str, XeoPlugin]:
        """Get all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to retrieve
            
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return {
            name: plugin 
            for name, plugin in self._plugins.items()
            if plugin.plugin_info.type == plugin_type
        }
    
    def cleanup(self) -> None:
        """Clean up all plugins."""
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Error cleaning up plugin {plugin.plugin_info.name}: {e}")
        
        self._plugins.clear()
        self._initialized = False

# Global plugin manager instance
plugin_manager = PluginManager()

def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return plugin_manager
