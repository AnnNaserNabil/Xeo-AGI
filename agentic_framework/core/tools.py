"""
Tools module for the Agentic Framework.

This module defines the base Tool class and ToolRegistry for managing
tools that agents can use to interact with the environment or perform tasks.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, TypeVar, Callable, Awaitable


class ToolCategory(Enum):
    """Categories for organizing tools."""
    SEARCH = auto()
    DATA_PROCESSING = auto()
    FILE_OPERATIONS = auto()
    NETWORK = auto()
    SYSTEM = auto()
    CUSTOM = auto()


@dataclass
class ToolConfig:
    """Configuration for a tool."""
    name: str
    description: str
    category: ToolCategory = ToolCategory.CUSTOM
    version: str = "1.0.0"
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required_resources: List[str] = field(default_factory=list)
    is_safe: bool = True
    requires_confirmation: bool = False


class Tool(ABC):
    """
    Base class for all tools in the framework.
    
    Tools are used by agents to perform specific tasks or interact with
    external systems. Each tool should implement the execute method.
    """
    
    def __init__(self, config: ToolConfig):
        """
        Initialize the tool with the given configuration.
        
        Args:
            config: Configuration for the tool
        """
        self.config = config
        self._is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the tool and any required resources."""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources used by the tool."""
        pass
    
    @abstractmethod
    async def execute(self, input_data: Any, **kwargs) -> Any:
        """
        Execute the tool with the given input and parameters.
        
        Args:
            input_data: Input data for the tool
            **kwargs: Additional parameters for the tool
            
        Returns:
            The result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the tool's parameters.
        
        Returns:
            Dictionary describing the tool's parameter schema
        """
        return {
            "name": self.config.name,
            "description": self.config.description,
            "category": self.config.category.name,
            "version": self.config.version,
            "parameters": self.config.parameters,
            "required_resources": self.config.required_resources,
            "is_safe": self.config.is_safe,
            "requires_confirmation": self.config.requires_confirmation
        }
    
    @property
    def is_initialized(self) -> bool:
        """Check if the tool is initialized and ready to use."""
        return self._is_initialized
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.config.name}', category={self.config.category.name})"


class FunctionTool(Tool):
    """
    A tool that wraps a Python function.
    
    This allows any callable to be used as a tool without creating a full Tool subclass.
    """
    
    def __init__(self, 
                 name: str, 
                 func: Callable[..., Awaitable[Any]],
                 description: str = "",
                 category: ToolCategory = ToolCategory.CUSTOM,
                 parameters: Optional[Dict[str, Dict[str, Any]]] = None,
                 **kwargs):
        """
        Initialize the function tool.
        
        Args:
            name: Name of the tool
            func: The function to wrap
            description: Description of what the tool does
            category: Category of the tool
            parameters: Schema for the function's parameters
            **kwargs: Additional arguments for ToolConfig
        """
        config = ToolConfig(
            name=name,
            description=description or func.__doc__ or "",
            category=category,
            parameters=parameters or {},
            **kwargs
        )
        super().__init__(config)
        self._func = func
    
    async def initialize(self) -> None:
        """Initialize the function tool."""
        self._is_initialized = True
    
    async def cleanup(self) -> None:
        """Clean up resources used by the function tool."""
        self._is_initialized = False
    
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the wrapped function.
        
        Args:
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
        """
        if not self._is_initialized:
            await self.initialize()
        
        try:
            result = await self._func(*args, **kwargs)
            return result
        except Exception as e:
            raise RuntimeError(f"Error executing tool '{self.config.name}': {e}")


class ToolRegistry:
    """
    Registry for managing tools in the framework.
    
    The registry provides a central place to register, retrieve, and manage
    different tools that agents can use.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}
        self._tool_classes: Dict[str, Type[Tool]] = {}
    
    def register_tool_class(self, tool_class: Type[Tool], name: Optional[str] = None) -> None:
        """
        Register a tool class with the registry.
        
        Args:
            tool_class: The tool class to register
            name: Optional name to register the class under. If not provided,
                  the class's __name__ will be used.
        """
        name = name or tool_class.__name__
        self._tool_classes[name] = tool_class
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool instance with the registry.
        
        Args:
            tool: The tool instance to register
            
        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.config.name in self._tools:
            raise ValueError(f"Tool with name '{tool.config.name}' is already registered.")
        
        self._tools[tool.config.name] = tool
    
    def create_tool(self, config: ToolConfig, tool_class_name: Optional[str] = None) -> Tool:
        """
        Create a new tool instance.
        
        Args:
            config: Configuration for the tool
            tool_class_name: Name of the tool class to use. If not provided,
                           the tool type from config will be used.
                           
        Returns:
            A new tool instance
            
        Raises:
            ValueError: If the tool class is not found
        """
        if tool_class_name is None:
            # Default tool class based on category
            tool_class_name = f"{config.category.name.capitalize()}Tool"
        
        tool_class = self._tool_classes.get(tool_class_name)
        if tool_class is None:
            # Fall back to base Tool class if specific class not found
            tool_class = Tool
        
        return tool_class(config)
    
    async def initialize_tool(self, config: ToolConfig) -> Tool:
        """
        Create and initialize a tool.
        
        Args:
            config: Configuration for the tool
            
        Returns:
            The initialized tool instance
        """
        tool = self.create_tool(config)
        await tool.initialize()
        self._tools[config.name] = tool
        return tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The tool instance, or None if not found
        """
        return self._tools.get(name)
    
    async def cleanup_tool(self, name: str) -> None:
        """
        Clean up a tool and remove it from the registry.
        
        Args:
            name: Name of the tool to clean up
        """
        tool = self._tools.get(name)
        if tool is not None:
            await tool.cleanup()
            del self._tools[name]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered tool classes.
        
        Returns:
            List of tool class information dictionaries
        """
        return [{"name": name, "class": cls.__name__} 
               for name, cls in self._tool_classes.items()]
    
    def list_loaded_tools(self) -> List[Dict[str, Any]]:
        """
        Get information about all loaded tools.
        
        Returns:
            List of loaded tool information dictionaries
        """
        return [{"name": name, "info": tool.get_schema()} 
               for name, tool in self._tools.items()]
