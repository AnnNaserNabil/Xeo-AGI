"""
Team module for the Agentic Framework.

This module defines the Team class and related components for managing
groups of agents and their interactions.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Any

from .agent import Agent, AgentState


class TeamRole(Enum):
    """Represents possible roles within a team."""
    LEADER = auto()
    MEMBER = auto()
    SPECIALIST = auto()
    REVIEWER = auto()


class CommunicationProtocol(Enum):
    """Represents available communication protocols for team interactions."""
    BROADCAST = auto()
    DIRECT = auto()
    HIERARCHICAL = auto()
    BROKERED = auto()


@dataclass
class TeamMember:
    """Represents a member of a team."""
    agent: Agent
    roles: Set[TeamRole] = field(default_factory=set)
    capabilities: Set[str] = field(default_factory=set)


class Team:
    """
    A team of agents that can work together to achieve common goals.
    
    Teams facilitate collaboration between agents by managing communication,
    task delegation, and conflict resolution.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new team.
        
        Args:
            name: Name of the team
            description: Optional description of the team
        """
        self.name = name
        self.description = description
        self.members: Dict[str, TeamMember] = {}
        self.communication_protocol = CommunicationProtocol.BROADCAST
        self._message_queue = []
        self._task_queue = []
    
    def add_member(self, agent: Agent, roles: Optional[List[TeamRole]] = None,
                  capabilities: Optional[List[str]] = None) -> None:
        """
        Add an agent to the team.
        
        Args:
            agent: The agent to add
            roles: List of roles for the agent in the team
            capabilities: List of capabilities the agent brings to the team
        """
        if agent.config.name in self.members:
            raise ValueError(f"Agent '{agent.config.name}' is already a member of this team.")
        
        member_roles = set(roles) if roles else {TeamRole.MEMBER}
        member_capabilities = set(capabilities) if capabilities else set()
        
        self.members[agent.config.name] = TeamMember(
            agent=agent,
            roles=member_roles,
            capabilities=member_capabilities
        )
        
        # Add team observer to the agent
        agent.add_observer(self._on_agent_state_change)
    
    def remove_member(self, agent_name: str) -> None:
        """
        Remove an agent from the team.
        
        Args:
            agent_name: Name of the agent to remove
        """
        if agent_name in self.members:
            agent = self.members[agent_name].agent
            agent.remove_observer(self._on_agent_state_change)
            del self.members[agent_name]
    
    async def broadcast(self, message: Any, sender: Optional[str] = None) -> None:
        """
        Broadcast a message to all team members.
        
        Args:
            message: The message to broadcast
            sender: Optional name of the sending agent
        """
        for member_name, member in self.members.items():
            if member_name != sender:  # Don't send the message back to the sender
                await self._send_message(member_name, message, sender)
    
    async def send_message(self, recipient: str, message: Any, sender: Optional[str] = None) -> None:
        """
        Send a message to a specific team member.
        
        Args:
            recipient: Name of the recipient agent
            message: The message to send
            sender: Optional name of the sending agent
        """
        if recipient not in self.members:
            raise ValueError(f"No member with name '{recipient}' in the team.")
        
        await self._send_message(recipient, message, sender)
    
    async def _send_message(self, recipient: str, message: Any, sender: Optional[str] = None) -> None:
        """Internal method to handle message delivery."""
        try:
            # In a real implementation, this would handle different communication protocols
            # and message serialization/deserialization
            recipient_agent = self.members[recipient].agent
            recipient_agent.observe({
                "type": "message",
                "from": sender,
                "content": message,
                "timestamp": self._get_timestamp()
            })
        except Exception as e:
            print(f"Failed to send message to {recipient}: {e}")
    
    async def assign_task(self, task: str, assignee: str, **kwargs) -> Any:
        """
        Assign a task to a specific team member.
        
        Args:
            task: The task to assign
            assignee: Name of the agent to assign the task to
            **kwargs: Additional arguments for the task
            
        Returns:
            The result of the task execution
        """
        if assignee not in self.members:
            raise ValueError(f"No member with name '{assignee}' in the team.")
        
        member = self.members[assignee]
        if member.agent.state != AgentState.IDLE:
            raise RuntimeError(f"Agent '{assignee}' is not available to take new tasks.")
        
        # Add task to the queue and process it
        self._task_queue.append((task, assignee, kwargs))
        return await self._process_next_task()
    
    async def _process_next_task(self) -> Any:
        """Process the next task in the queue."""
        if not self._task_queue:
            return None
        
        task, assignee, kwargs = self._task_queue.pop(0)
        member = self.members[assignee]
        
        try:
            result = await member.agent.run_task(task, **kwargs)
            return result
        except Exception as e:
            print(f"Error processing task '{task}' by {assignee}: {e}")
            raise
    
    def get_member_status(self, member_name: str) -> Dict[str, Any]:
        """
        Get the status of a team member.
        
        Args:
            member_name: Name of the team member
            
        Returns:
            Dictionary containing status information
        """
        if member_name not in self.members:
            raise ValueError(f"No member with name '{member_name}' in the team.")
        
        member = self.members[member_name]
        return {
            "name": member_name,
            "state": member.agent.state.name,
            "roles": [role.name for role in member.roles],
            "capabilities": list(member.capabilities),
            "memory_size": len(member.agent.memory)
        }
    
    def _on_agent_state_change(self, agent: Agent, old_state: AgentState, new_state: AgentState) -> None:
        """
        Handle agent state changes.
        
        Args:
            agent: The agent whose state changed
            old_state: Previous state
            new_state: New state
        """
        # In a real implementation, this would handle state change events
        # such as notifying other team members, logging, etc.
        if new_state == AgentState.ERROR:
            print(f"Agent {agent.config.name} encountered an error.")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def __str__(self) -> str:
        return f"Team(name='{self.name}', members={len(self.members)})"
