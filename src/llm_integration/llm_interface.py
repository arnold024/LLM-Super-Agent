import abc

class LLMInterface(abc.ABC):
    """
    Abstract base class for integrating various LLM APIs.
    """

    @abc.abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generates a response from the LLM based on the given prompt.

        Args:
            prompt: The input prompt for the LLM.
            **kwargs: Additional parameters for the LLM API call.

        Returns:
            The generated response string.
        """
        pass

    @abc.abstractmethod
    def get_model_name(self) -> str:
        """
        Returns the name of the LLM model being used.
        """
        pass

# Future methods for more advanced interactions could be added here,
# e.g., chat history, function calling, etc.