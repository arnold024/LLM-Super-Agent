import os
import sys

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import google.generativeai as genai
from src.llm_integration.api_key_manager import APIKeyManager

def list_models():
    """Lists available Gemini models and their supported methods."""
    try:
        api_key = APIKeyManager.get_api_key("GOOGLE")
        genai.configure(api_key=api_key)

        print("Available Gemini Models:")
        for model in genai.list_models():
            print(f"Name: {model.name}")
            print(f"  Supported methods: {model.supported_generation_methods}")
            print("-" * 20)

    except ValueError as e:
        print(f"Error: {e}")
        print("Please ensure the GOOGLE_API_KEY environment variable is set or in your .env file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    list_models()