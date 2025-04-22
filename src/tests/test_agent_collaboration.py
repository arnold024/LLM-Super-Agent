import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..llm_integration.generic_llm_connector import GenericLLMConnector
from ..agent.basic_agent import BasicAgent
from ..agent.communication import AgentCommunicationChannel, AgentMessage
from ..memory.memory import Memory
from ..plugins.plugin_manager import PluginManager
from ..task_management.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_agent_collaboration():
    # Setup communication channel, memory, and plugin manager
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    # Create two agents with dummy LLM connectors
    llm_connector_1 = GenericLLMConnector("dummy-llm-1")
    llm_connector_2 = GenericLLMConnector("dummy-llm-2")

    agent1 = BasicAgent("Agent1", llm_connector_1, communication_channel, memory, plugin_manager)
    agent2 = BasicAgent("Agent2", llm_connector_2, communication_channel, memory, plugin_manager)

    # Agent1 creates a task and delegates it to Agent2
    task = Task("Collaborative task", input_data={"prompt": "Process this collaboratively."})
    agent1.delegate_task(task, "Agent2")

    # Agent2 checks messages and handles the delegated task
    messages = agent2.receive_messages()
    for message in messages:
        agent2.handle_message(message)
        if message.message_type == "task_delegation":
            # Agent2 processes the delegated task
            delegated_task = Task(
                description=message.payload["description"],
                task_id=message.payload["task_id"],
                input_data=message.payload["input_data"]
            )
            result_task = agent2.process_task(delegated_task)
            logging.info(f"Agent2 processed delegated task with status: {result_task.status}")

if __name__ == "__main__":
    test_agent_collaboration()