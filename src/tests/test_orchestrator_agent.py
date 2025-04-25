import logging
import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agent.orchestrator_agent import OrchestratorAgent
from src.agent.basic_agent import BasicAgent
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.agent.communication import AgentCommunicationChannel
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager
from src.task_management.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_orchestrator_agent():
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    orchestrator = OrchestratorAgent("Orchestrator", communication_channel, memory, plugin_manager)

    # Create a user request task
    user_task = Task("User request", input_data={"prompt": "Write a few sentences about the weather and base64 decode it."})

    # Process the user request with the orchestrator
    result_task = orchestrator.process_task(user_task)

    logging.info(f"Orchestration plan output:\n{result_task.output_data.get('orchestration_plan')}")

if __name__ == "__main__":
    test_orchestrator_agent()