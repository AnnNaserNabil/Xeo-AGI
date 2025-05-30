"""
Provider configurations for the Xeo framework.

This module contains configuration and initialization logic for different
LLM providers supported by the framework.
"""
from typing import Dict, Type, Any, Optional
from pydantic import BaseModel, Field
import os
from ..llm.base import BaseLLM, LLMType
from ..llm.providers import get_llm_provider

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
    
    def get_provider(self, provider_name: Optional[str] = None) -> Type[BaseLLM]:
        """Get the provider class for the specified provider."""
        provider_name = provider_name or self.default_provider
        if provider_name not in self.providers or not self.providers[provider_name].enabled:
            raise ValueError(f"Provider '{provider_name}' is not enabled or does not exist")
        
        try:
            return get_llm_provider(LLMType(provider_name))
        except ValueError as e:
            raise ValueError(f"Failed to load provider '{provider_name}': {str(e)}")
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get the configuration for a specific provider."""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name].config

# Global LLM configuration
llm_config = LLMConfig()

def get_llm_config() -> LLMConfig:
    """Get the LLM configuration."""
    return llm_config
