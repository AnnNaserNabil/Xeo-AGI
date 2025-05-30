# Quick Start Guide

This guide will help you quickly get started with the Xeo framework by walking you through creating and running a simple agent.

## Installation

First, install the framework using pip:

```bash
pip install xeo
```

## Your First Agent

Let's create a simple agent that can respond to greetings:

```python
from xeo import Agent, AgentType

class GreetingAgent(Agent):
    def __init__(self, name):
        super().__init__(name, agent_type=AgentType.AUTONOMOUS)
    
    async def respond(self, message: str) -> str:
        if "hello" in message.lower() or "hi" in message.lower():
            return f"Hello! I'm {self.name}. How can I assist you today?"
        return "I'm not sure how to respond to that."

# Create an instance of the agent
agent = GreetingAgent("Greeter")

# Test the agent
response = await agent.respond("Hello!")
print(response)  # Output: Hello! I'm Greeter. How can I assist you today?
```

## Running a Simple Workflow

Let's create a simple workflow with two agents:

```python
from xeo import Workflow, TaskDefinition

# Create agents
greeter = GreetingAgent("Greeter")

# Define tasks
greet_task = TaskDefinition(
    name="greet",
    action=greeter.respond,
    parameters={"message": "Hello!"}
)

# Create and run workflow
workflow = Workflow("greeting_workflow")
workflow.add_task(greet_task)

# Run the workflow
result = await workflow.run()
print(result["greet"])  # Output: Hello! I'm Greeter. How can I assist you today?
```

## Next Steps

- Learn more about [Agents](../concepts/agents.md)
- Explore [Workflows](../concepts/workflows.md)
- Check out more [Examples](../use_cases/basic/)

## Need Help?

If you run into any issues or have questions, please [open an issue](https://github.com/AnnNaserNabil/Xeo-AGI/issues) on our GitHub repository.
