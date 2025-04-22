import sqlite3
import json
import logging
from typing import Any, Dict, Optional, List
from .memory_interface import MemoryInterface # Import the interface

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SQLiteMemory(MemoryInterface):
    """
    A basic SQLite database-backed memory implementation.
    Stores key-value pairs in a SQLite database file.
    """

    def __init__(self, db_path: str = "memory.db"):
        """
        Initializes the SQLiteMemory.

        Args:
            db_path: The path to the SQLite database file.
        """
        self._db_path = db_path
        self._conn = None
        self._connect()
        self._create_table()
        logging.info(f"SQLiteMemory component initialized using database: {db_path}")

    def _connect(self):
        """Establishes a connection to the SQLite database."""
        try:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row # Access columns by name
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            # In a real application, handle this error more gracefully

    def _close(self):
        """Closes the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logging.info("Database connection closed.")

    def _create_table(self):
        """Creates the memory table if it doesn't exist."""
        if self._conn:
            try:
                cursor = self._conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                self._conn.commit()
                logging.info("Memory table checked/created.")
            except sqlite3.Error as e:
                logging.error(f"Error creating table: {e}")
                # Handle error

    def store(self, key: str, value: Any):
        """
        Stores a piece of information in memory.
        Value is stored as a JSON string.

        Args:
            key: A unique key to identify the information.
            value: The information to store.
        """
        if self._conn:
            try:
                value_json = json.dumps(value)
                cursor = self._conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)", (key, value_json))
                self._conn.commit()
                logging.info(f"Stored item in SQLite memory with key: {key}")
            except sqlite3.Error as e:
                logging.error(f"Error storing data: {e}")
                # Handle error

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieves a piece of information from memory by its key.
        Value is loaded from a JSON string.

        Args:
            key: The key of the information to retrieve.

        Returns:
            The stored information, or None if the key is not found.
        """
        if self._conn:
            try:
                cursor = self._conn.cursor()
                cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    value_json = row['value']
                    value = json.loads(value_json)
                    logging.info(f"Retrieved item from SQLite memory with key: {key}")
                    return value
                else:
                    logging.warning(f"Attempted to retrieve non-existent key from SQLite memory: {key}")
                    return None
            except sqlite3.Error as e:
                logging.error(f"Error retrieving data: {e}")
                return None
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from memory for key {key}: {e}")
                return None
        return None

    def list_keys(self) -> List[str]:
        """
        Lists all keys currently stored in memory.

        Returns:
            A list of keys.
        """
        if self._conn:
            try:
                cursor = self._conn.cursor()
                cursor.execute("SELECT key FROM memory")
                keys = [row['key'] for row in cursor.fetchall()]
                return keys
            except sqlite3.Error as e:
                logging.error(f"Error listing keys: {e}")
                return []
        return []

    def clear(self):
        """
        Clears all information from memory.
        """
        if self._conn:
            try:
                cursor = self._conn.cursor()
                cursor.execute("DELETE FROM memory")
                self._conn.commit()
                logging.info("SQLite memory cleared.")
            except sqlite3.Error as e:
                logging.error(f"Error clearing memory: {e}")
                # Handle error

    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Performs a basic keyword search within the stored memory values in the SQLite database.

        Args:
            query: The search query string.
            **kwargs: Additional parameters (not used in this basic implementation).

        Returns:
            A list of dictionaries for matching items, containing 'key' and 'value'.
        """
        logging.info(f"Performing SQLite memory search for query: '{query}'")
        results = []
        if self._conn:
            try:
                cursor = self._conn.cursor()
                # Use LIKE for basic substring matching in the JSON string value
                cursor.execute("SELECT key, value FROM memory WHERE value LIKE ?", (f"%{query}%",))
                rows = cursor.fetchall()
                for row in rows:
                    try:
                        value = json.loads(row['value'])
                        results.append({"key": row['key'], "value": value})
                    except json.JSONDecodeError as e:
                        logging.error(f"Error decoding JSON from memory for key {row['key']} during search: {e}")
                logging.info(f"SQLite memory search found {len(results)} results.")
                return results
            except sqlite3.Error as e:
                logging.error(f"Error searching data: {e}")
                return []
        return []

    def __del__(self):
        """Ensures the database connection is closed when the object is garbage collected."""
        self._close()

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Create a temporary database file for testing
    test_db_path = "test_memory.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    sqlite_memory = SQLiteMemory(test_db_path)

    # Store some information
    sqlite_memory.store("user_settings", {"theme": "dark", "language": "en"})
    sqlite_memory.store("task_result_456", {"status": "processed", "output": "Summary generated."})
    sqlite_memory.store("project_status", "Project is currently in progress.")

    # Retrieve information
    settings = sqlite_memory.retrieve("user_settings")
    task_result = sqlite_memory.retrieve("task_result_456")
    non_existent = sqlite_memory.retrieve("project_config")

    print(f"\nRetrieved user_settings: {settings}")
    print(f"Retrieved task_result_456: {task_result}")
    print(f"Retrieved non_existent: {non_existent}")

    # List keys
    print(f"\nKeys in memory: {sqlite_memory.list_keys()}")

    print("-" * 20)

    # Perform searches
    search_results_report = sqlite_memory.search("Summary")
    print(f"\nSearch results for 'Summary': {search_results_report}")

    search_results_dark = sqlite_memory.search("dark")
    print(f"\nSearch results for 'dark': {search_results_dark}")

    search_results_progress = sqlite_memory.search("progress")
    print(f"\nSearch results for 'progress': {search_results_progress}")

    search_results_missing = sqlite_memory.search("nonexistent")
    print(f"\nSearch results for 'nonexistent': {search_results_missing}")


    # Clear memory
    sqlite_memory.clear()
    print(f"\nKeys in memory after clearing: {sqlite_memory.list_keys()}")

    # Clean up the test database file
    if os.path.exists(test_db_path):
        os.remove(test_db_path)