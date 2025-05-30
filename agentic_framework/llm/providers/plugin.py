"""
Gemini LLM Provider Plugin for the Xeo framework.

This module provides a plugin for the Gemini LLM provider.
"""
from typing import Dict, Any
from ...core.plugins import plugin_manager
from ..base import LLMType
from ..plugin import register_llm_provider
from .gemini import GeminiLLM

# Register the Gemini provider with the plugin system
gemini_plugin = register_llm_provider(
    provider_class=GeminiLLM,
    provider_type=LLMType.GEMINI,
    name="Google Gemini",
    version="2.0.0",
    description="Google's Gemini family of language models",
    author="Google",
    url="https://ai.google.dev/",
    default_model="gemini-2.0-flash",
    supported_models={
        "gemini-1.5-pro": {
            "max_tokens": 1048576,
            "capabilities": ["chat", "function_calling", "streaming", "long_context"]
        },
        "gemini-1.5-flash": {
            "max_tokens": 1048576,
            "capabilities": ["chat", "function_calling", "streaming"]
        },
        "gemini-2.0-flash": {
            "max_tokens": 128000,
            "capabilities": ["chat", "function_calling", "streaming", "long_context"]
        },
        "gemini-2.0-pro": {
            "max_tokens": 1048576,
            "capabilities": ["chat", "function_calling", "streaming", "long_context"]
        }
    }
)

# Register the plugin with the global plugin manager
def register():
    """Register the Gemini plugin with the global plugin manager."""
    plugin_manager.register_plugin(gemini_plugin)

# Automatically register the plugin when the module is imported
register()
