from typing import Any, Dict, Optional, List
import logging
from .memory_interface import MemoryInterface # Import the interface

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Memory(MemoryInterface): # Inherit from MemoryInterface
    """
    A basic in-memory placeholder for the agent's memory.
    In a real system, this would be a more sophisticated memory system
    (e.g., database, vector store, knowledge graph).
    """

    def __init__(self):
        """
        Initializes an empty in-memory memory store.
        """
        self._memory: Dict[str, Any] = {}
        logging.info("Memory component initialized.")

    def store(self, key: str, value: Any):
        """
        Stores a piece of information in memory.

        Args:
            key: A unique key to identify the information.
            value: The information to store.
        """
        self._memory[key] = value
        logging.info(f"Stored item in memory with key: {key}")

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieves a piece of information from memory by its key.

        Args:
            key: The key of the information to retrieve.

        Returns:
            The stored information, or None if the key is not found.
        """
        value = self._memory.get(key)
        if value is not None:
            logging.info(f"Retrieved item from memory with key: {key}")
        else:
            logging.warning(f"Attempted to retrieve non-existent key from memory: {key}")
        return value

    def list_keys(self) -> List[str]:
        """
        Lists all keys currently stored in memory.

        Returns:
            A list of keys.
        """
        return list(self._memory.keys())

    def clear(self):
        """
        Clears all information from memory.
        """
        self._memory = {}
        logging.info("Memory cleared.")

    def consolidate(self, max_size: int = 100, **kwargs):
        """
        Consolidates the memory by removing the oldest entries if the memory exceeds max_size.
        This is a very basic implementation.

        Args:
            max_size: The maximum number of entries to keep in memory.
            **kwargs: Additional parameters (not used in this basic implementation).
        """
        logging.info(f"Performing basic memory consolidation (max_size={max_size})")
        if len(self._memory) > max_size:
            # Sort keys by insertion order (older keys come first) - Python dicts maintain insertion order
            keys_to_remove = list(self._memory.keys())[:len(self._memory) - max_size] # Get the oldest keys
            for key in keys_to_remove:
                del self._memory[key]
                logging.info(f"Removed key '{key}' during memory consolidation.")
            logging.info(f"Memory consolidated.  New size: {len(self._memory)}")
        else:
            logging.info("Memory consolidation not needed (memory within limits).")

    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Performs a basic keyword search within the stored memory values.
        This is a simple placeholder implementation.

        Args:
            query: The search query string.
            **kwargs: Additional parameters (not used in this basic implementation).

        Returns:
            A list of dictionaries for matching items, containing 'key' and 'value'.
        """
        logging.info(f"Performing basic memory search for query: '{query}'")
        results = []
        query_lower = query.lower()
        for key, value in self._memory.items():
            # Convert value to string for simple keyword search
            if query_lower in str(value).lower():
                results.append({"key": key, "value": value})
        logging.info(f"Basic memory search found {len(results)} results.")
        return results

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    memory = Memory()

    # Store some information
    memory.store("user_name", "Alice")
    memory.store("task_result_123", {"summary": "Report complete", "status": "completed"})
    memory.store("project_status", "Project is currently in progress.")

    # Retrieve information
    user = memory.retrieve("user_name")
    task_result = memory.retrieve("task_result_123")
    non_existent = memory.retrieve("project_config")

    print(f"\nRetrieved user_name: {user}")
    print(f"Retrieved task_result_123: {task_result}")
    print(f"Retrieved non_existent: {non_existent}")

    # List keys
    print(f"\nKeys in memory: {memory.list_keys()}")

    print("-" * 20)

    # Perform searches
    search_results_report = memory.search("report")
    print(f"\nSearch results for 'report': {search_results_report}")

    search_results_alice = memory.search("Alice")
    print(f"\nSearch results for 'Alice': {search_results_alice}")

    search_results_progress = memory.search("progress")
    print(f"\nSearch results for 'progress': {search_results_progress}")

    search_results_missing = memory.search("nonexistent")
    print(f"\nSearch results for 'nonexistent': {search_results_missing}")

    print("-" * 20)

    # Demonstrate consolidation
    print("\nDemonstrating memory consolidation:")
    for i in range(150):
        memory.store(f"item_{i}", f"Value {i}") # Add more items to exceed max_size

    print(f"Memory size before consolidation: {len(memory.list_keys())}")
    memory.consolidate(max_size=100)
    print(f"Memory size after consolidation: {len(memory.list_keys())}")

    # Clear memory
    memory.clear()
    print(f"\nKeys in memory after clearing: {memory.list_keys()}")