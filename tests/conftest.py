"""
Pytest configuration and fixtures for Xeo framework tests.
"""
import os
import sys
import asyncio
from pathlib import Path
from typing import Generator, AsyncGenerator, Any

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_CONFIG = {
    "DEFAULT_LLM_PROVIDER": "gemini",
    "DEFAULT_LLM_MODEL": "gemini-2.0-flash",
    "GOOGLE_API_KEY": "test-api-key",
    "XEO_LOG_LEVEL": "WARNING",
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def setup_environment(monkeypatch):
    """Set up the test environment."""
    # Set environment variables
    for key, value in TEST_CONFIG.items():
        monkeypatch.setenv(key, value)
    
    # Set up test directories
    test_dir = Path(__file__).parent
    test_data_dir = test_dir / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Set XDG_CONFIG_HOME to a test directory
    monkeypatch.setenv("XDG_CONFIG_HOME", str(test_data_dir / "config"))
    
    # Clean up after tests
    yield
    
    # Clean up test directories
    # Uncomment to clean up after tests
    # if test_data_dir.exists():
    #     import shutil
    #     shutil.rmtree(test_data_dir)

@pytest.fixture
def mock_llm():
    """Create a mock LLM instance."""
    mock = MagicMock()
    mock.chat = AsyncMock(return_value="Mocked response")
    mock.stream_chat = AsyncMock(return_value=["Chunk 1", "Chunk 2"])
    return mock

@pytest.fixture
def mock_llm_factory(mock_llm):
    """Create a mock LLM factory."""
    factory = MagicMock()
    factory.create_llm = MagicMock(return_value=mock_llm)
    return factory

@pytest.fixture
def mock_plugin_manager():
    """Create a mock plugin manager."""
    manager = MagicMock()
    manager._plugins = {}
    manager.register_plugin = MagicMock()
    manager.initialize_plugins = MagicMock()
    manager.cleanup = MagicMock()
    manager.get_plugins_by_type = MagicMock(return_value={})
    return manager

@pytest.fixture
def mock_settings():
    """Create a mock settings object."""
    from xeo.config import Settings
    
    class MockSettings(Settings):
        def __init__(self):
            self.DEBUG = False
            self.LOG_LEVEL = "WARNING"
            self.DATA_DIR = "/tmp/xeo_test_data"
            self.CACHE_DIR = "/tmp/xeo_test_cache"
    
    return MockSettings()

@pytest.fixture
def mock_llm_config():
    """Create a mock LLM config."""
    from xeo.config.providers import LLMConfig, ProviderConfig
    
    config = LLMConfig()
    config.default_provider = "gemini"
    config.providers = {
        "gemini": ProviderConfig(
            enabled=True,
            priority=10,
            config={
                "api_key": "test-api-key",
                "default_model": "gemini-2.0-flash"
            }
        )
    }
    return config
