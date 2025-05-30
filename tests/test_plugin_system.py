# Run all tests
pytest

# Run tests with coverage
pytest --cov=xeo --cov-report=term-missing

# Run a specific test file
pytest tests/test_plugin_system.py -v"""
Tests for the Xeo plugin system.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo.core.plugins import (
    PluginType,
    XeoPlugin,
    PluginInfo,
    PluginManager,
    get_plugin_manager
)

class TestPluginSystem:
    """Test suite for the plugin system."""
    
    def test_plugin_info_creation(self):
        """Test creating a PluginInfo instance."""
        info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test User",
            url="https://example.com/plugin",
            type=PluginType.TOOL
        )
        
        assert info.name == "test_plugin"
        assert info.version == "1.0.0"
        assert info.description == "A test plugin"
        assert info.author == "Test User"
        assert info.url == "https://example.com/plugin"
        assert info.type == PluginType.TOOL
    
    def test_plugin_info_from_dict(self):
        """Test creating a PluginInfo instance from a dictionary."""
        data = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "A test plugin",
            "author": "Test User",
            "url": "https://example.com/plugin",
            "type": "tool"
        }
        
        info = PluginInfo.from_dict(data)
        
        assert info.name == "test_plugin"
        assert info.version == "1.0.0"
        assert info.description == "A test plugin"
        assert info.author == "Test User"
        assert info.url == "https://example.com/plugin"
        assert info.type == PluginType.TOOL
    
    def test_plugin_manager_initialization(self):
        """Test initializing a PluginManager."""
        manager = PluginManager()
        assert len(manager._plugins) == 0
        assert not manager._initialized
    
    def test_register_plugin(self):
        """Test registering a plugin."""
        manager = PluginManager()
        
        class TestPlugin(XeoPlugin):
            def __init__(self):
                self.plugin_info = PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    type=PluginType.TOOL
                )
            
            def initialize(self, **kwargs):
                pass
            
            def cleanup(self):
                pass
        
        plugin = TestPlugin()
        manager.register_plugin(plugin)
        
        assert "test_plugin" in manager._plugins
        assert manager._plugins["test_plugin"] == plugin
    
    def test_register_duplicate_plugin(self):
        """Test registering a duplicate plugin raises an error."""
        manager = PluginManager()
        
        class TestPlugin(XeoPlugin):
            def __init__(self):
                self.plugin_info = PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    type=PluginType.TOOL
                )
            
            def initialize(self, **kwargs):
                pass
            
            def cleanup(self):
                pass
        
        plugin1 = TestPlugin()
        plugin2 = TestPlugin()
        
        manager.register_plugin(plugin1)
        
        with pytest.raises(ValueError, match="Plugin 'test_plugin' is already registered"):
            manager.register_plugin(plugin2)
    
    def test_initialize_plugins(self):
        """Test initializing plugins."""
        manager = PluginManager()
        
        mock_plugin = MagicMock(spec=XeoPlugin)
        mock_plugin.plugin_info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            type=PluginType.TOOL
        )
        
        manager._plugins["test_plugin"] = mock_plugin
        
        manager.initialize_plugins(test_config="value")
        
        mock_plugin.initialize.assert_called_once_with(test_config="value")
        assert manager._initialized
    
    def test_cleanup_plugins(self):
        """Test cleaning up plugins."""
        manager = PluginManager()
        manager._initialized = True
        
        mock_plugin = MagicMock(spec=XeoPlugin)
        mock_plugin.plugin_info = PluginInfo(
            name="test_plugin",
            version="1.0.0",
            type=PluginType.TOOL
        )
        
        manager._plugins["test_plugin"] = mock_plugin
        
        manager.cleanup()
        
        mock_plugin.cleanup.assert_called_once()
        assert len(manager._plugins) == 0
        assert not manager._initialized
    
    def test_get_plugins_by_type(self):
        """Test getting plugins by type."""
        manager = PluginManager()
        
        # Create test plugins
        tool_plugin = MagicMock()
        tool_plugin.plugin_info = PluginInfo(
            name="tool_plugin",
            version="1.0.0",
            type=PluginType.TOOL
        )
        
        llm_plugin = MagicMock()
        llm_plugin.plugin_info = PluginInfo(
            name="llm_plugin",
            version="1.0.0",
            type=PluginType.LLM_PROVIDER
        )
        
        manager._plugins = {
            "tool_plugin": tool_plugin,
            "llm_plugin": llm_plugin
        }
        
        # Test getting tool plugins
        tool_plugins = manager.get_plugins_by_type(PluginType.TOOL)
        assert len(tool_plugins) == 1
        assert "tool_plugin" in tool_plugins
        
        # Test getting LLM plugins
        llm_plugins = manager.get_plugins_by_type(PluginType.LLM_PROVIDER)
        assert len(llm_plugins) == 1
        assert "llm_plugin" in llm_plugins
        
        # Test getting non-existent plugin type
        other_plugins = manager.get_plugins_by_type(PluginType.INTEGRATION)
        assert len(other_plugins) == 0

class TestPluginLoading:
    """Test plugin loading functionality."""
    
    @patch("importlib.import_module")
    @patch("pkgutil.iter_modules")
    def test_load_plugins_from_path(self, mock_iter_modules, mock_import_module):
        """Test loading plugins from a path."""
        # Mock the module iterator
        mock_module = MagicMock()
        mock_module.name = "test_plugin"
        mock_iter_modules.return_value = [
            (None, "test_plugin", False)
        ]
        
        # Mock the imported module
        mock_plugin = MagicMock()
        mock_plugin.TestPlugin = MagicMock()
        mock_plugin.TestPlugin.return_value.plugin_info = MagicMock()
        mock_import_module.return_value = mock_plugin
        
        manager = PluginManager()
        manager._register_plugins_from_module = MagicMock()
        
        manager.load_plugins_from_path("/fake/path")
        
        mock_import_module.assert_called_once_with("test_plugin")
        manager._register_plugins_from_module.assert_called_once_with(mock_plugin)
    
    def test_register_plugins_from_module(self):
        """Test registering plugins from a module."""
        class TestPlugin(XeoPlugin):
            def __init__(self):
                self.plugin_info = PluginInfo(
                    name="test_plugin",
                    version="1.0.0",
                    type=PluginType.TOOL
                )
            
            def initialize(self, **kwargs):
                pass
            
            def cleanup(self):
                pass
        
        # Create a mock module with a plugin class
        mock_module = MagicMock()
        mock_module.TestPlugin = TestPlugin
        
        # Mock the getmembers function to return our test plugin
        with patch("inspect.getmembers") as mock_getmembers:
            mock_getmembers.return_value = [
                ("TestPlugin", TestPlugin),
                ("NotAPlugin", object)
            ]
            
            manager = PluginManager()
            manager._register_plugins_from_module(mock_module)
            
            # Verify the plugin was registered
            assert "test_plugin" in manager._plugins
            assert isinstance(manager._plugins["test_plugin"], TestPlugin)

def test_get_plugin_manager():
    """Test the get_plugin_manager function returns a singleton."""
    manager1 = get_plugin_manager()
    manager2 = get_plugin_manager()
    
    assert manager1 is manager2

if __name__ == "__main__":
    pytest.main(["-v", __file__])
