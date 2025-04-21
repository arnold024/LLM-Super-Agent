from typing import Any, Dict, Optional, List
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeBase:
    """
    A basic in-memory placeholder for an external knowledge base.
    In a real system, this would connect to external APIs, databases,
    or other knowledge sources.
    """

    def __init__(self):
        """
        Initializes a basic in-memory knowledge base with some dummy data.
        """
        self._knowledge: Dict[str, Any] = {
            "capital_of_france": "Paris",
            "pi_value": 3.14159,
            "greeting_message": "Hello! How can I help you today?"
        }
        logging.info("KnowledgeBase component initialized with dummy data.")

    def query(self, query_key: str) -> Optional[Any]:
        """
        Queries the knowledge base for information based on a key.

        Args:
            query_key: The key to query the knowledge base with.

        Returns:
            The retrieved information, or None if the key is not found.
        """
        info = self._knowledge.get(query_key.lower()) # Case-insensitive query for simplicity
        if info is not None:
            logging.info(f"KnowledgeBase retrieved information for query: {query_key}")
        else:
            logging.warning(f"KnowledgeBase could not find information for query: {query_key}")
        return info

    def add_knowledge(self, key: str, value: Any):
        """
        Adds a piece of knowledge to the knowledge base.
        In a real system, this might involve more complex ingestion.

        Args:
            key: The key for the knowledge.
            value: The knowledge to add.
        """
        self._knowledge[key.lower()] = value # Store keys in lowercase
        logging.info(f"Added knowledge to KnowledgeBase with key: {key}")

    def list_keys(self) -> List[str]:
        """
        Lists all keys currently stored in the knowledge base.

        Returns:
            A list of keys.
        """
        return list(self._knowledge.keys())

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    kb = KnowledgeBase()

    # Query existing knowledge
    capital = kb.query("Capital_of_France")
    pi = kb.query("pi_value")
    greeting = kb.query("greeting_message")
    non_existent = kb.query("population_of_tokyo")

    print(f"\nQuery 'Capital_of_France': {capital}")
    print(f"Query 'pi_value': {pi}")
    print(f"Query 'greeting_message': {greeting}")
    print(f"Query 'population_of_tokyo': {non_existent}")

    # Add new knowledge
    kb.add_knowledge("favorite_color", "blue")
    print(f"\nKeys in KnowledgeBase after adding: {kb.list_keys()}")

    # Query new knowledge
    fav_color = kb.query("favorite_color")
    print(f"Query 'favorite_color': {fav_color}")