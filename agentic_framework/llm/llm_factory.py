"""
Factory module for creating and managing LLM instances.

This module provides a factory pattern for creating LLM instances
with proper configuration and dependency injection.
"""
from typing import Type, Dict, Optional, Any, Literal
from .base import BaseLLM, LLMError

# Define LLMType as a string literal to avoid circular imports
LLMTypeStr = Literal["gemini", "openai", "claude"]

# Deferred import to avoid circular imports
get_llm_config = None

class LLMFactory:
    """Factory for creating and managing LLM instances."""
    
    _instance = None
    _providers: Dict[LLMTypeStr, Type[BaseLLM]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._config = None
        self._initialized = True
        
    @property
    def config(self):
        if self._config is None:
            from ..config.providers import get_llm_config as _get_llm_config
            self._config = _get_llm_config()
        return self._config
    
    def register_provider(self, provider_type: LLMTypeStr, provider_class: Type[BaseLLM]) -> None:
        """Register a new LLM provider.
        
        Args:
            provider_type: The type of the provider (one of 'gemini', 'openai', 'claude')
            provider_class: The provider class to register
            
        Raises:
            ValueError: If the provider type is already registered or invalid
        """
        if provider_type not in ["gemini", "openai", "claude"]:
            raise ValueError(f"Invalid provider type: {provider_type}")
            
        if provider_type in self._providers:
            raise ValueError(f"Provider type '{provider_type}' is already registered")
        self._providers[provider_type] = provider_class
        
        # Lazy import of get_llm_config
        global get_llm_config
        if get_llm_config is None:
            from ..config.providers import get_llm_config as _get_llm_config
            get_llm_config = _get_llm_config
            self._config = get_llm_config()
    
    def get_provider(self, provider_name: Optional[LLMTypeStr] = None) -> Type[BaseLLM]:
        """Get the provider class for the specified provider.
        
        Args:
            provider_name: Name of the provider (defaults to the configured default)
            
        Returns:
            The provider class
            
        Raises:
            LLMError: If the provider is not found or not enabled
        """
        if not self._providers:
            raise LLMError("No LLM providers registered")
            
        if provider_name is None:
            provider_name = self.config.default_provider
            
        if provider_name not in self._providers:
            raise LLMError(f"No such LLM provider: {provider_name}")
            
        return self._providers[provider_name]
    
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
