"""
Application module for the Agentic Framework.

This module defines the Application class for managing agent applications.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .agent import Agent
from .workflows import Workflow, WorkflowEngine


@dataclass
class ApplicationConfig:
    """Configuration for an application."""
    name: str
    description: str = ""
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class Application:
    """
    Represents an application that uses agents to achieve specific goals.
    
    An application is a collection of agents, workflows, and resources
    that work together to solve a particular problem or provide a service.
    """
    
    def __init__(self, config: ApplicationConfig):
        """
        Initialize the application.
        
        Args:
            config: Configuration for the application
        """
        self.config = config
        self.agents: Dict[str, Agent] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.workflow_engine = WorkflowEngine()
        self.resources: Dict[str, Any] = {}
    
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the application.
        
        Args:
            agent: The agent to add
            
        Raises:
            ValueError: If an agent with the same name already exists
        """
        if agent.config.name in self.agents:
            raise ValueError(f"Agent with name '{agent.config.name}' already exists in the application.")
        self.agents[agent.config.name] = agent
    
    def remove_agent(self, agent_name: str) -> None:
        """
        Remove an agent from the application.
        
        Args:
            agent_name: Name of the agent to remove
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
    
    def add_workflow(self, workflow: Workflow) -> None:
        """
        Add a workflow to the application.
        
        Args:
            workflow: The workflow to add
            
        Raises:
            ValueError: If a workflow with the same name already exists
        """
        if workflow.name in self.workflows:
            raise ValueError(f"Workflow with name '{workflow.name}' already exists in the application.")
        self.workflows[workflow.name] = workflow
    
    async def execute_workflow(self, workflow_name: str, input_data: Optional[Dict] = None) -> Any:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            input_data: Optional input data for the workflow
            
        Returns:
            The result of the workflow execution
            
        Raises:
            ValueError: If the workflow is not found
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found.")
        
        workflow = self.workflows[workflow_name]
        context = {
            "application": self,
            "agents": self.agents,
            "resources": self.resources,
            "input": input_data or {}
        }
        
        return await self.workflow_engine.execute(workflow, context)
    
    def add_resource(self, name: str, resource: Any) -> None:
        """
        Add a resource to the application.
        
        Args:
            name: Name of the resource
            resource: The resource to add
        """
        self.resources[name] = resource
    
    def get_resource(self, name: str) -> Any:
        """
        Get a resource by name.
        
        Args:
            name: Name of the resource to retrieve
            
        Returns:
            The requested resource, or None if not found
        """
        return self.resources.get(name)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the application.
        
        Returns:
            Dictionary containing application status information
        """
        return {
            "name": self.config.name,
            "version": self.config.version,
            "agent_count": len(self.agents),
            "workflow_count": len(self.workflows),
            "resource_count": len(self.resources)
        }
    
    def __str__(self) -> str:
        return f"Application(name='{self.config.name}', agents={len(self.agents)}, workflows={len(self.workflows)})"
