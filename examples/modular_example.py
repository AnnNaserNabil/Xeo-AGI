#!/usr/bin/env python3
"""
Example demonstrating the modular architecture of the Xeo framework.

This example shows how to:
1. Initialize the Xeo framework
2. Use the plugin system to load LLM providers
3. Create and use an LLM instance
4. Clean up resources
"""
import asyncio
import os
from pathlib import Path

from xeo import (
    init, cleanup,
    get_llm_factory, LLMType,
    Message, MessageRole
)

# Set your API key in the environment or in a .env file
# os.environ["GOOGLE_API_KEY"] = "your-api-key-here"

async def main():
    # Initialize the framework
    # This will load plugins and configuration
    init()
    
    try:
        # Get the LLM factory
        llm_factory = get_llm_factory()
        
        # Create a Gemini LLM instance
        gemini_llm = llm_factory.create_llm(
            provider_name="gemini",
            model_name="gemini-2.0-flash"
        )
        
        # Test the LLM
        messages = [
            Message(role=MessageRole.USER, content="Hello, how are you?")
        ]
        
        print("Sending request to Gemini...")
        response = await gemini_llm.chat(messages)
        print(f"Response: {response.content}")
        
        # Test streaming
        print("\nTesting streaming...")
        print("Assistant: ", end="", flush=True)
        
        async for chunk in gemini_llm.stream_chat(messages):
            print(chunk.content, end="", flush=True)
            
        print("\n")
        
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    asyncio.run(main())
