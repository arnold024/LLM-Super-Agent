import sys
import os

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from llm_integration.google_gemini_connector import GoogleGeminiConnector # Import GoogleGeminiConnector
from agent.basic_agent import BasicAgent
from agent.communication import AgentCommunicationChannel
from memory.sqlite_memory import SQLiteMemory # Import SQLiteMemory
from plugins.plugin_manager import PluginManager
from task_management.task import Task
from orchestrator.simple_orchestrator import SimpleOrchestrator

def main():
    """
    Main function to set up and run the LLMSuperAgent CLI.
    """
    print("Initializing LLMSuperAgent...")

    # Initialize core components
    communication_channel = AgentCommunicationChannel()
    memory = SQLiteMemory() # Use SQLiteMemory instead of in-memory Memory
    plugin_manager = PluginManager()

    # Create LLM connectors (using GoogleGeminiConnector)
    # Note: Ensure GOOGLE_API_KEY environment variable is set for this to work
    # Using 'models/gemini-2.5-flash-preview-04-17' as it supports generateContent
    gemini_llm_1 = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17")
    gemini_llm_2 = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17") # Can use different models if needed

    # Create basic agents, passing the necessary components and the Gemini connector
    agent_alpha = BasicAgent("AlphaAgent", gemini_llm_1, communication_channel, memory, plugin_manager)
    agent_beta = BasicAgent("BetaAgent", gemini_llm_2, communication_channel, memory, plugin_manager)

    # Create the orchestrator with the agents
    orchestrator = SimpleOrchestrator(agents=[agent_alpha, agent_beta])

    print("LLMSuperAgent initialized. Type 'exit' to quit.")

    # Basic CLI loop
    while True:
        try:
            user_input = input("Enter a task description: ")
            if user_input.lower() == 'exit':
                break

            if not user_input.strip():
                print("Please enter a valid task description.")
                continue

            # Create a task from user input
            new_task = Task(description=user_input.strip(), input_data={"prompt": user_input.strip()})

            # Add the task to the orchestrator and run
            orchestrator.add_task(new_task)
            orchestrator.run() # In a real system, this might run in a separate thread or process

            # Display the result of the task (assuming sequential processing for MVP)
            # In a more complex system, you'd retrieve the task by ID and check its status/output
            print("\nTask Processing Complete.")
            # For this simple example, we'll just show the last processed task's output if available
            # A better approach would be to retrieve the task from a task registry
            # For now, we'll rely on the orchestrator's logging to show processing.

        except Exception as e:
            print(f"An error occurred: {e}")

    print("Exiting LLMSuperAgent CLI.")

if __name__ == "__main__":
    main()