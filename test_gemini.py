"""
Test script for the Gemini agent using google-generativeai 0.8.5.
"""
import asyncio
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def test_gemini():
    """Test the Gemini LLM integration."""
    # Get the API key from environment variables
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set the GOOGLE_API_KEY environment variable in your .env file.")
        return

    try:
        # Configure the API
        print(f"Using API key: {api_key[:10]}...{api_key[-4:]}" if api_key else "No API key found")
        genai.configure(api_key=api_key)
        
        # List available models
        print("\nAvailable models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} (supports: {', '.join(m.supported_generation_methods)})")
        
        # Use the gemini-2.0-flash model
        model_name = "models/gemini-2.0-flash"
        
        # Verify the model exists and is accessible
        available_models = [m.name for m in genai.list_models()]
        if model_name not in available_models:
            print(f"\nError: Model {model_name} not found in available models.")
            print("Available models:")
            for m in available_models:
                if 'gemini' in m.lower():
                    print(f"- {m}")
            return
            
        print(f"\nUsing model: {model_name}")
        
        # Test text generation
        print("\nTesting text generation...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Write a haiku about artificial intelligence")
        print(f"Response: {response.text}")
        
        # Test chat
        print("\nTesting chat...")
        chat = model.start_chat(history=[])
        response = chat.send_message("Hello, who are you?")
        print(f"Assistant: {response.text}")
        
    except Exception as e:
        print(f"\nError: {e}")
        if hasattr(e, 'status_code') and e.status_code == 403:
            print("\nThis might be due to:"
                  "\n1. The API key doesn't have the required permissions"
                  "\n2. The API is not enabled for your project"
                  "\n3. The API key is invalid or has been revoked"
                  "\nPlease check your Google Cloud Console settings.")
        elif hasattr(e, 'status_code') and e.status_code == 429:
            print("\nYou've exceeded your quota. Please check your Google Cloud Console for more details.")
        else:
            print("\nAn unexpected error occurred. Please check your setup and try again.")

if __name__ == "__main__":
    asyncio.run(test_gemini())
