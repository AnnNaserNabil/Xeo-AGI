"""
Provider configurations for the Xeo framework.

This module contains configuration and initialization logic for different
LLM providers supported by the framework.
"""
from typing import Dict, Type, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
import os
from enum import Enum

# Define LLMType as a string literal to avoid circular imports
LLMTypeStr = Literal["gemini", "openai", "claude"]

# Import BaseLLM with a deferred import to avoid circular imports
BaseLLM = Any  # This will be properly imported when needed

# Import GeminiLLM with a deferred import
try:
    from ..llm.providers.gemini import GeminiLLM
except ImportError:
    GeminiLLM = None

class ProviderConfig(BaseModel):
    """Base configuration for a provider."""
    enabled: bool = True
    priority: int = 10  # Lower numbers have higher priority
    config: Dict[str, Any] = Field(default_factory=dict)

class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    default_provider: str = "gemini"
    providers: Dict[str, ProviderConfig] = Field(
        default_factory=lambda: {
            "gemini": ProviderConfig(
                enabled=True,
                priority=10,
                config={
                    "api_key": os.getenv("GOOGLE_API_KEY"),
                    "default_model": "gemini-2.0-flash"
                }
            ),
            "openai": ProviderConfig(
                enabled=False,
                priority=20,
                config={
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "default_model": "gpt-4"
                }
            )
        }
    )
    
    def get_provider(self, provider_name: Optional[LLMTypeStr] = None) -> Type[BaseLLM]:
        # Deferred import to avoid circular imports
        from ..llm.base import BaseLLM  # noqa: F811
        """Get the provider class for the specified provider."""
        provider_name = provider_name or self.default_provider
        if provider_name not in self.providers or not self.providers[provider_name].enabled:
            raise ValueError(f"Provider '{provider_name}' is not enabled or does not exist")
        
        if provider_name == "gemini":
            return GeminiLLM
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def get_provider_config(self, provider_name: LLMTypeStr) -> Dict[str, Any]:
        """Get the configuration for a specific provider."""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name].config

# Global LLM configuration
llm_config = LLMConfig()

def get_llm_config() -> LLMConfig:
    """Get the LLM configuration."""
    return llm_config
