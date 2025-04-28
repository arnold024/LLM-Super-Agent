import sqlite3
import json
import logging
from typing import Any, Dict, Optional, List
from .memory_interface import MemoryInterface # Import the interface
from src.llm_integration.llm_interface import LLMInterface # Import LLMInterface
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector # Import for example usage
import json # Ensure json is imported

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SQLiteMemory(MemoryInterface):
    """
    A basic SQLite database-backed memory implementation.
    Stores key-value pairs in a SQLite database file.
    """

    def __init__(self, db_path: str = "memory.db", llm_connector: Optional[LLMInterface] = None):
        """
        Initializes the SQLiteMemory.

        Args:
            db_path: The path to the SQLite database file.
            llm_connector: An optional LLM connector for enhanced search/consolidation.
        """
        self._db_path = db_path
        self._llm = llm_connector
        self._conn = None
        self._connect()
        self._create_table()
        logging.info(f"SQLiteMemory component initialized using database: {db_path}")
        if self._llm:
            logging.info(f"SQLiteMemory using LLM for enhanced features: {self._llm.get_model_name()}")

        def __init__(self, db_path: str = "memory.db", llm_connector: Optional[LLMInterface] = None):
            """
            Initializes the SQLiteMemory.
    
            Args:
                db_path: The path to the SQLite database file.
                llm_connector: An optional LLM connector for enhanced search/consolidation.
            """
            self._db_path = db_path
            self._llm = llm_connector
            self._conn = None
            self._connect()
            self._create_table()
            logging.info(f"SQLiteMemory component initialized using database: {db_path}")
            if self._llm:
                logging.info(f"SQLiteMemory using LLM for enhanced features: {self._llm.get_model_name()}")
    
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
                except Exception as e:
                    logging.error(f"An unexpected error occurred while listing keys: {e}")
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
            Performs a search within the stored memory values.
            If an LLM connector is available, it uses the LLM to generate search terms.
            Otherwise, it performs a basic keyword search.
    
            Args:
                query: The search query string.
                **kwargs: Additional parameters (e.g., number of results).
    
            Returns:
                A list of dictionaries for matching items, containing 'key' and 'value'.
            """
            logging.info(f"Performing SQLite memory search for query: '{query}'")
            search_terms = [query] # Start with the original query
    
            if self._llm:
                try:
                    # Use LLM to generate additional search terms or a refined query
                    llm_prompt = f"Given the search query '{query}', generate a few related keywords or phrases that could be used to find relevant information in a database. Provide them as a comma-separated list."
                    llm_response = self._llm.generate_response(llm_prompt)
                    generated_terms = [term.strip() for term in llm_response.split(',') if term.strip()]
                    search_terms.extend(generated_terms)
                    logging.info(f"LLM generated search terms: {generated_terms}")
                except Exception as e:
                    logging.error(f"Error using LLM for search term generation: {e}")
                    # Continue with just the original query if LLM call fails
    
            results = []
            if self._conn:
                try:
                    cursor = self._conn.cursor()
                    # Construct a WHERE clause using LIKE for each search term
                    where_clauses = [f"value LIKE ?" for _ in search_terms]
                    where_sql = " OR ".join(where_clauses)
                    query_params = [f"%{term}%" for term in search_terms]
    
                    sql_query = f"SELECT key, value FROM memory WHERE {where_sql}"
                    cursor.execute(sql_query, query_params)
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
    
        def consolidate(self, **kwargs):
            """
            Performs memory consolidation.
            If an LLM connector is available, it can be used to guide consolidation.
            (Basic implementation: currently just logs a message)
    
            Args:
                **kwargs: Additional parameters for consolidation (e.g., strategy, criteria).
            """
            logging.info("Performing SQLite memory consolidation...")
    
            if self._llm:
                try:
                    # Example LLM call for consolidation strategy (this is a placeholder)
                    llm_prompt = "Given the current memory contents (list keys or summaries), suggest a consolidation strategy (e.g., summarize old entries, remove irrelevant ones)."
                    # In a real implementation, you would pass actual memory content or summaries to the LLM
                    llm_response = self._llm.generate_response(llm_prompt)
                    logging.info(f"LLM suggested consolidation strategy: {llm_response}")
                    # TODO: Implement logic to act on the LLM's suggestion
                except Exception as e:
                    logging.error(f"Error using LLM for memory consolidation suggestion: {e}")
    
            # TODO: Implement actual consolidation logic (e.g., based on age, relevance, size)
            logging.info("SQLite memory consolidation process finished (basic implementation).")
    
    
        def __del__(self):
            """Ensures the database connection is closed when the object is garbage collected."""
            self._close()
    
    # Example usage (for testing purposes, can be removed later)
    if __name__ == "__main__":
        # To run this example with LLM features, you need to have GOOGLE_API_KEY environment variable set
        # and the google-generativeai library installed (pip install google-generativeai)
    
        test_db_path = "test_memory.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
        # Instantiate a Google Gemini connector for the memory
        gemini_connector = None
        try:
            gemini_connector = GoogleGeminiConnector("gemini-pro") # Use a real Gemini model name
            sqlite_memory = SQLiteMemory(test_db_path, llm_connector=gemini_connector)
        except ValueError as e:
            print(f"Could not initialize LLM connector for memory: {e}")
            print("Proceeding with basic SQLite memory without LLM enhancement.")
            sqlite_memory = SQLiteMemory(test_db_path) # Initialize without LLM if API key is missing
        except Exception as e:
            print(f"An unexpected error occurred during LLM connector initialization: {e}")
            print("Proceeding with basic SQLite memory without LLM enhancement.")
            sqlite_memory = SQLiteMemory(test_db_path)
    
    
        # Store some information
        sqlite_memory.store("user_settings", {"theme": "dark", "language": "en"})
        sqlite_memory.store("task_result_456", {"status": "processed", "output": "Summary generated for document X."})
        sqlite_memory.store("project_status", "Project is currently in progress with phase 2.")
        sqlite_memory.store("meeting_notes_20250425", "Discussed enhancing memory search with LLMs.")
    
    
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
    
        # Perform searches (will use LLM if available)
        search_queries = [
            "summarize document",
            "dark theme setting",
            "project status update",
            "notes about memory enhancement",
            "nonexistent topic"
        ]
    
        for query in search_queries:
            search_results = sqlite_memory.search(query)
            print(f"\nSearch results for '{query}': {search_results}")
    
        print("-" * 20)
    
        # Perform consolidation (basic implementation)
        sqlite_memory.consolidate()
        print("\nConsolidation attempted.")
        print("-" * 20)
    
    
        # Clear memory
        sqlite_memory.clear()
        print(f"\nKeys in memory after clearing: {sqlite_memory.list_keys()}")
    
        # Clean up the test database file
        if os.path.exists(test_db_path):
            os.remove(test_db_path)