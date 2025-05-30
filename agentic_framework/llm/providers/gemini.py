"""
Google Gemini LLM integration.
"""
import json
import os
from typing import List, Dict, Any, Optional, Union, cast, AsyncGenerator, AsyncIterator

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, GenerateContentResponse

from ..base import (
    BaseLLM, 
    LLMType, 
    Message, 
    MessageRole,
    FunctionCall,
    ToolCall,
    StreamProtocol
)

# Map our message roles to Gemini's expected roles
ROLE_MAPPING = {
    MessageRole.USER: "user",
    MessageRole.ASSISTANT: "model",
    MessageRole.SYSTEM: "user",  # System messages are typically prepended to user messages
    MessageRole.FUNCTION: "function",
    MessageRole.TOOL: "function",
}

def _convert_to_gemini_messages(messages: List[Message]) -> List[Dict[str, Any]]:
    """Convert internal message format to Gemini's format."""
    gemini_messages = []
    
    for msg in messages:
        role = ROLE_MAPPING.get(msg.role, "user")
        
        # Handle system messages by prefixing to user messages
        if msg.role == MessageRole.SYSTEM:
            if not gemini_messages or gemini_messages[-1]["role"] != "user":
                gemini_messages.append({"role": "user", "parts": [msg.content or ""]})
            gemini_messages.append({"role": "model", "parts": ["Understood."]})
            continue
            
        # Handle function/tool calls
        parts = []
        if msg.content:
            parts.append({"text": msg.content})
            
        # Handle function calls in the assistant's message
        if msg.role == MessageRole.ASSISTANT and msg.function_call:
            function_call = msg.function_call
            parts.append({
                "function_call": {
                    "name": function_call["name"],
                    "args": function_call["arguments"]
                }
            })
        
        # Handle tool calls
        if msg.role == MessageRole.ASSISTANT and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if "function" in tool_call:
                    function_call = tool_call["function"]
                    parts.append({
                        "function_call": {
                            "name": function_call.get("name", ""),
                            "args": function_call.get("arguments", {})
                        }
                    })
        
        # Handle function/tool responses
        if msg.role in (MessageRole.FUNCTION, MessageRole.TOOL) and msg.name:
            parts.append({
                "function_response": {
                    "name": msg.name,
                    "response": {"content": msg.content or ""}
                }
            })
        
        # If no parts were added, add an empty text part
        if not parts:
            parts.append({"text": ""})
            
        gemini_messages.append({
            "role": role,
            "parts": parts
        })
    
    return gemini_messages

def _parse_gemini_response(response: GenerateContentResponse) -> Message:
    """Parse Gemini's response into our Message format."""
    content_parts = []
    function_calls = []
    tool_calls = []
    
    for part in response.parts:
        if hasattr(part, 'text'):
            content_parts.append(part.text)
        elif hasattr(part, 'function_call'):
            function_call = part.function_call
            call_id = f"call_{len(tool_calls)}"
            
            # Handle tool calls
            tool_calls.append({
                "id": call_id,
                "type": "function",
                "function": {
                    "name": function_call.name,
                    "arguments": json.dumps(function_call.args) 
                    if isinstance(function_call.args, dict) 
                    else str(function_call.args)
                }
            })
            
            # For backward compatibility
            if not function_calls:  # Only add to function_calls for backward compatibility
                function_calls.append({
                    "name": function_call.name,
                    "arguments": json.dumps(function_call.args) 
                    if isinstance(function_call.args, dict) 
                    else str(function_call.args)
                })
    
    content = "".join(content_parts).strip()
    
    message = Message(
        role=MessageRole.ASSISTANT,
        content=content if content else None
    )
    
    if function_calls:
        message.function_call = function_calls[0]  # For backward compatibility
    
    if tool_calls:
        message.tool_calls = tool_calls
    
    return message

class GeminiLLM(BaseLLM):
    """Google Gemini LLM provider with support for streaming and function calling."""
    
    def __init__(self, model_name: str, **kwargs):
        """
        Initialize the Gemini LLM.
        
        Args:
            model_name: Name of the Gemini model to use (e.g., 'gemini-1.5-pro', 'gemini-2.0-flash')
            **kwargs: Additional arguments:
                - api_key: Google AI API key (can also be set via GOOGLE_API_KEY env var)
                - generation_config: Optional GenerationConfig for the model
                - safety_settings: Optional safety settings for content generation
        """
        super().__init__(model_name, **kwargs)
        
        # Initialize the Gemini client
        api_key = kwargs.get('api_key') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "Google API key is required. "
                "Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )
            
        genai.configure(api_key=api_key)
        self.generation_config = kwargs.get('generation_config')
        self.safety_settings = kwargs.get('safety_settings')
        
        # Initialize the model with appropriate settings
        self._model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=self.generation_config or self._get_default_generation_config(),
            safety_settings=self.safety_settings or self._get_default_safety_settings()
        )
        
    def _get_default_generation_config(self) -> dict:
        """Get default generation config for the model."""
        return {
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
        
    def _get_default_safety_settings(self) -> list:
        """Get default safety settings for the model."""
        return [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
    
    @classmethod
    def get_provider_type(cls) -> LLMType:
        return LLMType.GEMINI
    
    def _get_generation_config(self, **kwargs) -> GenerationConfig:
        """Create a GenerationConfig from kwargs."""
        return GenerationConfig(
            temperature=kwargs.get('temperature', 0.7),
            max_output_tokens=kwargs.get('max_tokens', kwargs.get('max_output_tokens', 2048)),
            top_p=kwargs.get('top_p', 0.95),
            top_k=kwargs.get('top_k', 40),
            stop_sequences=kwargs.get('stop_sequences', None),
            candidate_count=kwargs.get('n', 1),
            presence_penalty=kwargs.get('presence_penalty', 0.0),
            frequency_penalty=kwargs.get('frequency_penalty', 0.0),
        )
    
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
        config = self._get_generation_config(**generation_kwargs)
        
        if isinstance(prompt, str):
            response = await self._model.generate_content_async(
                prompt,
                generation_config=config,
                safety_settings=self.safety_settings,
                **{k: v for k, v in generation_kwargs.items() 
                   if k not in ['temperature', 'max_tokens', 'max_output_tokens', 
                              'top_p', 'top_k', 'stop_sequences', 'n',
                              'presence_penalty', 'frequency_penalty']}
            )
            return response.text
        else:
            # For message lists, use chat completion
            return (await self.chat(prompt, **generation_kwargs)).content or ""
    
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
                - functions: List of function definitions the model may call
                - function_call: Controls how the model responds to function calls
                - tools: List of tools the model may call
                - tool_choice: Controls which tool the model calls
                
        Returns:
            Assistant's response message
        """
        # Convert messages to Gemini format
        gemini_messages = _convert_to_gemini_messages(messages)
        
        # Get generation config
        config = self._get_generation_config(**generation_kwargs)
        
        # Handle function/tool definitions
        tools = generation_kwargs.get('tools')
        if tools:
            # Convert tools to Gemini format
            gemini_tools = []
            for tool in tools:
                if 'function' in tool:
                    gemini_tools.append({
                        'function_declarations': [{
                            'name': tool['function']['name'],
                            'description': tool['function'].get('description', ''),
                            'parameters': tool['function'].get('parameters', {})
                        }]
                    })
        else:
            gemini_tools = None
        
        # Start a chat session
        chat = self._model.start_chat(history=gemini_messages[:-1])
        
        # Get the latest message parts
        latest_message = gemini_messages[-1]
        
        # Send the message and get response
        response = await chat.send_message_async(
            latest_message['parts'],
            generation_config=config,
            safety_settings=self.safety_settings,
            tools=gemini_tools,
            **{k: v for k, v in generation_kwargs.items() 
               if k not in ['temperature', 'max_tokens', 'max_output_tokens', 
                          'top_p', 'top_k', 'stop_sequences', 'n',
                          'presence_penalty', 'frequency_penalty',
                          'functions', 'function_call', 'tools', 'tool_choice']}
        )
        
        return _parse_gemini_response(response)
    
    async def stream_chat(
        self,
        messages: List[Message],
        **generation_kwargs
    ) -> AsyncGenerator[Message, None]:
        """
        Stream chat completions from the model.
        
        Args:
            messages: List of messages in the conversation
            **generation_kwargs: Same as chat() method
            
        Yields:
            Message chunks as they become available
        """
        # Convert messages to Gemini format
        gemini_messages = _convert_to_gemini_messages(messages)
        
        # Get generation config
        gen_config = self._get_generation_config(**generation_kwargs)
        
        # Start chat session
        chat = self._model.start_chat(history=gemini_messages[:-1])
        
        # Collect all chunks
        response_parts = []
        
        # Get the async iterator for the response
        response = await chat.send_message_async(
            gemini_messages[-1],
            stream=True,
            generation_config=gen_config,
            safety_settings=self.safety_settings
        )
        
        # Process the streaming response
        async for chunk in response:
            if hasattr(chunk, 'text'):
                response_parts.append(chunk.text)
                
                # Create a message with the current response
                response_text = ''.join(response_parts)
                yield Message(
                    role=MessageRole.ASSISTANT,
                    content=response_text
                )
                
            # If this is the final chunk, we're done
            if hasattr(chunk, 'candidates') and chunk.candidates and chunk.candidates[0].finish_reason:
                break
    
    async def stream_generate(
        self,
        prompt: Union[str, List[Message]],
        **generation_kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream generated text from the model.
        
        Args:
            prompt: The prompt or list of messages
            **generation_kwargs: Same as generate() method
            
        Yields:
            Text chunks as they become available
        """
        if isinstance(prompt, str):
            # For simple prompts, use the completion API
            config = self._get_generation_config(**generation_kwargs)
            
            response = await self._model.generate_content_async(
                prompt,
                generation_config=config,
                safety_settings=self.safety_settings,
                stream=True,
                **{k: v for k, v in generation_kwargs.items() 
                   if k not in ['temperature', 'max_tokens', 'max_output_tokens', 
                              'top_p', 'top_k', 'stop_sequences', 'n',
                              'presence_penalty', 'frequency_penalty']}
            )
            
            async for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text
        else:
            # For message lists, use chat streaming
            async for message in self.stream_chat(prompt, **generation_kwargs):
                if message.content:
                    yield message.content
    
    def get_model_info(self) -> dict:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information including capabilities
        """
        model_info = {
            "provider": "google",
            "model": self.model_name,
            "capabilities": ["chat", "function_calling", "streaming"],
            "max_tokens": 1048576,  # Default for Gemini 1.5 models
            "supports_system_messages": True,
        }
        
        # Update based on model version
        if '1.5' in self.model_name:
            model_info.update({
                "max_tokens": 1048576,
                "capabilities": ["chat", "function_calling", "streaming", "long_context"]
            })
        elif '2.0' in self.model_name:
            model_info.update({
                "max_tokens": 1048576 if 'flash' not in self.model_name else 128000,
                "capabilities": ["chat", "function_calling", "streaming", "long_context"]
            })
            
        return model_info
