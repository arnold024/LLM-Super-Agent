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
    # Choose one of the connectors created earlier
    primary_llm = gemini_llm
    orchestrator = SimpleOrchestrator(plugin_manager=plugin_manager, llm_connector=primary_llm)

    print("LLMSuperAgent initialized.")
    print("Available commands: goal <description>, list tasks, search memory <query>, exit")

    # Basic CLI loop
    # --- Temporary hardcoded goal for testing ---
    test_goal = "visit https://www.dentalpatientforum.com, pick a random forum topic and generate a summary about it for a facebook post"
    print(f"Automatically processing test goal: {test_goal}")
    try:
        # Assuming 'orchestrator' is already initialized
        generated_plan = orchestrator.process_goal(test_goal) # Pass the goal string directly

        if generated_plan and generated_plan.metadata.get('status') != "failed":
            print(f"\nPlan generated successfully (ID: {generated_plan.metadata.get('plan_id', 'N/A')}). Executing plan...")
            orchestrator.run(plan=generated_plan)
            print(f"\nPlan execution finished. Final plan status: {generated_plan.status}")
        else:
            print("\nPlanning failed or no plan generated, cannot execute.")
            if generated_plan:
                 print(f"Plan Status: {generated_plan.metadata.get('status')}")
                 print(f"Plan Failure Reason: {generated_plan.metadata.get('reason', 'N/A')}")

    except Exception as e:
        print(f"An error occurred during automatic goal processing: {e}")
        import traceback
        traceback.print_exc()
    # --- End temporary testing block ---

    print("Exiting LLMSuperAgent CLI.")

if __name__ == "__main__":
    main()