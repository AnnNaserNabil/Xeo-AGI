"""
Example of using Google's Gemini LLM with an Agent in the Xeo framework.
"""
import asyncio
import os
from typing import List, Dict, Any

from xeo import Agent, AgentConfig, AgentType
from xeo.llm import create_llm, LLMType, Message, MessageRole

class GeminiAgent(Agent):
    """An agent that uses Google's Gemini for text generation."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Gemini agent.
        
        Args:
            api_key: Google API key (optional, can be set via GOOGLE_API_KEY env var)
        """
        config = AgentConfig(
            name="GeminiAgent",
            agent_type=AgentType.AUTONOMOUS,
            description="An agent that uses Google's Gemini for text generation"
        )
        super().__init__(config)
        
        # Initialize the Gemini LLM
        self.llm = create_llm(
            llm_type=LLMType.GEMINI,
            model_name="gemini-pro",
            api_key=api_key or os.getenv("GOOGLE_API_KEY")
        )
        
        # Add some default capabilities
        self.capabilities = ["text_generation", "chat"]
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Gemini model.
        
        Args:
            prompt: The prompt to generate text from
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        return await self.llm.generate(prompt, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generate a chat response using the Gemini model.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        # Convert messages to the expected format
        formatted_messages = [
            Message(
                role=MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT,
                content=msg["content"]
            )
            for msg in messages
        ]
        
        response = await self.llm.chat(formatted_messages, **kwargs)
        return response.content
    
    async def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process input data using the agent's capabilities.
        
        Args:
            input_data: Input data to process
            **kwargs: Additional parameters
            
        Returns:
            Processed output
        """
        if isinstance(input_data, str):
            return await self.generate_text(input_data, **kwargs)
        elif isinstance(input_data, list):
            return await self.chat(input_data, **kwargs)
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}")

async def main():
    """Example usage of the GeminiAgent."""
    # Create an instance of the agent
    agent = GeminiAgent()
    
    # Example 1: Simple text generation
    print("=== Example 1: Text Generation ===")
    response = await agent.generate_text(
        "Write a haiku about artificial intelligence"
    )
    print(f"Response: {response}")
    
    # Example 2: Chat conversation
    print("\n=== Example 2: Chat Conversation ===")
    messages = [
        {"role": "user", "content": "Hello, who are you?"},
    ]
    
    # First response
    response = await agent.chat(messages)
    print(f"Assistant: {response}")
    
    # Add assistant's response to the conversation
    messages.append({"role": "assistant", "content": response})
    
    # User follow-up
    messages.append({"role": "user", "content": "Tell me more about yourself."})
    
    # Get another response
    response = await agent.chat(messages)
    print(f"\nAssistant: {response}")
    
    # Example 3: Using the process method
    print("\n=== Example 3: Using process method ===")
    response = await agent.process("What is the capital of France?")
    print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
