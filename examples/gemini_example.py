"""
Example of using Google's Gemini LLM with the Xeo framework.
"""
import asyncio
import os
from typing import List

from xeo.llm import (
    create_llm,
    LLMType,
    Message,
    MessageRole
)

async def main():
    # Initialize the Gemini LLM
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro",  # or "gemini-1.5-pro-latest" for the latest model
        api_key=os.getenv("GOOGLE_API_KEY")  # Set your API key here or in environment
    )
    
    print(f"Using model: {gemini.model_name}")
    print(f"Model info: {gemini.get_model_info()}")
    
    # Example 1: Simple text generation
    print("\n--- Example 1: Simple Text Generation ---")
    prompt = "Write a short poem about artificial intelligence."
    response = await gemini.generate(prompt)
    print(f"Prompt: {prompt}")
    print(f"Response: {response}")
    
    # Example 2: Chat conversation
    print("\n--- Example 2: Chat Conversation ---")
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What's the weather like today?")
    ]
    
    # Get the assistant's response
    assistant_message = await gemini.chat(messages)
    messages.append(assistant_message)
    print(f"Assistant: {assistant_message.content}")
    
    # Continue the conversation
    messages.append(Message(
        role=MessageRole.USER,
        content="Tell me more about how weather affects daily life."
    ))
    
    assistant_message = await gemini.chat(messages)
    print(f"\nFollow-up response: {assistant_message.content[:200]}...")  # Print first 200 chars
    
    # Example 3: Advanced generation with parameters
    print("\n--- Example 3: Advanced Generation ---")
    advanced_prompt = """
    Write a creative short story (2-3 paragraphs) about a robot 
    that discovers human emotions. The story should be:
    - Set in a futuristic city
    - Include a plot twist
    - Have a philosophical tone
    """
    
    story = await gemini.generate(
        advanced_prompt,
        temperature=0.9,  # More creative/random
        max_tokens=500,  # Limit response length
        top_p=0.9,
    )
    
    print(f"Generated story:\n{story}")

if __name__ == "__main__":
    asyncio.run(main())
