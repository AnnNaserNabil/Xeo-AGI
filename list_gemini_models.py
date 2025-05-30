"""
List available Gemini models using the API key.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set the GOOGLE_API_KEY environment variable in your .env file.")
    exit(1)

# Configure the API
print(f"Using API key: {api_key[:10]}...{api_key[-4:]}" if api_key else "No API key found")

try:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (supports: {', '.join(m.supported_generation_methods)})")
    
    # Test a simple generation with the first available model
    print("\nTesting generation with the first available model:")
    model = next((m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods), None)
    if model:
        print(f"Using model: {model.name}")
        response = genai.generate_content("Say hello!")
        print(f"Response: {response.text}")
    else:
        print("No suitable model found for content generation.")
        
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
