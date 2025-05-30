"""
Factory module for creating and managing LLM instances.

This module provides a factory pattern for creating LLM instances
with proper configuration and dependency injection.
"""
from typing import Type, Dict, Optional, Any
from .base import BaseLLM, LLMType, LLMError
from ..config.providers import get_llm_config

class LLMFactory:
    """Factory for creating and managing LLM instances."""
    
    _instance = None
    _providers: Dict[LLMType, Type[BaseLLM]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._config = get_llm_config()
        self._initialized = True
    
    def register_provider(self, provider_type: LLMType, provider_class: Type[BaseLLM]) -> None:
        """Register a new LLM provider.
        
        Args:
            provider_type: The type of the provider
            provider_class: The provider class to register
            
        Raises:
            ValueError: If the provider type is already registered
        """
        if provider_type in self._providers:
            raise ValueError(f"Provider type '{provider_type}' is already registered")
        self._providers[provider_type] = provider_class
    
    def get_provider(self, provider_name: Optional[str] = None) -> Type[BaseLLM]:
        """Get the provider class for the specified provider.
        
        Args:
            provider_name: Name of the provider (defaults to the configured default)
            
        Returns:
            The provider class
            
        Raises:
            ValueError: If the provider is not found or not enabled
        """
        provider_name = provider_name or self._config.default_provider
        
        try:
            provider_type = LLMType(provider_name)
        except ValueError as e:
            raise ValueError(f"Unknown provider type: {provider_name}") from e
            
        if provider_type not in self._providers:
            raise ValueError(f"No provider registered for type: {provider_type}")
            
        return self._providers[provider_type]
    
    def create_llm(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> BaseLLM:
        """Create a new LLM instance.
        
        Args:
            provider_name: Name of the provider (defaults to the configured default)
            model_name: Name of the model to use (defaults to the provider's default)
            **kwargs: Additional arguments to pass to the provider
            
        Returns:
            An instance of the requested LLM provider
            
        Raises:
            ValueError: If the provider is not found or not enabled
        """
        # Get the provider class
        provider_class = self.get_provider(provider_name)
        
        # Get provider config
        provider_name = provider_name or self._config.default_provider
        provider_config = self._config.get_provider_config(provider_name)
        
        # Merge config with provided kwargs (kwargs take precedence)
        config = {**provider_config, **kwargs}
        
        # Use provided model_name or default from config
        model = model_name or config.pop("default_model", None)
        if not model:
            raise ValueError("No model name provided and no default model configured")
            
        return provider_class(model_name=model, **config)

# Global factory instance
llm_factory = LLMFactory()

def get_llm_factory() -> LLMFactory:
    """Get the global LLM factory instance."""
    return llm_factory
