"""
Example script demonstrating the use of Gemini 2.0 Flash model in the Xeo framework.
"""
import asyncio
from dotenv import load_dotenv
from agentic_framework.llm import create_llm, LLMType, Message, MessageRole

async def test_gemini_2_flash():
    # Load environment variables
    load_dotenv()
    
    # Create the Gemini 2.0 Flash LLM instance
    llm = create_llm(
        llm_type=LLMType.GEMINI,
        model_name="gemini-2.0-flash",
    )
    
    # Get model info
    model_info = llm.get_model_info()
    print("\n=== Model Information ===")
    print(f"Model: {model_info['model']}")
    print(f"Provider: {model_info['provider']}")
    print(f"Max tokens: {model_info['max_tokens']}")
    print(f"Capabilities: {', '.join(model_info['capabilities'])}")
    
    # Test chat
    print("\n=== Testing Chat ===")
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="Tell me a short joke about AI")
    ]
    
    response = await llm.chat(messages=messages)
    print(f"\nResponse: {response.content}")
    
    # Test streaming
    print("\n=== Testing Streaming ===")
    print("Response (streaming): ", end="", flush=True)
    
    async for chunk in llm.stream_chat(messages=messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(test_gemini_2_flash())
