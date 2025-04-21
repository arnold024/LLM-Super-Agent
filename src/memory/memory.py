from typing import Any, Dict, Optional, List
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Memory:
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

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    memory = Memory()

    # Store some information
    memory.store("user_name", "Alice")
    memory.store("task_result_123", {"summary": "Report complete"})

    # Retrieve information
    user = memory.retrieve("user_name")
    task_result = memory.retrieve("task_result_123")
    non_existent = memory.retrieve("project_status")

    print(f"\nRetrieved user_name: {user}")
    print(f"Retrieved task_result_123: {task_result}")
    print(f"Retrieved non_existent: {non_existent}")

    # List keys
    print(f"\nKeys in memory: {memory.list_keys()}")

    # Clear memory
    memory.clear()
    print(f"\nKeys in memory after clearing: {memory.list_keys()}")