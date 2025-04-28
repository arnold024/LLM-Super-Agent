import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_openai_chatgpt_connector():
    try:
        connector = OpenAIChatGPTConnector("gpt-4")
        prompt = "Write a short poem about the sea."
        response = connector.generate_response(prompt)
        logging.info(f"Prompt: {prompt}")
        logging.info(f"Response: {response}")
    except Exception as e:
        logging.error(f"Error during OpenAI ChatGPT connector test: {e}")

if __name__ == "__main__":
    test_openai_chatgpt_connector()
