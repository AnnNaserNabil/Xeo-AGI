"""
LLM (Large Language Model) module for the Xeo Framework.
"""
from typing import Type, Dict, Literal

from .base import BaseLLM, LLMError, Message, MessageRole
from .llm_factory import get_llm_factory, llm_factory, LLMTypeStr

# For backward compatibility
LLMType = LLMTypeStr

# Registry of available LLM providers
_llm_registry: Dict[LLMTypeStr, Type[BaseLLM]] = {}

def get_llm_provider(llm_type: LLMTypeStr) -> Type[BaseLLM]:
    """
    Get the LLM provider class for the given type.
    
    Args:
        llm_type: Type of LLM provider (e.g., 'gemini', 'openai', 'claude')
        
    Returns:
        LLM provider class
        
    Raises:
        LLMError: If the provider is not supported
    """
    # Lazy import to avoid circular imports
    from .providers.gemini import GeminiLLM
    
    # Register known providers
    if not _llm_registry:
        _llm_registry['gemini'] = GeminiLLM
        # Register with the factory
        factory = get_llm_factory()
        factory.register_provider('gemini', GeminiLLM)
    
    if llm_type not in _llm_registry:
        raise LLMError(f"Unsupported LLM provider: {llm_type}")
    return _llm_registry[llm_type]

def create_llm(
    llm_type: LLMTypeStr,
    model_name: str,
    **kwargs
) -> BaseLLM:
    """
    Create an instance of an LLM provider.
    
    Args:
        llm_type: Type of LLM provider
        model_name: Name of the model to use
        **kwargs: Provider-specific arguments
        
    Returns:
        LLM instance
    """
    provider = get_llm_provider(llm_type)
    return provider(model_name, **kwargs)

__all__ = [
    'get_llm_factory',
    'llm_factory',
    'BaseLLM',
    'LLMType',
    'LLMError',
    'Message',
    'MessageRole',
    'get_llm_provider',
    'create_llm',
]
