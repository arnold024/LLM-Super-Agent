import abc
from typing import Any, Dict, Optional, List

class MemoryInterface(abc.ABC):
    """
    Abstract base class for the agent's memory component.
    Defines the interface for storing, retrieving, and managing information.
    """

    @abc.abstractmethod
    def store(self, key: str, value: Any):
        """
        Stores a piece of information in memory.

        Args:
            key: A unique key to identify the information.
            value: The information to store.
        """
        pass

    @abc.abstractmethod
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieves a piece of information from memory by its key.

        Args:
            key: The key of the information to retrieve.

        Returns:
            The stored information, or None if the key is not found.
        """
        pass

    @abc.abstractmethod
    def list_keys(self) -> List[str]:
        """
        Lists all keys currently stored in memory.

        Returns:
            A list of keys.
        """
        pass

    @abc.abstractmethod
    def clear(self):
        """
        Clears all information from memory.
        """
        pass

    @abc.abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Searches the memory for information relevant to the query.

        Args:
            query: The search query string.
            **kwargs: Additional parameters for the search operation (e.g., similarity threshold, number of results).

        Returns:
            A list of dictionaries, where each dictionary represents a search result
            and contains at least 'key' and 'value'. Additional fields like 'score'
            can be included depending on the implementation.
        """
        pass

    @abc.abstractmethod
    def consolidate(self, **kwargs):
        """
        Performs memory consolidation to manage memory size and relevance.
        The specific strategy depends on the implementation.

        Args:
            **kwargs: Additional parameters for the consolidation operation.
        """
        pass

    # Future methods for more advanced memory operations could be added here,
    # e.g., summarize, handle different memory types (short-term, long-term)
    # e.g., summarize, consolidate, handle different memory types (short-term, long-term)