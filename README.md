# Xeo Framework

A modular, scalable, and maintainable framework for building autonomous agent systems with a focus on flexibility and extensibility.

## 🚀 Key Features

- **Modular Architecture**: Easily extendable with plugins for LLMs, tools, and more
- **Agent System**: Create and manage autonomous agents with different capabilities
- **Plugin System**: Dynamic loading of components at runtime
- **LLM Integration**: First-class support for multiple LLM providers (Gemini, OpenAI, etc.)
- **Configuration Management**: Centralized configuration with environment variable support
- **Type Safety**: Full type hints and runtime type checking with Pydantic
- **Async by Default**: Built with asyncio for high-performance concurrent operations

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/xeoai/xeo-framework.git
   cd xeo-framework
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .[llm]  # Install with LLM support
   ```

## 🚀 Quick Start

### Using the Framework

```python
import asyncio
from xeo import (
    init, cleanup,
    get_llm_factory,
    Message, MessageRole
)

async def main():
    # Initialize the framework
    init()
    
    try:
        # Get the LLM factory
        llm_factory = get_llm_factory()
        
        # Create a Gemini LLM instance
        gemini_llm = llm_factory.create_llm(
            provider_name="gemini",
            model_name="gemini-2.0-flash"
        )
        
        # Test the LLM
        messages = [
            Message(role=MessageRole.USER, content="Hello, how are you?")
        ]
        
        response = await gemini_llm.chat(messages)
        print(f"Response: {response.content}")
        
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🧩 Plugin System

Xeo's plugin system allows you to extend the framework with new functionality:

### Creating a Plugin

```python
from xeo.core.plugins import PluginType, XeoPlugin, PluginInfo

class MyPlugin(XeoPlugin):
    """Example plugin that extends Xeo's functionality."""
    
    def __init__(self):
        self.plugin_info = PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="An example plugin for Xeo",
            author="Your Name",
            url="https://example.com/my_plugin",
            type=PluginType.TOOL
        )
    
    def initialize(self, **kwargs):
        print(f"Initializing {self.plugin_info.name}")
    
    def cleanup(self):
        print(f"Cleaning up {self.plugin_info.name}")
```

### Registering a Plugin

```python
from xeo.core.plugins import get_plugin_manager

# Create and register the plugin
plugin = MyPlugin()
plugin_manager = get_plugin_manager()
plugin_manager.register_plugin(plugin)

# Initialize all registered plugins
plugin_manager.initialize_plugins()
```

## ⚙️ Configuration

Xeo can be configured using environment variables or a `.env` file:

```env
# Core settings
XEO_LOG_LEVEL=INFO
XEO_DEBUG=false

# LLM settings
GOOGLE_API_KEY=your-api-key
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.0-flash
```

## 📚 Documentation

For detailed documentation, please visit our [documentation site](https://xeo.ai/docs).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Create an agent
agent = Agent(config)
```

### LLM Integration Example

```python
import asyncio
from xeo.llm import create_llm, LLMType

async def main():
    # Initialize the Gemini LLM
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro",
        api_key="your-google-api-key"  # Or use environment variable GOOGLE_API_KEY
    )
    
    # Generate text
    response = await gemini.generate("Tell me a joke about programming.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

For detailed documentation, please see the [docs](./docs) directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
