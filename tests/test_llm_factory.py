"""
Tests for the Xeo LLM factory and provider system.
"""
import sys
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo.llm.llm_factory import LLMFactory, get_llm_factory, llm_factory
from xeo.llm.base import BaseLLM, LLMType, Message, MessageRole
from xeo.core.plugins import PluginInfo, PluginType

class MockLLMProvider(BaseLLM):
    """Mock LLM provider for testing."""
    
    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.model_name = model_name
        self.kwargs = kwargs
    
    async def chat(self, messages, **generation_kwargs):
        """Mock chat method."""
        return Message(role=MessageRole.ASSISTANT, content="Mock response")
    
    async def stream_chat(self, messages, **generation_kwargs):
        """Mock stream_chat method."""
        yield Message(role=MessageRole.ASSISTANT, content="Mock ")
        yield Message(role=MessageRole.ASSISTANT, content="response")
    
    def get_model_info(self):
        """Mock get_model_info method."""
        return {
            "provider": "mock",
            "model": self.model_name,
            "capabilities": ["chat", "streaming"]
        }
    
    @classmethod
    def get_provider_type(cls) -> LLMType:
        """Get the provider type."""
        return LLMType.MOCK

class TestLLMFactory:
    """Test suite for the LLM factory."""
    
    def test_llm_factory_initialization(self):
        """Test initializing the LLM factory."""
        factory = LLMFactory()
        assert isinstance(factory._providers, dict)
        assert len(factory._providers) == 0
    
    def test_register_provider(self):
        """Test registering a provider."""
        factory = LLMFactory()
        factory.register_provider(LLMType.MOCK, MockLLMProvider)
        
        assert LLMType.MOCK in factory._providers
        assert factory._providers[LLMType.MOCK] == MockLLMProvider
    
    def test_register_duplicate_provider(self):
        """Test registering a duplicate provider raises an error."""
        factory = LLMFactory()
        factory.register_provider(LLMType.MOCK, MockLLMProvider)
        
        with pytest.raises(ValueError, match="Provider 'mock' is already registered"):
            factory.register_provider(LLMType.MOCK, MockLLMProvider)
    
    def test_create_llm(self):
        """Test creating an LLM instance."""
        factory = LLMFactory()
        factory.register_provider(LLMType.MOCK, MockLLMProvider)
        
        llm = factory.create_llm(
            provider_name="mock",
            model_name="test-model",
            api_key="test-key",
            temperature=0.7
        )
        
        assert isinstance(llm, MockLLMProvider)
        assert llm.model_name == "test-model"
        assert llm.kwargs["api_key"] == "test-key"
        assert llm.kwargs["temperature"] == 0.7
    
    def test_create_llm_invalid_provider(self):
        """Test creating an LLM with an invalid provider raises an error."""
        factory = LLMFactory()
        
        with pytest.raises(ValueError, match="No provider registered for type: invalid"):
            factory.create_llm(provider_name="invalid", model_name="test-model")
    
    @pytest.mark.asyncio
    async def test_llm_chat(self):
        """Test chat functionality with the LLM."""
        factory = LLMFactory()
        factory.register_provider(LLMType.MOCK, MockLLMProvider)
        
        llm = factory.create_llm(provider_name="mock", model_name="test-model")
        
        messages = [
            Message(role=MessageRole.USER, content="Hello")
        ]
        
        response = await llm.chat(messages)
        
        assert response.role == MessageRole.ASSISTANT
        assert response.content == "Mock response"
    
    @pytest.mark.asyncio
    async def test_llm_stream_chat(self):
        """Test streaming chat functionality with the LLM."""
        factory = LLMFactory()
        factory.register_provider(LLMType.MOCK, MockLLMProvider)
        
        llm = factory.create_llm(provider_name="mock", model_name="test-model")
        
        messages = [
            Message(role=MessageRole.USER, content="Hello")
        ]
        
        chunks = []
        async for chunk in llm.stream_chat(messages):
            chunks.append(chunk.content)
        
        assert len(chunks) == 2
        assert "".join(chunks) == "Mock response"

def test_get_llm_factory():
    """Test the get_llm_factory function returns a singleton."""
    factory1 = get_llm_factory()
    factory2 = get_llm_factory()
    
    assert factory1 is factory2
    assert factory1 is llm_factory

class TestLLMPluginIntegration:
    """Test integration between LLM factory and plugin system."""
    
    def test_llm_plugin_registration(self):
        """Test that LLM plugins are registered with the factory."""
        from xeo.llm.plugin import LLMProviderPlugin, register_llm_provider
        
        # Create a test provider class
        class TestLLMProvider(BaseLLM):
            def __init__(self, model_name: str, **kwargs):
                super().__init__(model_name, **kwargs)
            
            async def chat(self, messages, **generation_kwargs):
                return Message(role=MessageRole.ASSISTANT, content="Test response")
            
            async def stream_chat(self, messages, **generation_kwargs):
                yield Message(role=MessageRole.ASSISTANT, content="Test response")
            
            def get_model_info(self):
                return {"provider": "test", "model": self.model_name}
            
            @classmethod
            def get_provider_type(cls) -> LLMType:
                return LLMType.TEST
        
        # Create and register a plugin for the test provider
        plugin = LLMProviderPlugin(
            provider_class=TestLLMProvider,
            provider_type=LLMType.TEST,
            plugin_info=PluginInfo(
                name="test_provider",
                version="1.0.0",
                type=PluginType.LLM_PROVIDER,
                description="Test LLM provider"
            )
        )
        
        # Initialize the plugin (which should register the provider)
        plugin.initialize()
        
        # Verify the provider was registered with the factory
        factory = get_llm_factory()
        assert LLMType.TEST in factory._providers
        assert factory._providers[LLMType.TEST] == TestLLMProvider
        
        # Clean up
        plugin.cleanup()
        
        # Verify the provider was unregistered
        assert LLMType.TEST not in factory._providers

if __name__ == "__main__":
    pytest.main(["-v", __file__])
