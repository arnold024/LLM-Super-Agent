import os
from typing import Any, Dict
import openai

from src.llm_integration.llm_interface import LLMInterface
from src.llm_integration.api_key_manager import APIKeyManager

class OpenAIChatGPTConnector(LLMInterface):
    """
    Connector for the OpenAI ChatGPT API.
    Requires the OPENAI_API_KEY environment variable to be set.
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initializes the OpenAIChatGPTConnector.

        Args:
            model_name: The name of the ChatGPT model to use (e.g., "gpt-4").
        """
        self._model_name = model_name
        self._api_key = APIKeyManager.get_api_key("OPENAI")
        openai.api_key = self._api_key

    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generates a response using the OpenAI ChatGPT model.

        Args:
            prompt: The input prompt for the LLM.
            **kwargs: Additional parameters for the OpenAI API call.

        Returns:
            The generated response string.

        Raises:
            Exception: If the API call fails.
        """
        print(f"Using OpenAI ChatGPT model '{self._model_name}' for prompt: {prompt}")

        try:
            response = openai.chat.completions.create(
                model=self._model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error during OpenAI ChatGPT API call: {e}")
            raise Exception(f"OpenAI ChatGPT API error: {e}")

    def get_model_name(self) -> str:
        """
        Returns the name of the OpenAI ChatGPT model being used.
        """
        return self._model_name

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    try:
        connector = OpenAIChatGPTConnector("gpt-4")
        response = connector.generate_response("Hello, how are you?")
        print(f"Response: {response}")
        print(f"Model Used: {connector.get_model_name()}")
    except Exception as e:
        print(f"Error: {e}")