import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestrator.capability_based_orchestrator import CapabilityBasedOrchestrator
from src.agent.basic_agent import BasicAgent
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from src.agent.communication import AgentCommunicationChannel
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager
from src.task_management.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_capability_based_orchestrator():
    # Setup communication channel, memory, and plugin manager
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    # Create agents with capabilities
    gemini_connector = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17")
    chatgpt_connector = OpenAIChatGPTConnector("gpt-4")

    agent_gemini = BasicAgent("GeminiAgent", gemini_connector, communication_channel, memory, plugin_manager, capabilities=["science", "math"])
    agent_chatgpt = BasicAgent("ChatGPTAgent", chatgpt_connector, communication_channel, memory, plugin_manager, capabilities=["poetry", "creative writing"])

    # Create the orchestrator with the agents
    orchestrator = CapabilityBasedOrchestrator(agents=[agent_gemini, agent_chatgpt])

    # Create tasks with required capabilities
    task1 = Task("Explain the theory of relativity", input_data={"prompt": "Explain the theory of relativity."})
    task2 = Task("Write a poem about the sea", input_data={"prompt": "Write a poem about the sea."})

    # Add tasks to the orchestrator with required capabilities
    orchestrator.add_task(task1, capability="science")
    orchestrator.add_task(task2, capability="poetry")

    # Run the orchestrator
    orchestrator.run()

    # For demonstration, print the output data stored in memory for each task
    for task in [task1, task2]:
        memory_key = f"task_output_{task.task_id}"
        output_data = memory.retrieve(memory_key)
        print(f"\nOutput for task '{task.description}':")
        print(output_data)

if __name__ == "__main__":
    demo_capability_based_orchestrator()