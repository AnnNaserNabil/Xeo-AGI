# Single Agent Use Case

This guide demonstrates how to create and use a single autonomous agent with the Xeo framework capabilities.

## Overview

We'll create a `ResearchAgent` that can:
1. Accept research topics
2. Simulate gathering information
3. Return structured findings

## Implementation

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
from xeo import Agent, AgentType, AgentState

@dataclass
class ResearchFinding:
    source: str
    summary: str
    relevance: float

class ResearchAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name, agent_type=AgentType.AUTONOMOUS)
        self.state = AgentState.IDLE
        
    async def research_topic(self, topic: str, depth: str = "basic") -> Dict:
        """
        Simulate researching a topic.
        
        Args:
            topic: The topic to research
            depth: Research depth (basic, detailed, comprehensive)
            
        Returns:
            Dict containing research findings
        """
        self._set_state(AgentState.THINKING)
        
        # Simulate research time based on depth
        research_time = {
            "basic": 1.0,
            "detailed": 2.0,
            "comprehensive": 5.0
        }.get(depth, 1.0)
        
        # Simulate finding information
        findings = [
            ResearchFinding(
                source=f"source_{i+1}",
                summary=f"Information about {topic} from source {i+1}",
                relevance=0.9 - (i * 0.1)
            ) for i in range(3)
        ]
        
        self._set_state(AgentState.COMPLETED)
        
        return {
            "topic": topic,
            "status": "completed",
            "findings": [f.__dict__ for f in findings],
            "conclusions": [f"Based on research, {topic} is an important topic with several key aspects."]
        }
```

## Usage

```python
import asyncio

async def main():
    # Create and use the research agent
    researcher = ResearchAgent("Researcher")
    
    # Conduct research
    results = await researcher.research_topic(
        topic="the impact of AI on software development",
        depth="detailed"
    )
    
    # Print results
    print(f"Research on: {results['topic']}")
    print(f"Status: {results['status']}")
    print("\nFindings:")
    for finding in results['findings']:
        print(f"- {finding['summary']} (Relevance: {finding['relevance']:.2f})")
    
    print("\nConclusions:")
    for conclusion in results['conclusions']:
        print(f"- {conclusion}")

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

## Expected Output

```
Research on: the impact of AI on software development
Status: completed

Findings:
- Information about the impact of AI on software development from source 1 (Relevance: 0.90)
- Information about the impact of AI on software development from source 2 (Relevance: 0.80)
- Information about the impact of AI on software development from source 3 (Relevance: 0.70)

Conclusions:
- Based on research, the impact of AI on software development is an important topic with several key aspects.
```

## Key Features Demonstrated

1. **Agent Creation**: Creating a custom agent by inheriting from the base `Agent` class
2. **State Management**: Using `AgentState` to track the agent's current state
3. **Asynchronous Operations**: Using `async/await` for non-blocking operations
4. **Structured Output**: Returning structured data from agent methods
5. **Type Hints**: Using Python type hints for better code clarity and IDE support

## Next Steps

- Learn how to [extend agents with tools](../agent_with_tools.md)
- Explore [multi-agent systems](../../advanced/multi_agent_system.md)
- See how to [create custom workflows](../../concepts/workflows.md)
