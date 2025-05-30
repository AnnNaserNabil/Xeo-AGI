# LLM Integration Guide

This guide explains how to integrate and use Large Language Models (LLMs) with the Xeo framework, with a focus on Google's Gemini model.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Available Models](#available-models)
- [Usage](#usage)
  - [Basic Text Generation](#basic-text-generation)
  - [Chat Conversations](#chat-conversations)
  - [Advanced Generation Parameters](#advanced-generation-parameters)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements-llm.txt
```

2. Set up your Google API key:

```bash
export GOOGLE_API_KEY='your-api-key-here'
# Or add it to a .env file:
# GOOGLE_API_KEY=your-api-key-here
```

## Quick Start

Here's a simple example of using the Gemini LLM:

```python
import asyncio
import os
from xeo.llm import create_llm, LLMType

async def main():
    # Initialize the Gemini LLM
    gemini = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-pro",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Generate text
    response = await gemini.generate("Tell me a joke about programming.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Models

The following Gemini models are supported:

- `gemini-pro`: Best for text generation
- `gemini-1.5-pro-latest`: Latest version with enhanced capabilities

## Usage

### Basic Text Generation

```python
response = await gemini.generate("Explain quantum computing in simple terms.")
print(response)
```

### Chat Conversations

```python
from xeo.llm import Message, MessageRole

messages = [
    Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
    Message(role=MessageRole.USER, content="What's the weather like today?")
]

# Get the assistant's response
assistant_message = await gemini.chat(messages)
print(assistant_message.content)
```

### Advanced Generation Parameters

```python
response = await gemini.generate(
    "Write a creative story",
    temperature=0.8,  # Controls randomness (0.0 to 1.0)
    max_tokens=500,   # Maximum length of the response
    top_p=0.9,        # Nucleus sampling parameter
    top_k=40          # Top-k sampling parameter
)
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Cloud API key
- `HTTP_PROXY` / `HTTPS_PROXY`: Proxy configuration if needed

### Generation Parameters

- `temperature` (float, 0.0-1.0): Controls randomness (higher = more creative)
- `max_tokens` (int): Maximum number of tokens to generate
- `top_p` (float): Nucleus sampling parameter (0.0-1.0)
- `top_k` (int): Top-k sampling parameter

## Error Handling

Handle LLM errors using the `LLMError` exception:

```python
from xeo.llm import LLMError

try:
    response = await gemini.generate(prompt)
except LLMError as e:
    print(f"Error generating response: {e}")
```

## Best Practices

1. **API Key Security**: Never hardcode API keys in your source code. Use environment variables or a secure secret management system.

2. **Rate Limiting**: Implement rate limiting to avoid hitting API rate limits.

3. **Error Handling**: Always implement proper error handling for API calls.

4. **Prompt Engineering**: Craft clear and specific prompts for better results.

5. **Testing**: Test different temperature and top-p values to find the best balance between creativity and coherence.

6. **Cost Management**: Monitor your API usage to manage costs, especially for production applications.

For more examples, see the [examples/gemini_example.py](../examples/gemini_example.py) file.
