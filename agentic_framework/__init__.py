"""
Xeo - A modular framework for building autonomous agent systems.
"""

# Core components
from .core.agent import Agent, AgentConfig, AgentType
from .core.team import Team, TeamRole

# LLM integration
from .llm import (
    BaseLLM,
    LLMType,
    LLMError,
    Message,
    MessageRole,
    create_llm,
    get_llm_provider
)

__version__ = "0.1.0"
__all__ = [
    # Core components
    'Agent', 'AgentConfig', 'AgentType',
    'Team', 'TeamRole',
    
    # LLM integration
    'BaseLLM',
    'LLMType',
    'LLMError',
    'Message',
    'MessageRole',
    'create_llm',
    'get_llm_provider',
]