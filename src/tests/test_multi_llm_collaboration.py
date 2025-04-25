import sys
import os
import logging

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from src.agent.basic_agent import BasicAgent
from src.agent.communication import AgentCommunicationChannel
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager
from src.task_management.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_multi_llm_collaboration():
    # Setup communication channel, memory, and plugin manager
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    # Create two agents with different LLM connectors
    gemini_connector = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17")
    openai_connector = OpenAIChatGPTConnector("gpt-4") # Use a real OpenAI model name

    agent_gemini = BasicAgent("GeminiAgent", gemini_connector, communication_channel, memory, plugin_manager)
    agent_openai = BasicAgent("OpenAIAgent", openai_connector, communication_channel, memory, plugin_manager)

    # Create tasks for both agents
    task1 = Task("Gemini task", input_data={"prompt": "Explain the theory of relativity."})
    task2 = Task("Generic task", input_data={"prompt": "Write a poem about the sea."})

    # Add tasks to the queue
    agent_gemini.delegate_task(task1, "OpenAIAgent")
    agent_openai.delegate_task(task2, "GeminiAgent")

    # Agents process their own tasks
    result1 = agent_gemini.process_task(task1)
    result2 = agent_openai.process_task(task2)

    logging.info(f"GeminiAgent processed task with status: {result1.status}")
    logging.info(f"OpenAIAgent processed task with status: {result2.status}")

if __name__ == "__main__":
    test_multi_llm_collaboration()