# Xeo

A modular, scalable, and maintainable framework for building autonomous agent systems.

## Features

- **Agents**: Create and manage autonomous agents with different capabilities
- **Teams**: Form teams of agents with role-based collaboration
- **LLM Integration**: First-class support for large language models (Gemini, etc.)
- **Models**: Integrate various AI/ML models (LLMs, embeddings, etc.)
- **Tools**: Extend agent capabilities with custom tools
- **Memory**: Short-term and long-term memory systems
- **Knowledge**: Knowledge representation and management
- **Workflows**: Define and execute complex agent workflows
- **API**: RESTful API for interacting with the framework
- **Observability**: Built-in monitoring and logging

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/xeo.git
   cd xeo
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Agent Example

```python
from xeo.core.agent import Agent, AgentConfig, AgentType
from xeo.core.team import Team, TeamRole

# Create an agent config
config = AgentConfig(
    name="assistant",
    agent_type=AgentType.AUTONOMOUS,
    description="A helpful assistant agent"
)

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

For more details, see the [LLM Integration Guide](./docs/llm_integration.md).


# Create a team and add the agent
team = Team("engineering")
team.add_member(agent, roles=[TeamRole.MEMBER])

# Execute a task
import asyncio

async def main():
    result = await team.assign_task("research latest AI papers", assignee="assistant")
    print(f"Task result: {result}")

asyncio.run(main())
```

## Project Structure

```
xeo/
├── core/                    # Core framework components
│   ├── __init__.py
│   ├── agent.py             # Base Agent class
│   ├── team.py              # Team management
│   ├── models.py            # Model integration
│   ├── tools.py             # Tool system
│   ├── memory.py            # Memory systems
│   ├── knowledge.py         # Knowledge management
│   ├── workflows.py         # Workflow engine
│   └── ...
├── api/                     # API layer
│   ├── __init__.py
│   ├── endpoints.py
│   └── models.py
├── ui/                      # User interface
│   ├── static/
│   └── templates/
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── logging.py
│   └── helpers.py
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_agent.py
│   └── ...
├── requirements.txt         # Dependencies
└── README.md
```

## Documentation

For detailed documentation, please see the [docs](docs/) directory.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, or suggest features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by various open-source agent frameworks
- Built with ❤️ by the Xeo team