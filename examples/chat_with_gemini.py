#!/usr/bin/env python3
"""
Continuous chat interface with Google's Gemini model using the Xeo framework.

This script provides an interactive chat interface that allows you to have
conversations with the Gemini model. It maintains conversation history and
provides a user-friendly interface.

Usage:
    python examples/chat_with_gemini.py
"""
import asyncio
import os
import sys
import readline  # For better input handling
from typing import List, Optional
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from xeo import (
    init, cleanup,
    get_llm_factory,
    Message, MessageRole,
    get_plugin_manager
)
from xeo.llm.providers.gemini import GeminiLLM
from xeo.llm.llm_factory import llm_factory

class ChatSession:
    """Manages a chat session with the Gemini model."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialize the chat session.
        
        Args:
            model_name: Name of the Gemini model to use.
        """
        self.model_name = model_name
        self.messages: List[Message] = []
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM with the Gemini provider."""
        try:
            llm_factory = get_llm_factory()
            self.llm = llm_factory.create_llm(
                provider_name="gemini",
                model_name=self.model_name,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                top_k=40
            )
        except Exception as e:
            print(f"Error initializing LLM: {e}")
            raise
    
    async def chat(self, user_input: str) -> str:
        """Send a message to the model and get a response.
        
        Args:
            user_input: The user's message.
            
        Returns:
            The model's response.
        """
        if not user_input.strip():
            return "Please provide a non-empty message."
        
        # Add user message to history
        self.messages.append(Message(role=MessageRole.USER, content=user_input))
        
        try:
            # Get response from the model
            response = await self.llm.chat(self.messages)
            
            # Add assistant's response to history
            self.messages.append(response)
            
            return response.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def clear_history(self):
        """Clear the conversation history."""
        self.messages = []
        return "Conversation history cleared."
    
    def show_help(self):
        """Show help message with available commands."""
        return """\nAvailable commands:
    /help - Show this help message
    /clear - Clear conversation history
    /exit or /quit - Exit the chat
    /model [name] - Switch to a different model (if available)
    /history - Show conversation history
"""
    
    def show_history(self):
        """Show the conversation history."""
        if not self.messages:
            return "No conversation history."
        
        history = []
        for i, msg in enumerate(self.messages, 1):
            role = "You" if msg.role == MessageRole.USER else "Assistant"
            history.append(f"{i}. {role}: {msg.content}")
        
        return "\n".join(history)
    
    def change_model(self, model_name: str) -> str:
        """Change the model being used.
        
        Args:
            model_name: Name of the model to switch to.
            
        Returns:
            Status message.
        """
        try:
            self.model_name = model_name
            self._initialize_llm()
            return f"Switched to model: {model_name}"
        except Exception as e:
            return f"Error switching model: {str(e)}"

async def main():
    """Run the interactive chat session."""
    # Initialize the Xeo framework
    print("Initializing Xeo framework...")
    
    # Register the Gemini provider
    print("Registering Gemini provider...")
    llm_factory.register_provider('gemini', GeminiLLM)
    
    # Initialize the framework
    init()
    
    try:
        # Create a chat session
        print("Initializing Gemini model...")
        session = ChatSession()
        
        print("\n" + "=" * 50)
        print("Gemini Chat".center(50))
        print("Type '/help' for available commands".center(50))
        print("=" * 50 + "\n")
        
        # Main chat loop
        while True:
            try:
                # Get user input
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break
                
                # Handle commands
                if user_input.lower() in ('/exit', '/quit'):
                    print("Goodbye!")
                    break
                    
                elif user_input.lower() == '/help':
                    print(session.show_help())
                    continue
                    
                elif user_input.lower() == '/clear':
                    session.clear_history()
                    print("Conversation history cleared.")
                    continue
                    
                elif user_input.lower() == '/history':
                    print("\n" + session.show_history() + "\n")
                    continue
                    
                elif user_input.lower().startswith('/model '):
                    model_name = user_input[7:].strip()
                    print(session.change_model(model_name))
                    continue
                
                # Get response from the model
                print("\nAssistant: ", end="", flush=True)
                
                # Stream the response
                response = ""
                async for chunk in session.llm.stream_chat(session.messages + [Message(role=MessageRole.USER, content=user_input)]):
                    print(chunk.content, end="", flush=True)
                    response += chunk.content
                
                # Add the response to history
                if response:
                    session.messages.append(Message(role=MessageRole.ASSISTANT, content=response))
                
                print("\n")
                
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    finally:
        # Clean up resources
        print("Cleaning up...")
        cleanup()

if __name__ == "__main__":
    asyncio.run(main())
