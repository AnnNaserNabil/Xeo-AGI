"""
Advanced Gemini LLM Features Example

This example demonstrates the advanced features of Google's Gemini LLM with the Xeo framework,
including streaming responses and function calling.
"""
import asyncio
import json
from typing import List, Dict, Any, AsyncGenerator, Optional

from xeo import (
    create_llm,
    LLMType,
    Message,
    MessageRole,
    FunctionCall,
    ToolCall
)

# Example function definitions that the model can call
FUNCTIONS = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email to a recipient",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                }
            },
            "required": ["to", "subject", "body"]
        }
    }
]

# Mock function implementations
def get_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """Mock function to get weather information."""
    print(f"\n[Function called] get_weather(location='{location}', unit='{unit}')")
    return {
        "location": location,
        "temperature": 22 if unit == "celsius" else 72,
        "unit": unit,
        "conditions": "sunny",
        "humidity": 0.6
    }

async def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Mock function to send an email."""
    print(f"\n[Function called] send_email(to='{to}', subject='{subject}')")
    print(f"Email body: {body[:100]}..." if len(body) > 100 else f"Email body: {body}")
    return {
        "success": True,
        "to": to,
        "subject": subject,
        "message": "Email sent successfully"
    }

async def process_function_call(function_call: Dict[str, Any]) -> Dict[str, Any]:
    """Process a function call and return the result."""
    name = function_call.get("name", "")
    args = function_call.get("arguments", {})
    
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}
    
    if name == "get_weather":
        return get_weather(**args)
    elif name == "send_email":
        return await send_email(**args)
    else:
        return {"error": f"Unknown function: {name}"}

async def chat_with_function_calling():
    """Example of chat with function calling."""
    print("\n=== Chat with Function Calling ===")
    
    # Initialize the Gemini LLM
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Start a conversation
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What's the weather like in Tokyo?")
    ]
    
    print(f"\nUser: {messages[-1].content}")
    
    # Get the model's response (which may include function calls)
    response = await gemini.chat(
        messages=messages,
        tools=[{"function": func} for func in FUNCTIONS],
        tool_choice="auto"
    )
    
    # Add the assistant's response to the conversation
    messages.append(response)
    
    # Check if the model wants to call a function
    if response.tool_calls:
        print("\nAssistant is calling functions...")
        
        # Process each function call
        for tool_call in response.tool_calls:
            if tool_call.get("type") == "function":
                function_call = tool_call.get("function", {})
                function_name = function_call.get("name", "")
                function_args = function_call.get("arguments", {})
                
                print(f"\nCalling function: {function_name}")
                print(f"Arguments: {function_args}")
                
                # Call the function
                function_result = await process_function_call({
                    "name": function_name,
                    "arguments": function_args
                })
                
                # Add the function result to the conversation
                messages.append(Message(
                    role=MessageRole.TOOL,
                    name=function_name,
                    content=json.dumps(function_result),
                    tool_call_id=tool_call.get("id", "")
                ))
        
        # Get the final response with the function results
        final_response = await gemini.chat(
            messages=messages,
            tools=[{"function": func} for func in FUNCTIONS]
        )
        
        print(f"\nAssistant: {final_response.content}")
        messages.append(final_response)
    else:
        print(f"\nAssistant: {response.content}")
    
    return messages

async def stream_chat_example():
    """Example of streaming chat completions."""
    print("\n=== Streaming Chat Example ===")
    
    # Initialize the Gemini LLM
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Start a conversation
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Tell me a short story about a robot learning to paint.")
    ]
    
    print(f"\nUser: {messages[-1].content}")
    print("\nAssistant: ", end="", flush=True)
    
    # Stream the response
    full_response = ""
    async for chunk in gemini.stream_chat(messages=messages, temperature=0.7):
        if chunk.content:
            print(chunk.content[len(full_response):], end="", flush=True)
            full_response = chunk.content
    
    # Add the assistant's response to the conversation
    messages.append(Message(role=MessageRole.ASSISTANT, content=full_response))
    
    return messages

async def main():
    """Run all examples."""
    # Run the function calling example
    await chat_with_function_calling()
    
    # Run the streaming chat example
    await stream_chat_example()

if __name__ == "__main__":
    import os
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please set your Google API key and try again.")
    else:
        asyncio.run(main())
