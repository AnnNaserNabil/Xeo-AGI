"""
Reasoning module for the Agentic Framework.

This module provides components for agent reasoning, including inference engines
and planning capabilities.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable, Awaitable
import asyncio


class ReasoningMethod(Enum):
    """Different reasoning methods that can be used by the inference engine."""
    DEDUCTIVE = auto()
    INDUCTIVE = auto()
    ABDUCTIVE = auto()
    ANALOGICAL = auto()
    COMMONSENSE = auto()


@dataclass
class InferenceRule:
    """Represents a rule for making inferences."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], Awaitable[Any]]
    priority: int = 0
    description: str = ""


class InferenceEngine:
    """
    A rule-based inference engine for making logical deductions.
    
    The inference engine applies a set of rules to a knowledge base
    to derive new knowledge or make decisions.
    """
    
    def __init__(self):
        """Initialize the inference engine with an empty set of rules."""
        self.rules: List[InferenceRule] = []
        self.working_memory: Dict[str, Any] = {}
    
    def add_rule(self, rule: InferenceRule) -> None:
        """
        Add a rule to the inference engine.
        
        Args:
            rule: The inference rule to add
        """
        self.rules.append(rule)
        # Keep rules sorted by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule by name.
        
        Args:
            rule_name: Name of the rule to remove
            
        Returns:
            True if the rule was found and removed, False otherwise
        """
        initial_count = len(self.rules)
        self.rules = [r for r in self.rules if r.name != rule_name]
        return len(self.rules) < initial_count
    
    async def execute(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the inference engine with the given context.
        
        Args:
            context: Initial context for the inference
            
        Returns:
            The final context after applying all applicable rules
        """
        if context is None:
            context = {}
            
        self.working_memory = context.copy()
        changed = True
        iteration = 0
        max_iterations = 100  # Prevent infinite loops
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            for rule in self.rules:
                try:
                    # Check if the rule's condition is satisfied
                    if rule.condition(self.working_memory):
                        # Execute the rule's action
                        result = await rule.action(self.working_memory)
                        
                        # Update working memory with the result
                        if isinstance(result, dict):
                            self.working_memory.update(result)
                            changed = True
                        
                        # If the rule is marked as exclusive, stop after it fires
                        if rule.priority == float('inf'):
                            return self.working_memory
                            
                except Exception as e:
                    print(f"Error executing rule '{rule.name}': {e}")
                    continue
        
        return self.working_memory
    
    def clear_rules(self) -> None:
        """Remove all rules from the inference engine."""
        self.rules = []
    
    def get_rule_names(self) -> List[str]:
        """Get the names of all rules in the inference engine."""
        return [rule.name for rule in self.rules]


class Planner:
    """
    A planning component that generates sequences of actions to achieve goals.
    
    The planner uses a goal-directed approach to determine the best sequence
    of actions to achieve a desired state from the current state.
    """
    
    def __init__(self):
        """Initialize the planner with an empty set of actions."""
        self.actions: Dict[str, Callable] = {}
        self.preconditions: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self.effects: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
    
    def add_action(self, 
                  name: str, 
                  action: Callable,
                  preconditions: Callable[[Dict[str, Any]], bool],
                  effects: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Add an action to the planner's repertoire.
        
        Args:
            name: Name of the action
            action: The action function to execute
            preconditions: Function that checks if the action can be executed
            effects: Function that computes the effects of the action
        """
        self.actions[name] = action
        self.preconditions[name] = preconditions
        self.effects[name] = effects
    
    def remove_action(self, name: str) -> bool:
        """
        Remove an action from the planner.
        
        Args:
            name: Name of the action to remove
            
        Returns:
            True if the action was found and removed, False otherwise
        """
        if name in self.actions:
            del self.actions[name]
            del self.preconditions[name]
            del self.effects[name]
            return True
        return False
    
    async def plan(self, 
                  initial_state: Dict[str, Any], 
                  goal_condition: Callable[[Dict[str, Any]], bool],
                  max_depth: int = 10) -> Optional[List[str]]:
        """
        Generate a plan to achieve the goal condition from the initial state.
        
        Args:
            initial_state: The initial state of the world
            goal_condition: Function that checks if the goal has been achieved
            max_depth: Maximum depth of the search tree
            
        Returns:
            A list of action names representing the plan, or None if no plan is found
        """
        # Check if goal is already satisfied
        if goal_condition(initial_state):
            return []
        
        # Use A* search to find a plan
        open_set = [(0, 0, initial_state.copy(), [])]  # (f, g, state, path)
        closed_set = set()
        
        while open_set:
            # Get the state with the lowest f score
            open_set.sort()  # Sort by f score (first element of tuple)
            f, g, current_state, path = open_set.pop(0)
            
            # Check if current state is the goal
            if goal_condition(current_state):
                return path
            
            # Skip if we've already explored this state
            state_key = self._get_state_key(current_state)
            if state_key in closed_set:
                continue
                
            closed_set.add(state_key)
            
            # Check if we've exceeded max depth
            if g >= max_depth:
                continue
            
            # Try all possible actions
            for action_name in self.actions:
                # Check preconditions
                if not self.preconditions[action_name](current_state):
                    continue
                
                # Apply action effects to get new state
                new_state = current_state.copy()
                effects = self.effects[action_name](new_state)
                new_state.update(effects)
                
                # Calculate g and h scores
                new_g = g + 1  # Each action has a cost of 1
                h = self._heuristic(new_state, goal_condition)
                new_f = new_g + h
                
                # Add to open set
                open_set.append((new_f, new_g, new_state, path + [action_name]))
        
        # No plan found
        return None
    
    async def execute_plan(self, plan: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plan in the given context.
        
        Args:
            plan: List of action names to execute
            context: The execution context
            
        Returns:
            The updated context after executing the plan
        """
        for action_name in plan:
            if action_name not in self.actions:
                raise ValueError(f"Unknown action: {action_name}")
            
            # Check preconditions
            if not self.preconditions[action_name](context):
                raise RuntimeError(f"Preconditions not met for action: {action_name}")
            
            # Execute the action
            action = self.actions[action_name]
            if asyncio.iscoroutinefunction(action):
                result = await action(context)
            else:
                result = action(context)
            
            # Apply effects
            if result is not None:
                context.update(result)
            
            # Apply defined effects
            effects = self.effects[action_name](context)
            context.update(effects)
        
        return context
    
    def _heuristic(self, state: Dict[str, Any], goal_condition: Callable[[Dict[str, Any]], bool]) -> int:
        """
        Heuristic function for A* search.
        
        This is a simple implementation that returns 0, making A* equivalent to
        uniform cost search. In a real implementation, this would estimate the
        cost to reach the goal from the given state.
        """
        return 0
    
    def _get_state_key(self, state: Dict[str, Any]) -> str:
        """
        Generate a unique key for a state.
        
        This is used to detect duplicate states during planning.
        """
        # Sort items to ensure consistent ordering
        sorted_items = sorted(state.items(), key=lambda x: x[0])
        return str(sorted_items)
