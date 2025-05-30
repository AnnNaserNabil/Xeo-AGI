"""
Xeo - A modular framework for building autonomous agent systems.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Core components
from .core.agent import Agent, AgentConfig, AgentType
from .core.team import Team, TeamRole
from .core.plugins import PluginType, PluginManager, get_plugin_manager

# Configuration
from .config import get_settings, Settings
from .config.providers import get_llm_config, LLMConfig

# LLM integration
from .llm import (
    BaseLLM,
    LLMType,
    LLMError,
    Message,
    MessageRole,
    create_llm,
    get_llm_provider,
    llm_factory,
    get_llm_factory
)

# Import plugins
from .llm.providers.plugin import register as register_gemini_plugin

__version__ = "0.2.0"

# Global initialization flag
_initialized = False

def init(config_path: Optional[str] = None, **kwargs) -> None:
    """
    Initialize the Xeo framework.
    
    Args:
        config_path: Path to a configuration file
        **kwargs: Additional configuration overrides
    """
    global _initialized
    
    if _initialized:
        return
    
    # Load settings
    settings = get_settings()
    
    # Load environment from .env file if it exists
    env_path = Path(config_path) if config_path else Path.cwd() / ".env"
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
    
    # Initialize plugins
    plugin_manager = get_plugin_manager()
    
    # Load plugins from the plugins directory
    plugins_dir = Path(__file__).parent / "plugins"
    if plugins_dir.exists():
        plugin_manager.load_plugins_from_path(str(plugins_dir))
    
    # Initialize plugins
    plugin_manager.initialize_plugins(**kwargs.get("plugins", {}))
    
    _initialized = True

def cleanup() -> None:
    """Clean up resources used by the Xeo framework."""
    global _initialized
    
    if not _initialized:
        return
    
    # Clean up plugins
    plugin_manager = get_plugin_manager()
    plugin_manager.cleanup()
    
    _initialized = False

# Export public API
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
    'llm_factory',
    'get_llm_factory',
    
    # Configuration
    'get_settings',
    'Settings',
    'get_llm_config',
    'LLMConfig',
    
    # Plugin system
    'PluginType',
    'PluginManager',
    'get_plugin_manager',
    
    # Initialization
    'init',
    'cleanup',
]

# Auto-initialize if XEO_AUTO_INIT is set
if os.getenv("XEO_AUTO_INIT", "true").lower() == "true":
    try:
        init()
    except Exception as e:
        print(f"Warning: Failed to auto-initialize Xeo framework: {e}")