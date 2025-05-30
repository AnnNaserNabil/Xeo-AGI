"""
Test script demonstrating a complete agent workflow with memory and knowledge.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from xeo.core.agent import Agent, AgentConfig, AgentType, AutonomousAgent, AgentState
from xeo.core.team import Team, TeamRole, CommunicationProtocol
from xeo.core.memory import ShortTermMemory, LongTermMemory, MemoryItem
from xeo.core.knowledge import KnowledgeItem, KnowledgeType, InMemoryKnowledgeBase, KnowledgeManager
from xeo.core.workflows import Workflow, TaskDefinition, TaskStatus, WorkflowEngine


class ResearchAgent(AutonomousAgent):
    """
    A specialized agent for conducting research.
    """
    
    def __init__(self, config):
        """Initialize the research agent with memory and knowledge base."""
        super().__init__(config)
        self.short_term_memory = ShortTermMemory(max_size=100)
        self.long_term_memory = LongTermMemory("research_agent_memory.json")
        self.knowledge_base = InMemoryKnowledgeBase()
        self.knowledge_manager = KnowledgeManager()
        self.knowledge_manager.add_knowledge_base("research", self.knowledge_base, set_as_default=True)
    
    async def run_task(self, task: str, **kwargs) -> Any:
        """
        Execute a research task.
        
        Args:
            task: The task to execute
            **kwargs: Additional parameters
            
        Returns:
            The result of the task
        """
        self._set_state(AgentState.THINKING)
        
        try:
            # Store the task in short-term memory
            task_id = await self.short_term_memory.store(
                content=task,
                task_type="research",
                status="started",
                **kwargs
            )
            
            # Add to knowledge base
            knowledge_item = KnowledgeItem(
                id=f"task_{task_id}",
                content={"description": task, "parameters": kwargs},
                knowledge_type=KnowledgeType.PROCEDURE,
                source="user",
                tags={"task", "research"}
            )
            await self.knowledge_manager.add(knowledge_item)
            
            # Simulate research process
            self._set_state(AgentState.EXECUTING)
            
            # In a real implementation, this would involve actual research
            result = {
                "task": task,
                "status": "completed",
                "findings": [
                    {"source": "source_1", "summary": f"Information about {task}", "relevance": 0.85},
                    {"source": "source_2", "summary": f"Additional details about {task}", "relevance": 0.72},
                ],
                "conclusions": [f"Based on research, {task} is an important topic with several key aspects."],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store results in long-term memory
            await self.long_term_memory.store(
                content=result,
                task=task,
                task_id=task_id,
                type="research_result"
            )
            
            # Update knowledge base with findings
            for i, finding in enumerate(result["findings"]):
                finding_item = KnowledgeItem(
                    id=f"finding_{task_id}_{i}",
                    content=finding,
                    knowledge_type=KnowledgeType.FACT,
                    source=finding["source"],
                    confidence=finding["relevance"],
                    tags={"finding", "research"}
                )
                await self.knowledge_manager.add(finding_item)
                
                # Create relationship between task and finding
                await self.knowledge_manager.relate(
                    source_id=knowledge_item.id,
                    target_id=finding_item.id,
                    relation_type="has_finding",
                    relevance=finding["relevance"]
                )
            
            self.iteration_count += 1
            self._set_state(AgentState.COMPLETED)
            return result
            
        except Exception as e:
            self._set_state(AgentState.ERROR)
            print(f"Error in research task: {e}")
            raise
        finally:
            if self.state != AgentState.ERROR:
                self._set_state(AgentState.IDLE)


class AnalysisAgent(AutonomousAgent):
    """
    A specialized agent for analyzing research findings.
    """
    
    def __init__(self, config):
        """Initialize the analysis agent."""
        super().__init__(config)
        self.short_term_memory = ShortTermMemory(max_size=100)
        self.knowledge_base = InMemoryKnowledgeBase()
    
    async def analyze_research(self, research_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Analyze research findings.
        
        Args:
            research_data: The research data to analyze
            **kwargs: Additional context parameters (ignored)
            
        Returns:
            Analysis results
        """
        self._set_state(AgentState.THINKING)
        
        try:
            # Store the analysis task
            task_id = await self.short_term_memory.store(
                content="Analyze research findings",
                research_topic=research_data.get("task", ""),
                status="started"
            )
            
            # In a real implementation, this would involve actual analysis
            self._set_state(AgentState.EXECUTING)
            
            # Simulate analysis
            analysis = {
                "task": f"Analyze research on '{research_data.get('task', '')}'",
                "key_insights": [
                    f"The research covers {len(research_data.get('findings', []))} key points about {research_data.get('task', 'the topic')}.",
                    "Several sources provide consistent information on this topic.",
                    "The overall quality of information is good, with relevance scores above 0.7."
                ],
                "recommendations": [
                    "Consider exploring related subtopics for a more comprehensive understanding.",
                    "Verify the most relevant findings with additional sources."
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.iteration_count += 1
            self._set_state(AgentState.COMPLETED)
            return analysis
            
        except Exception as e:
            self._set_state(AgentState.ERROR)
            print(f"Error in analysis: {e}")
            raise
        finally:
            if self.state != AgentState.ERROR:
                self._set_state(AgentState.IDLE)


async def main():
    """Run the complete agent workflow."""
    print("=== Starting Agent Workflow Test ===\n")
    
    # Create a team
    team = Team("research_team", description="Team for conducting and analyzing research")
    
    # Create and add agents to the team
    research_agent = ResearchAgent(
        AgentConfig(
            name="researcher",
            agent_type=AgentType.AUTONOMOUS,
            description="Agent specialized in conducting research",
            capabilities=["web_search", "document_analysis", "information_synthesis"]
        )
    )
    
    analysis_agent = AnalysisAgent(
        AgentConfig(
            name="analyst",
            agent_type=AgentType.AUTONOMOUS,
            description="Agent specialized in analyzing research findings",
            capabilities=["data_analysis", "insight_generation", "reporting"]
        )
    )
    
    team.add_member(research_agent, roles=[TeamRole.MEMBER], capabilities=["research"])
    team.add_member(analysis_agent, roles=[TeamRole.REVIEWER], capabilities=["analysis"])
    
    # Create a workflow
    workflow = Workflow("research_workflow", "Workflow for conducting and analyzing research")
    
    # Define tasks with direct method references
    research_task = TaskDefinition(
        name="conduct_research",
        action=research_agent.run_task,
        parameters={
            "task": "the impact of AI on software development",
            "depth": "detailed"
        }
    )
    
    analysis_task = TaskDefinition(
        name="analyze_findings",
        action=analysis_agent.analyze_research,
        parameters={"research_data": {"task": "the impact of AI on software development"}},
        depends_on=["conduct_research"]
    )
    
    # Add tasks to workflow
    workflow.add_task(research_task)
    workflow.add_task(analysis_task)
    
    # Create workflow engine
    workflow_engine = WorkflowEngine()
    
    # Execute workflow
    print("Executing research workflow...\n")
    
    # Create a context with the agent instances directly accessible
    context = {
        "researcher": research_agent,
        "analyst": analysis_agent,
        "tasks": {}
    }
    
    results = await workflow_engine.execute(workflow, context)
    
    # Print results
    print("\n=== Workflow Execution Results ===\n")
    print(json.dumps(results, indent=2, default=str))
    
    # Demonstrate memory and knowledge access
    print("\n=== Agent Memory and Knowledge ===\n")
    
    # Show research agent's memory
    research_memories = await research_agent.short_term_memory.retrieve(limit=3)
    print(f"Researcher's recent memories ({len(research_memories)}):")
    for i, mem in enumerate(research_memories, 1):
        print(f"  {i}. {mem.content}")
    
    # Show knowledge base contents
    research_items = await research_agent.knowledge_manager.search("", limit=3)
    print(f"\nKnowledge base items ({len(research_items)}):")
    for i, item in enumerate(research_items, 1):
        print(f"  {i}. {item.content}")
    
    print("\n=== Test Completed Successfully ===")


if __name__ == "__main__":
    asyncio.run(main())
