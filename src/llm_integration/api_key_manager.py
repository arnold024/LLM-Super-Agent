import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class APIKeyManager:
    """
    Manages secure access to API keys for different LLM providers.
    Loads keys from environment variables.
    """

    @staticmethod
    def get_api_key(provider_name: str) -> str:
        """
        Retrieves the API key for a given LLM provider from environment variables.

        Args:
            provider_name: The name of the LLM provider (e.g., "OPENAI", "ANTHROPIC", "GOOGLE").
                           The environment variable should be named in the format
                           [PROVIDER_NAME]_API_KEY (e.g., OPENAI_API_KEY).

        Returns:
            The API key string.

        Raises:
            ValueError: If the API key environment variable is not set.
        """
        env_var_name = f"{provider_name.upper()}_API_KEY"
        api_key = os.getenv(env_var_name)

        if not api_key:
            raise ValueError(f"API key for {provider_name} not found in environment variable {env_var_name}")

        return api_key

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # To test, set an environment variable like:
    # export OPENAI_API_KEY="your_openai_key_here"
    # or create a .env file with OPENAI_API_KEY="your_openai_key_here"

    try:
        openai_key = APIKeyManager.get_api_key("openai")
        print(f"Successfully retrieved OpenAI API key (first 5 chars): {openai_key[:5]}...")
    except ValueError as e:
        print(f"Error retrieving API key: {e}")

    try:
        google_key = APIKeyManager.get_api_key("google")
        print(f"Successfully retrieved Google API key (first 5 chars): {google_key[:5]}...")
    except ValueError as e:
        print(f"Error retrieving API key: {e}")