"""
Base module for LLM providers in the Xeo Framework.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, AsyncGenerator, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field

# Type variable for generic response types
T = TypeVar('T')

class StreamProtocol(Generic[T]):
    """Protocol for streaming responses."""
    async def __aiter__(self):
        ...
    
    async def __anext__(self) -> T:
        ...

class FunctionCall(BaseModel):
    """A function call request from the model."""
    name: str = Field(..., description="The name of the function to call.")
    arguments: Dict[str, Any] = Field(..., description="The arguments to call the function with, as a JSON object.")

class ToolCall(BaseModel):
    """A tool call request from the model."""
    id: str = Field(..., description="The ID of the tool call.")
    type: str = Field(..., description="The type of the tool call.")
    function: FunctionCall = Field(..., description="The function call details.")

class LLMType(str, Enum):
    """Supported LLM types."""
    GEMINI = "gemini"
    OPENAI = "openai"
    HUGGINGFACE = "huggingface"

class MessageRole(str, Enum):
    """Roles for chat messages."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"

@dataclass
class Message:
    """A message in a chat conversation."""
    role: MessageRole
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result = {
            "role": self.role.value,
            "content": self.content or ""
        }
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result

class LLMError(Exception):
    """Base exception for LLM-related errors."""
    pass

class BaseLLM(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, model_name: str, **kwargs):
        """
        Initialize the LLM.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Provider-specific arguments
        """
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    async def generate(
        self,
        prompt: Union[str, List[Message]],
        **generation_kwargs
    ) -> str:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The prompt or list of messages
            **generation_kwargs: Generation parameters
                - temperature: Controls randomness (0.0 to 1.0)
                - max_tokens: Maximum number of tokens to generate
                - top_p: Nucleus sampling parameter
                - top_k: Top-k sampling parameter
                - stop_sequences: List of strings to stop generation
                - presence_penalty: Penalty for new tokens based on presence in the text
                - frequency_penalty: Penalty for new tokens based on frequency in the text
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        **generation_kwargs
    ) -> Message:
        """
        Generate a chat completion.
        
        Args:
            messages: List of messages in the conversation
            **generation_kwargs: Generation parameters
                - temperature: Controls randomness (0.0 to 1.0)
                - max_tokens: Maximum number of tokens to generate
                - top_p: Nucleus sampling parameter
                - top_k: Top-k sampling parameter
                - stop_sequences: List of strings to stop generation
                - presence_penalty: Penalty for new tokens based on presence in the text
                - frequency_penalty: Penalty for new tokens based on frequency in the text
                - functions: List of function definitions the model may generate JSON inputs for
                - function_call: Controls how the model responds to function calls
                - tools: List of tools the model may call
                - tool_choice: Controls which tool the model calls
            
        Returns:
            Assistant's response message
        """
        pass
    
    async def stream_chat(
        self,
        messages: List[Message],
        **generation_kwargs
    ) -> AsyncGenerator[Message, None]:
        """
        Stream chat completions from the model.
        
        Args:
            messages: List of messages in the conversation
            **generation_kwargs: Generation parameters (same as chat method)
            
        Yields:
            Chunks of the assistant's response message as they become available
        """
        # Default implementation falls back to non-streaming
        response = await self.chat(messages, **generation_kwargs)
        yield response
    
    async def stream_generate(
        self,
        prompt: Union[str, List[Message]],
        **generation_kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream generated text from the model.
        
        Args:
            prompt: The prompt or list of messages
            **generation_kwargs: Generation parameters (same as generate method)
            
        Yields:
            Chunks of generated text as they become available
        """
        # Default implementation falls back to non-streaming
        response = await self.generate(prompt, **generation_kwargs)
        yield response
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information including:
            - provider: Name of the provider
            - model: Model name/ID
            - capabilities: List of supported features
            - max_tokens: Maximum context length
            - supports_system_messages: Whether system messages are supported
        """
        return {
            "provider": "unknown",
            "model": self.model_name,
            "capabilities": ["completion"],
            "max_tokens": 2048,
            "supports_system_messages": False,
        }
    
    @classmethod
    @abstractmethod
    def get_provider_type(cls) -> LLMType:
        """
        Get the type of this provider.
        
        Returns:
            LLMType enum value
        """
        pass
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if the model supports a specific feature.
        
        Args:
            feature: Feature name (e.g., 'streaming', 'function_calling')
            
        Returns:
            bool: Whether the feature is supported
        """
        return feature in self.get_model_info().get("capabilities", [])
