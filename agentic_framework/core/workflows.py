"""
Workflows module for the Agentic Framework.

This module defines the Workflow and related classes for managing
sequences of tasks performed by agents.
"""
import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable, Awaitable, Union


class TaskStatus(Enum):
    """Represents the status of a task in a workflow."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class TaskDefinition:
    """Definition of a task within a workflow."""
    name: str
    action: Union[str, Callable]  # Can be a string path or a callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 0
    timeout: Optional[float] = None


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_name: str
    status: TaskStatus
    output: Any = None
    error: Optional[Exception] = None
    execution_time: Optional[float] = None


class Workflow:
    """
    Represents a workflow consisting of multiple tasks.
    
    A workflow defines a sequence of tasks that can be executed by agents,
    with support for dependencies between tasks.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a new workflow.
        
        Args:
            name: Name of the workflow
            description: Optional description of the workflow
        """
        self.name = name
        self.description = description
        self.tasks: Dict[str, TaskDefinition] = {}
        self.results: Dict[str, TaskResult] = {}
    
    def add_task(self, task: TaskDefinition) -> None:
        """
        Add a task to the workflow.
        
        Args:
            task: The task definition to add
            
        Raises:
            ValueError: If a task with the same name already exists
        """
        if task.name in self.tasks:
            raise ValueError(f"Task with name '{task.name}' already exists in the workflow.")
        self.tasks[task.name] = task
    
    def get_task(self, task_name: str) -> Optional[TaskDefinition]:
        """
        Get a task by name.
        
        Args:
            task_name: Name of the task to retrieve
            
        Returns:
            The task definition, or None if not found
        """
        return self.tasks.get(task_name)
    
    def get_ready_tasks(self) -> List[TaskDefinition]:
        """
        Get a list of tasks that are ready to be executed.
        
        A task is ready if all of its dependencies have been completed
        and it's not already running or completed.
        
        Returns:
            List of ready task definitions
        """
        ready_tasks = []
        print(f"\nChecking ready tasks. Current results: {self.results}")
        
        for task in self.tasks.values():
            print(f"\nEvaluating task: {task.name}")
            print(f"Task depends on: {task.depends_on}")
            
            # Skip tasks that are already completed or running
            if task.name in self.results:
                status = self.results[task.name].status
                print(f"Task {task.name} already has result with status: {status}")
                if status in [TaskStatus.COMPLETED, TaskStatus.RUNNING, TaskStatus.FAILED]:
                    print(f"Skipping task {task.name} as it's already {status}")
                    continue
            
            # Check if all dependencies are satisfied
            dependencies_met = True
            for dep in task.depends_on:
                if dep not in self.results:
                    print(f"Dependency {dep} not found in results")
                    dependencies_met = False
                    break
                if self.results[dep].status != TaskStatus.COMPLETED:
                    print(f"Dependency {dep} status is {self.results[dep].status}, not COMPLETED")
                    dependencies_met = False
                    break
            
            print(f"Task {task.name} dependencies met: {dependencies_met}")
            if dependencies_met:
                print(f"Adding {task.name} to ready tasks")
                ready_tasks.append(task)
        
        print(f"Ready tasks: {[t.name for t in ready_tasks]}")
        
        return ready_tasks
    
    def update_task_result(self, result: TaskResult) -> None:
        """
        Update the result of a task.
        
        Args:
            result: The task result to update
        """
        self.results[result.task_name] = result
    
    def is_complete(self) -> bool:
        """
        Check if all tasks in the workflow are complete.
        
        Returns:
            True if all tasks are complete, False otherwise
        """
        if not self.tasks:
            return False
            
        return all(
            task.name in self.results and 
            self.results[task.name].status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for task in self.tasks.values()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the workflow.
        
        Returns:
            Dictionary containing workflow status information
        """
        status_counts = {
            TaskStatus.PENDING.name: 0,
            TaskStatus.RUNNING.name: 0,
            TaskStatus.COMPLETED.name: 0,
            TaskStatus.FAILED.name: 0,
            TaskStatus.CANCELLED.name: 0
        }
        
        for task in self.tasks.values():
            if task.name in self.results:
                status = self.results[task.name].status.name
            else:
                status = TaskStatus.PENDING.name
            status_counts[status] += 1
        
        return {
            "name": self.name,
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "is_complete": self.is_complete()
        }
    
    def __str__(self) -> str:
        return f"Workflow(name='{self.name}', tasks={len(self.tasks)})"


class WorkflowEngine:
    """
    Engine for executing workflows.
    
    The workflow engine is responsible for managing the execution of workflows,
    including task scheduling, dependency resolution, and error handling.
    """
    
    async def execute(self, workflow: Workflow, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow.
        
        Args:
            workflow: The workflow to execute
            context: Context data available to all tasks in the workflow
            
        Returns:
            Dictionary containing the results of the workflow execution
        """
        results = {}
        
        while not workflow.is_complete():
            # Get tasks that are ready to run
            ready_tasks = workflow.get_ready_tasks()
            
            if not ready_tasks:
                # No tasks are ready to run, but workflow isn't complete
                # This indicates a deadlock or circular dependency
                raise RuntimeError("Workflow deadlock detected - no tasks can make progress")
            
            # Execute ready tasks in parallel
            task_results = await asyncio.gather(
                *(self._execute_task(task, context) for task in ready_tasks),
                return_exceptions=True
            )
            
            # Update workflow with task results
            for result in task_results:
                if isinstance(result, Exception):
                    # Handle task execution errors
                    print(f"Error executing task: {result}")
                    continue
                    
                workflow.update_task_result(result)
                results[result.task_name] = {
                    "status": result.status.name,
                    "output": result.output,
                    "error": str(result.error) if result.error else None,
                    "execution_time": result.execution_time
                }
        
        return {
            "workflow_status": "completed",
            "results": results
        }
    
    async def _execute_task(self, task: TaskDefinition, context: Dict[str, Any]) -> TaskResult:
        """
        Execute a single task.
        
        Args:
            task: The task to execute
            context: Context data available to the task
            
        Returns:
            The result of the task execution
        """
        start_time = asyncio.get_event_loop().time()
        result = TaskResult(
            task_name=task.name,
            status=TaskStatus.RUNNING
        )
        
        try:
            # Get the action function from the context
            action_func = self._resolve_action(task.action, context)
            
            # Execute the action with parameters
            if asyncio.iscoroutinefunction(action_func):
                output = await action_func(**task.parameters, **context)
            else:
                # For synchronous functions, run in a thread pool
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(
                    None,
                    lambda: action_func(**task.parameters, **context)
                )
            
            # Update result with success
            result.status = TaskStatus.COMPLETED
            result.output = output
            
        except Exception as e:
            # Update result with failure
            result.status = TaskStatus.FAILED
            result.error = e
            
        # Calculate execution time
        result.execution_time = asyncio.get_event_loop().time() - start_time
        
        return result
    
    def _resolve_action(self, action: Union[str, Callable], context: Dict[str, Any]) -> Callable:
        """
        Resolve an action to a callable function.
        
        Args:
            action: Either a callable or a string path to the action (e.g., 'module.function')
            context: Context to look for the action in
            
        Returns:
            The resolved callable
            
        Raises:
            ValueError: If the action cannot be resolved
        """
        # If action is already callable, return it directly
        if callable(action):
            return action
            
        # Handle string action paths
        if isinstance(action, str):
            # First, try to find the action in the context
            if '.' not in action and action in context:
                resolved_action = context[action]
                if callable(resolved_action):
                    return resolved_action
            
            # Try to resolve as a module path
            try:
                module_path, func_name = action.rsplit('.', 1)
                module = __import__(module_path, fromlist=[func_name])
                return getattr(module, func_name)
            except (ImportError, AttributeError, ValueError) as e:
                raise ValueError(f"Could not resolve action: {action}") from e
        
        raise ValueError(f"Action must be a callable or a string path, got {type(action)}")
