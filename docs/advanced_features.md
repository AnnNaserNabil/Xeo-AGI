# Advanced Features

This document covers the advanced features available in the Xeo framework's LLM integration.

## Table of Contents

- [Streaming Responses](#streaming-responses)
- [Function Calling](#function-calling)
- [Tool Use](#tool-use)
- [System Messages](#system-messages)
- [Advanced Configuration](#advanced-configuration)
- [Error Handling](#error-handling)

## Streaming Responses

Streaming allows you to process the model's response as it's being generated, which is useful for creating responsive UIs or processing long-running generations.

### Basic Streaming

```python
from xeo import create_llm, LLMType, Message, MessageRole

async def stream_response():
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro"
    )
    
    messages = [
        Message(role=MessageRole.USER, content="Tell me a story about a robot.")
    ]
    
    print("Assistant: ", end="", flush=True)
    async for chunk in gemini.stream_chat(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")
```

### Streaming with Function Calling

```python
async def stream_with_functions():
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro"
    )
    
    functions = [
        {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    ]
    
    messages = [
        Message(role=MessageRole.USER, content="What's the weather in Tokyo?")
    ]
    
    print("Assistant: ", end="", flush=True)
    full_response = ""
    
    async for chunk in gemini.stream_chat(
        messages=messages,
        tools=[{"function": f} for f in functions]
    ):
        if chunk.content:
            print(chunk.content[len(full_response):], end="", flush=True)
            full_response = chunk.content
            
        if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
            print("\n\nFunction calls detected!")
            for tool_call in chunk.tool_calls:
                print(f"- {tool_call['function']['name']}: {tool_call['function']['arguments']}")
    print("\n")
```

## Function Calling

Function calling allows the model to request that certain functions be called with specific parameters.

### Basic Function Calling

```python
async def function_calling_example():
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro"
    )
    
    functions = [
        {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    ]
    
    messages = [
        Message(role=MessageRole.USER, content="What's the weather in Paris?")
    ]
    
    # Get the model's response (may include function calls)
    response = await gemini.chat(
        messages=messages,
        tools=[{"function": f} for f in functions],
        tool_choice="auto"
    )
    
    # Check if the model wants to call a function
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.get("type") == "function":
                function_name = tool_call["function"]["name"]
                function_args = tool_call["function"]["arguments"]
                
                print(f"Function call: {function_name}({function_args})")
                
                # Call the function and get the result
                result = {"temperature": 22, "conditions": "sunny"}  # Example result
                
                # Add the function result to the conversation
                messages.append(Message(
                    role=MessageRole.TOOL,
                    name=function_name,
                    content=json.dumps(result),
                    tool_call_id=tool_call.get("id", "")
                ))
        
        # Get the final response with the function results
        final_response = await gemini.chat(
            messages=messages,
            tools=[{"function": f} for f in functions]
        )
        
        print(f"Assistant: {final_response.content}")
    else:
        print(f"Assistant: {response.content}")
```

## Tool Use

Tools extend the model's capabilities by allowing it to interact with external systems.

### Defining Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                },
                "required": ["symbol"]
            }
        }
    }
]
```

## System Messages

System messages help set the behavior of the assistant.

```python
system_message = Message(
    role=MessageRole.SYSTEM,
    content="""You are a helpful assistant that provides concise answers. 
    If you don't know something, say so rather than making things up."""
)

user_message = Message(
    role=MessageRole.USER,
    content="What's the capital of France?"
)

response = await gemini.chat(messages=[system_message, user_message])
```

## Advanced Configuration

### Generation Parameters

```python
response = await gemini.chat(
    messages=messages,
    temperature=0.7,  # Controls randomness (0.0 to 1.0)
    max_tokens=1000,  # Maximum number of tokens to generate
    top_p=0.9,       # Nucleus sampling parameter
    top_k=40,        # Top-k sampling parameter
    stop_sequences=["\n"],  # Stop generation at these sequences
    presence_penalty=0.0,  # Penalize new tokens based on presence in the text
    frequency_penalty=0.0  # Penalize new tokens based on frequency in the text
)
```

## Error Handling

Handle errors that may occur during API calls:

```python
from xeo.llm import LLMError

try:
    response = await gemini.chat(messages=messages)
except LLMError as e:
    print(f"Error calling the LLM: {e}")
    # Handle the error appropriately
```

For more examples, see the [advanced_gemini_features.py](../examples/advanced_gemini_features.py) example.
