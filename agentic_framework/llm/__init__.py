"""
LLM (Large Language Model) module for the Xeo Framework.
"""
from typing import Type, Dict

from .base import BaseLLM, LLMType, LLMError, Message, MessageRole
from .providers.gemini import GeminiLLM

# Registry of available LLM providers
_llm_registry: Dict[LLMType, Type[BaseLLM]] = {
    LLMType.GEMINI: GeminiLLM,
}

def get_llm_provider(llm_type: LLMType) -> Type[BaseLLM]:
    """
    Get the LLM provider class for the given type.
    
    Args:
        llm_type: Type of LLM provider
        
    Returns:
        LLM provider class
        
    Raises:
        LLMError: If the provider is not supported
    """
    if llm_type not in _llm_registry:
        raise LLMError(f"Unsupported LLM provider: {llm_type}")
    return _llm_registry[llm_type]

def create_llm(
    llm_type: LLMType,
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
    'BaseLLM',
    'LLMType',
    'LLMError',
    'Message',
    'MessageRole',
    'get_llm_provider',
    'create_llm',
]
