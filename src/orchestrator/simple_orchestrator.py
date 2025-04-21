import logging
from typing import List, Dict, Any
from src.task_management.task import Task
from src.task_management.task_queue import TaskQueue
from src.agent.agent import Agent
from src.llm_integration.llm_interface import LLMInterface
from src.agent.basic_agent import BasicAgent # Assuming BasicAgent for initial implementation
from src.llm_integration.generic_llm_connector import GenericLLMConnector # Assuming GenericLLMConnector for initial implementation
from src.agent.communication import AgentCommunicationChannel # Import AgentCommunicationChannel

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleOrchestrator:
    """
    A simple orchestrator that manages a task queue and a pool of agents
    to execute tasks sequentially.
    """

    def __init__(self, agents: List[Agent]):
        """
        Initializes the SimpleOrchestrator.

        Args:
            agents: A list of Agent instances available to the orchestrator.
        """
        self._task_queue = TaskQueue()
        self._communication_channel = AgentCommunicationChannel() # Instantiate communication channel
        # Store agents, ensuring they are initialized with the communication channel
        # The agents list passed to the constructor should ideally already have the channel
        # For this simple orchestrator, we'll just store them.
        self._agents: Dict[str, Agent] = {agent.get_name(): agent for agent in agents}
        logging.info(f"Orchestrator initialized with agents: {list(self._agents.keys())}")

    def add_task(self, task: Task):
        """
        Adds a task to the orchestrator's task queue.

        Args:
            task: The Task object to add.
        """
        self._task_queue.add_task(task)

    def run(self):
        """
        Runs the orchestrator, processing tasks from the queue sequentially.
        A rudimentary routing mechanism is implemented: tasks are assigned
        to the first available agent in the provided list.
        """
        logging.info("Orchestrator started.")
        while not self._task_queue.is_empty():
            task = self._task_queue.get_next_task()
            if task:
                # Rudimentary routing: Assign to the first agent for now
                # In the future, this will involve more complex logic
                if not self._agents:
                    logging.error("No agents available to process tasks.")
                    task.update_status("failed")
                    task.add_output_data("error", "No agents available")
                    continue

                # Get the first agent (rudimentary routing)
                agent_name = list(self._agents.keys())[0]
                agent = self._agents[agent_name]

                logging.info(f"Assigning task {task.task_id} to agent {agent.get_name()}")
                processed_task = agent.process_task(task)
                logging.info(f"Task {processed_task.task_id} processed with status: {processed_task.status}")

        logging.info("Orchestrator finished processing all tasks.")

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Create dummy LLM connectors
    dummy_llm_1 = GenericLLMConnector("dummy-model-A")
    dummy_llm_2 = GenericLLMConnector("dummy-model-B")

    # Create a communication channel instance
    communication_channel = AgentCommunicationChannel()

    # Create basic agents, passing the communication channel, memory, and plugin manager
    # Note: Memory and PluginManager are not used by SimpleOrchestrator directly,
    # but are passed to agents during their creation.
    memory = Memory() # Instantiate Memory
    plugin_manager = PluginManager() # Instantiate PluginManager

    agent_alpha = BasicAgent("AlphaAgent", dummy_llm_1, communication_channel, memory, plugin_manager)
    agent_beta = BasicAgent("BetaAgent", dummy_llm_2, communication_channel, memory, plugin_manager)

    # Create the orchestrator with the agents
    orchestrator = SimpleOrchestrator(agents=[agent_alpha, agent_beta])

    # Create some tasks
    task1 = Task("Process document X", input_data={"prompt": "Summarize the following text: ..."})
    task2 = Task("Analyze sentiment", input_data={"prompt": "What is the sentiment of this review: ..."})
    task3 = Task("Generate code snippet", input_data={"prompt": "Write a Python function for ..."})

    # Add tasks to the orchestrator
    orchestrator.add_task(task1)
    orchestrator.add_task(task2)
    orchestrator.add_task(task3)

    # Run the orchestrator
    orchestrator.run()