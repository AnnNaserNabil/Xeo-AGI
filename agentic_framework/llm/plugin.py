"""
LLM Provider Plugin for the Xeo framework.

This module provides a base class for implementing LLM provider plugins.
"""
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass
from ..core.plugins import PluginType, XeoPlugin, PluginInfo, plugin_manager
from .base import BaseLLM, LLMType
from .llm_factory import llm_factory

@dataclass
class LLMProviderInfo(PluginInfo):
    """Metadata about an LLM provider plugin."""
    supported_models: Dict[str, Dict[str, Any]] = None
    default_model: str = ""
    
    def __post_init__(self):
        """Set the plugin type to LLM_PROVIDER."""
        self.type = PluginType.LLM_PROVIDER
        if self.supported_models is None:
            self.supported_models = {}

class LLMProviderPlugin(XeoPlugin):
    """Base class for LLM provider plugins."""
    
    def __init__(self, provider_class: Type[BaseLLM], provider_type: LLMType, **kwargs):
        """Initialize the LLM provider plugin.
        
        Args:
            provider_class: The LLM provider class
            provider_type: The type of the provider
            **kwargs: Additional plugin configuration
        """
        self.provider_class = provider_class
        self.provider_type = provider_type
        self.plugin_info = self.get_plugin_info()
        self._initialized = False
    
    def get_plugin_info(self) -> LLMProviderInfo:
        """Get the plugin metadata.
        
        Returns:
            LLMProviderInfo: The plugin metadata
        """
        raise NotImplementedError("Subclasses must implement get_plugin_info")
    
    @property
    def plugin_type(self):
        """Get the plugin type."""
        return PluginType.LLM_PROVIDER
    
    def initialize(self, **kwargs) -> None:
        """Initialize the plugin.
        
        Args:
            **kwargs: Plugin-specific initialization parameters
        """
        if self._initialized:
            return
            
        # Register the provider with the LLM factory
        llm_factory.register_provider(self.provider_type, self.provider_class)
        
        # Update the provider config with any plugin-specific settings
        provider_config = {
            "default_model": self.plugin_info.default_model,
            "supported_models": self.plugin_info.supported_models,
            **kwargs
        }
        
        # Register the provider with the global config
        from ..config.providers import get_llm_config
        config = get_llm_config()
        
        if str(self.provider_type) not in config.providers:
            from ..config.providers import ProviderConfig
            config.providers[str(self.provider_type)] = ProviderConfig(
                enabled=True,
                priority=10,
                config=provider_config
            )
        
        self._initialized = True
        print(f"Initialized LLM provider: {self.plugin_info.name} ({self.provider_type})")
    
    def cleanup(self) -> None:
        """Clean up any resources used by the plugin."""
        if not self._initialized:
            return
            
        # Unregister the provider from the factory
        if hasattr(llm_factory, '_providers') and self.provider_type in llm_factory._providers:
            del llm_factory._providers[self.provider_type]
        
        # Remove from global config
        from ..config.providers import get_llm_config
        config = get_llm_config()
        if str(self.provider_type) in config.providers:
            del config.providers[str(self.provider_type)]
        
        self._initialized = False
        print(f"Cleaned up LLM provider: {self.plugin_info.name} ({self.provider_type})")

def register_llm_provider(
    provider_class: Type[BaseLLM],
    provider_type: LLMType,
    **kwargs
) -> None:
    """Register an LLM provider with the plugin system.
    
    This is a convenience function to create and register an LLM provider plugin.
    
    Args:
        provider_class: The LLM provider class
        provider_type: The type of the provider
        **kwargs: Additional plugin configuration
    """
    class DynamicLLMProvider(LLMProviderPlugin):
        def get_plugin_info(self) -> LLMProviderInfo:
            return LLMProviderInfo(
                name=kwargs.get("name", provider_class.__name__),
                version=kwargs.get("version", "0.1.0"),
                description=kwargs.get("description", ""),
                author=kwargs.get("author", ""),
                url=kwargs.get("url", ""),
                supported_models=kwargs.get("supported_models", {}),
                default_model=kwargs.get("default_model", "")
            )
    
    plugin = DynamicLLMProvider(provider_class, provider_type, **kwargs)
    plugin_manager.register_plugin(plugin)
    return plugin
