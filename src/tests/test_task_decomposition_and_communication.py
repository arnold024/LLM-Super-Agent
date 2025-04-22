import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.task_management.task import Task
from src.task_management.task_decomposition import TaskDecomposer
from src.agent.basic_agent import BasicAgent
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from src.agent.communication import AgentCommunicationChannel
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_task_decomposition_and_communication():
    # Setup communication channel, memory, and plugin manager
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    # Create two agents with real LLM connectors
    gemini_connector = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17")
    chatgpt_connector = OpenAIChatGPTConnector("gpt-4")

    agent_gemini = BasicAgent("GeminiAgent", gemini_connector, communication_channel, memory, plugin_manager)
    agent_chatgpt = BasicAgent("ChatGPTAgent", chatgpt_connector, communication_channel, memory, plugin_manager)

    # Create a main task
    main_task = Task("Main task: Write a report and create a summary", input_data={"prompt": "Write a report and create a summary."})

    # Decompose the main task into subtasks
    decomposer = TaskDecomposer()
    subtasks = decomposer.decompose(main_task)

    # Assign subtasks to different agents
    for i, subtask in enumerate(subtasks):
        if i % 2 == 0:
            agent_gemini.delegate_task(subtask, "ChatGPTAgent")
        else:
            agent_chatgpt.delegate_task(subtask, "GeminiAgent")

    # Agents process their own tasks and handle messages
    for agent in [agent_gemini, agent_chatgpt]:
        messages = agent.receive_messages()
        for message in messages:
            agent.handle_message(message)
            if message.message_type == "task_delegation":
                delegated_task = Task(
                    description=message.payload["description"],
                    task_id=message.payload["task_id"],
                    input_data=message.payload["input_data"]
                )
                result_task = agent.process_task(delegated_task)
                logging.info(f"{agent.name} processed delegated task with status: {result_task.status}")

if __name__ == "__main__":
    test_task_decomposition_and_communication()