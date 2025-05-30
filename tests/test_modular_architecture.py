"""
Tests for the Xeo framework's modular architecture.
"""
import os
import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo import (
    init, cleanup,
    get_llm_factory,
    Message, MessageRole,
    get_plugin_manager
)

# Test configuration
TEST_CONFIG = {
    "DEFAULT_LLM_PROVIDER": "gemini",
    "DEFAULT_LLM_MODEL": "gemini-2.0-flash",
    "GOOGLE_API_KEY": "test-api-key",
}

class TestModularArchitecture:
    """Test suite for the modular architecture."""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Set up and tear down tests."""
        # Set up test environment
        for key, value in TEST_CONFIG.items():
            os.environ[key] = value
        
        # Initialize the framework
        init()
        
        yield  # This is where the test runs
        
        # Clean up
        cleanup()
        for key in TEST_CONFIG:
            os.environ.pop(key, None)
    
    @pytest.mark.asyncio
    async def test_llm_factory_initialization(self):
        """Test that the LLM factory is properly initialized."""
        llm_factory = get_llm_factory()
        assert llm_factory is not None
        
        # Verify we can create an LLM instance
        llm = llm_factory.create_llm(
            provider_name="gemini",
            model_name="gemini-2.0-flash"
        )
        assert llm is not None
    
    @pytest.mark.asyncio
    async def test_plugin_system(self):
        """Test that plugins are properly loaded and initialized."""
        plugin_manager = get_plugin_manager()
        
        # Verify at least the Gemini plugin is loaded
        plugins = plugin_manager.get_plugins_by_type("llm_provider")
        assert "gemini" in [p.plugin_info.name.lower() for p in plugins.values()]
    
    @pytest.mark.asyncio
    async def test_chat_completion(self, monkeypatch):
        """Test chat completion with the LLM provider."""
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        
        # Mock the chat method
        mock_chat = AsyncMock(return_value=Message(
            role=MessageRole.ASSISTANT,
            content="This is a test response"
        ))
        
        # Get the LLM factory and create an instance
        llm_factory = get_llm_factory()
        llm = llm_factory.create_llm(
            provider_name="gemini",
            model_name="gemini-2.0-flash"
        )
        
        # Patch the chat method
        monkeypatch.setattr(llm, "chat", mock_chat)
        
        # Test chat completion
        messages = [
            Message(role=MessageRole.USER, content="Hello, how are you?")
        ]
        
        response = await llm.chat(messages)
        
        # Verify the response
        assert response.role == MessageRole.ASSISTANT
        assert "test response" in response.content.lower()
        mock_chat.assert_called_once()

class TestCLICommands:
    """Test suite for CLI commands."""
    
    def test_version_command(self, capsys):
        """Test the version command."""
        from xeo.cli.commands import app
        
        # Mock sys.argv
        with patch("sys.argv", ["xeo", "version"]):
            try:
                app()
            except SystemExit:
                pass
            
            # Capture the output
            captured = capsys.readouterr()
            assert "Xeo Framework" in captured.out
    
    def test_plugins_command(self, capsys):
        """Test the plugins command."""
        from xeo.cli.commands import app
        
        # Mock sys.argv and plugin manager
        with (
            patch("sys.argv", ["xeo", "plugins"]),
            patch("xeo.cli.commands.get_plugin_manager") as mock_pm
        ):
            # Mock plugin manager
            mock_plugin = MagicMock()
            mock_plugin.plugin_info = MagicMock(
                name="test_plugin",
                type=MagicMock(value="test_type"),
                version="1.0.0",
                description="A test plugin"
            )
            mock_pm.return_value._plugins = {"test_plugin": mock_plugin}
            
            try:
                app()
            except SystemExit:
                pass
            
            # Capture the output
            captured = capsys.readouterr()
            assert "Installed Plugins" in captured.out
            assert "test_plugin" in captured.out

if __name__ == "__main__":
    pytest.main(["-v", __file__])
