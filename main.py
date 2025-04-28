import sys
import os
import logging # Import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from llm_integration.google_gemini_connector import GoogleGeminiConnector
from llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector # Import OpenAIChatGPTConnector
from agent.basic_agent import BasicAgent
from agent.communication import AgentCommunicationChannel
from memory.memory import Memory # Import in-memory Memory
from plugins.plugin_manager import PluginManager
from task_management.task import Task
from orchestrator.simple_orchestrator import SimpleOrchestrator
from planning.planner import BasicPlanner # Import BasicPlanner

def main():
    """
    Main function to set up and run the LLMSuperAgent CLI.
    """
    print("Initializing LLMSuperAgent...")

    # Initialize core components
    communication_channel = AgentCommunicationChannel()
    memory = Memory() # Use in-memory Memory temporarily
    plugin_manager = PluginManager()

    # Create LLM connectors (using GoogleGeminiConnector)
    # Note: Ensure GOOGLE_API_KEY environment variable is set for this to work
    # Using 'models/gemini-2.5-flash-preview-04-17' as it supports generateContent
    # Create LLM connectors
    # Note: Ensure GOOGLE_API_KEY and OPENAI_API_KEY environment variables are set
    gemini_llm = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17") # Use a real Gemini model name
    openai_llm = OpenAIChatGPTConnector("gpt-4") # Use a real OpenAI model name

    # Create basic agents, passing the necessary components and the Gemini connector
    # Create basic agents, passing the necessary components and the LLM connectors
    agent_gemini = BasicAgent("GeminiAgent", gemini_llm, communication_channel, memory, plugin_manager)
    agent_openai = BasicAgent("OpenAIAgent", openai_llm, communication_channel, memory, plugin_manager)

    # Create a planner instance
    # Create a planner instance
    planner = BasicPlanner(llm_connector=gemini_llm) # Use the BasicPlanner with a Gemini connector

    # Create the orchestrator with the agents and the planner
    orchestrator = SimpleOrchestrator(agents=[agent_gemini, agent_openai], planner=planner)

    print("LLMSuperAgent initialized.")
    print("Available commands: goal <description>, list tasks, search memory <query>, exit")

    # Basic CLI loop
    while True:
        try:
            user_input = input("Enter command: ")
            if user_input.lower() == 'exit':
                break

            # Simple command parsing
            parts = user_input.strip().split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == 'goal' and args:
                print(f"Received goal: {args}")
                orchestrator.process_goal(args)
                print("\nRunning orchestrator...")
                orchestrator.run()
                print("\nTask Processing Complete.")

            elif command == 'list' and args == 'tasks':
                print("\nCurrent Tasks in Queue:")
                tasks = orchestrator.get_tasks()
                if tasks:
                    for i, task in enumerate(tasks):
                        print(f"{i+1}. {task.description} (Status: {task.status})")
                else:
                    print("No tasks in the queue.")

            elif command == 'search' and args.startswith('memory '):
                query = args[len('memory '):].strip()
                if query:
                    print(f"\nSearching memory for: '{query}'")
                    results = orchestrator.search_memory(query)
                    if results:
                        print("Search Results:")
                        for result in results:
                            print(f"- Key: {result.get('key', 'N/A')}, Value: {result.get('value', 'N/A')}")
                    else:
                        print("No results found in memory.")
                else:
                    print("Please provide a search query for memory.")

            elif command == 'exit':
                break

            elif not user_input.strip():
                print("Please enter a command.")
                continue

            else:
                print(f"Unknown command: {command}. Type 'exit' to quit.")
                continue

        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"An error occurred: {e}", exc_info=True) # Log the full traceback

    print("Exiting LLMSuperAgent CLI.")

if __name__ == "__main__":
    main()