"""
Agent module for the Xeo Framework.

This module defines the base Agent class and related components for creating
and managing autonomous agents.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar


class AgentState(Enum):
    """Represents the possible states of an agent."""
    IDLE = auto()
    THINKING = auto()
    EXECUTING = auto()
    WAITING = auto()
    ERROR = auto()
    COMPLETED = auto()


class AgentType(Enum):
    """Represents the type of an agent."""
    AUTONOMOUS = auto()
    HUMAN_IN_LOOP = auto()
    SUPERVISED = auto()


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    agent_type: AgentType = AgentType.AUTONOMOUS
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    max_iterations: int = 100
    verbose: bool = False


class Agent(ABC):
    """
    Base class for all agents in the framework.
    
    Agents are autonomous entities that can perceive their environment,
    reason about it, and take actions to achieve specific goals.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with the given configuration.
        
        Args:
            config: Configuration for the agent
        """
        self.config = config
        self.state = AgentState.IDLE
        self.memory = {}
        self.iteration_count = 0
        self._observers = []
    
    @abstractmethod
    async def run_task(self, task: str, **kwargs) -> Any:
        """
        Execute a task.
        
        Args:
            task: The task to execute
            **kwargs: Additional arguments for the task
            
        Returns:
            The result of the task execution
        """
        pass
    
    def observe(self, observation: Any) -> None:
        """
        Process an observation from the environment.
        
        Args:
            observation: The observation to process
        """
        self.memory[f"observation_{len(self.memory)}"] = observation
    
    def reflect(self) -> Dict[str, Any]:
        """
        Reflect on past actions and observations.
        
        Returns:
            A dictionary containing reflections
        """
        return {
            "state": self.state,
            "memory_size": len(self.memory),
            "iterations": self.iteration_count
        }
    
    def add_observer(self, observer: callable) -> None:
        """
        Add an observer to be notified of agent state changes.
        
        Args:
            observer: Callable that takes (agent, old_state, new_state) as arguments
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: callable) -> None:
        """
        Remove an observer.
        
        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _set_state(self, new_state: AgentState) -> None:
        """
        Update the agent's state and notify observers.
        
        Args:
            new_state: The new state to set
        """
        old_state = self.state
        self.state = new_state
        for observer in self._observers:
            observer(self, old_state, new_state)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.config.name}', state={self.state.name})"


class AutonomousAgent(Agent):
    """
    An autonomous agent that can perform tasks without human intervention.
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.config.agent_type = AgentType.AUTONOMOUS
    
    async def run_task(self, task: str, **kwargs) -> Any:
        """
        Execute a task autonomously.
        
        Args:
            task: The task to execute
            **kwargs: Additional arguments for the task
            
        Returns:
            The result of the task execution
        """
        self._set_state(AgentState.THINKING)
        try:
            # Implement autonomous task execution logic here
            self._set_state(AgentState.EXECUTING)
            result = f"Executed task: {task} with args: {kwargs}"
            self.iteration_count += 1
            self._set_state(AgentState.COMPLETED)
            return result
        except Exception as e:
            self._set_state(AgentState.ERROR)
            raise RuntimeError(f"Failed to execute task: {e}")
        finally:
            if self.state != AgentState.ERROR:
                self._set_state(AgentState.IDLE)
