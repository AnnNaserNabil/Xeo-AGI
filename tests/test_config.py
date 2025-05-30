"""
Tests for the Xeo configuration system.
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from pydantic import ValidationError

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo.config import (
    Settings,
    get_settings,
    settings as global_settings
)
from xeo.config.providers import (
    ProviderConfig,
    LLMConfig,
    get_llm_config,
    llm_config as global_llm_config
)

class TestSettings:
    """Test suite for the Settings class."""
    
    def test_settings_defaults(self):
        """Test that settings have the expected default values."""
        settings = Settings()
        
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"
        assert "xeo" in str(settings.DATA_DIR)
        assert "xeo" in str(settings.CACHE_DIR)
    
    def test_settings_environment_variables(self, monkeypatch):
        """Test that settings can be overridden with environment variables."""
        monkeypatch.setenv("XEO_DEBUG", "true")
        monkeypatch.setenv("XEO_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("XEO_DATA_DIR", "/custom/data")
        monkeypatch.setenv("XEO_CACHE_DIR", "/custom/cache")
        
        settings = Settings()
        
        assert settings.DEBUG is True
        assert settings.LOG_LEVEL == "DEBUG"
        assert str(settings.DATA_DIR) == "/custom/data"
        assert str(settings.CACHE_DIR) == "/custom/cache"
    
    def test_invalid_log_level(self):
        """Test that an invalid log level raises a ValidationError."""
        with pytest.raises(ValidationError):
            Settings(LOG_LEVEL="INVALID_LEVEL")
    
    def test_ensure_dirs(self, tmp_path):
        """Test that directories are created if they don't exist."""
        data_dir = tmp_path / "data"
        cache_dir = tmp_path / "cache"
        
        settings = Settings(
            DATA_DIR=data_dir,
            CACHE_DIR=cache_dir
        )
        
        assert data_dir.exists()
        assert cache_dir.exists()

def test_get_settings():
    """Test that get_settings returns a singleton instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2
    assert settings1 is global_settings

class TestProviderConfig:
    """Test suite for the ProviderConfig class."""
    
    def test_provider_config_defaults(self):
        """Test that ProviderConfig has the expected default values."""
        config = ProviderConfig()
        
        assert config.enabled is True
        assert config.priority == 10
        assert config.config == {}
    
    def test_provider_config_custom_values(self):
        """Test that ProviderConfig can be initialized with custom values."""
        config = ProviderConfig(
            enabled=False,
            priority=5,
            config={"api_key": "test-key"}
        )
        
        assert config.enabled is False
        assert config.priority == 5
        assert config.config == {"api_key": "test-key"}

class TestLLMConfig:
    """Test suite for the LLMConfig class."""
    
    def test_llm_config_defaults(self):
        """Test that LLMConfig has the expected default values."""
        config = LLMConfig()
        
        assert config.default_provider == "gemini"
        assert isinstance(config.providers, dict)
        assert len(config.providers) > 0
        assert "gemini" in config.providers
    
    def test_get_provider(self):
        """Test getting a provider configuration."""
        config = LLMConfig()
        
        # Test getting an existing provider
        provider = config.get_provider("gemini")
        assert provider is not None
        assert isinstance(provider, type)
        
        # Test getting a non-existent provider
        with pytest.raises(ValueError, match="No provider registered for type: invalid"):
            config.get_provider("invalid")
    
    def test_get_provider_config(self):
        """Test getting a provider's configuration."""
        config = LLMConfig()
        
        # Test getting config for an existing provider
        provider_config = config.get_provider_config("gemini")
        assert provider_config is not None
        assert isinstance(provider_config, dict)
        
        # Test getting config for a non-existent provider
        with pytest.raises(ValueError, match="Unknown provider: invalid"):
            config.get_provider_config("invalid")

def test_get_llm_config():
    """Test that get_llm_config returns a singleton instance."""
    config1 = get_llm_config()
    config2 = get_llm_config()
    
    assert config1 is config2
    assert config1 is global_llm_config

class TestEnvironmentIntegration:
    """Test integration with environment variables."""
    
    def test_llm_config_environment_variables(self, monkeypatch):
        """Test that LLM config can be overridden with environment variables."""
        # Set environment variables
        monkeypatch.setenv("DEFAULT_LLM_PROVIDER", "openai")
        monkeypatch.setenv("DEFAULT_LLM_MODEL", "gpt-4")
        
        # Create a new config instance (bypassing the singleton)
        config = LLMConfig()
        
        assert config.default_provider == "openai"
        
        # Check that the default model is set for the provider
        provider_config = config.get_provider_config("openai")
        assert provider_config.get("default_model") == "gpt-4"
    
    def test_provider_config_environment_variables(self, monkeypatch):
        """Test that provider config can be overridden with environment variables."""
        # Set environment variables for the Gemini provider
        monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
        monkeypatch.setenv("GEMINI_DEFAULT_MODEL", "gemini-2.0-pro")
        
        # Create a new config instance (bypassing the singleton)
        config = LLMConfig()
        
        # Check that the provider config was updated
        provider_config = config.get_provider_config("gemini")
        assert provider_config.get("api_key") == "test-api-key"
        assert provider_config.get("default_model") == "gemini-2.0-pro"

class TestConfigIntegration:
    """Test integration between different config components."""
    
    def test_settings_and_llm_config_integration(self):
        """Test that settings and LLM config work together."""
        # Get the global instances
        settings = get_settings()
        llm_config = get_llm_config()
        
        # Verify they don't interfere with each other
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(llm_config.default_provider, str)
        
        # Verify the LLM config can be used to create a provider
        provider_class = llm_config.get_provider(llm_config.default_provider)
        assert provider_class is not None
        assert issubclass(provider_class, type)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
