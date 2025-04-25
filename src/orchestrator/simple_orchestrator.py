import sys
import os
import logging
from typing import List, Dict, Any

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..task_management.task import Task
from ..task_management.task_queue import TaskQueue
from ..agent.agent import Agent
from ..llm_integration.llm_interface import LLMInterface
from ..agent.basic_agent import BasicAgent # Assuming BasicAgent for initial implementation
from ..planning.planner import Planner # Import Planner
from ..llm_integration.google_gemini_connector import GoogleGeminiConnector
from ..llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from ..agent.communication import AgentCommunicationChannel # Import AgentCommunicationChannel

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleOrchestrator:
    """
    A simple orchestrator that manages a task queue and a pool of agents
    to execute tasks sequentially.
    """

    def __init__(self, agents: List[Agent], planner: Planner):
        """
        Initializes the SimpleOrchestrator.

        Args:
            agents: A list of Agent instances available to the orchestrator.
        """
        self._task_queue = TaskQueue()
        self._communication_channel = AgentCommunicationChannel() # Instantiate communication channel
        self._planner = planner # Store the planner instance
        # Store agents, ensuring they are initialized with the communication channel
        # The agents list passed to the constructor should ideally already have the channel
        # For this simple orchestrator, we'll just store them.
        self._agents: Dict[str, Agent] = {agent.get_name(): agent for agent in agents}
        self._agent_names = list(self._agents.keys())
        self._next_agent_index = 0
        logging.info(f"Orchestrator initialized with agents: {self._agent_names}")

    def add_task(self, task: Task):
        """
        Adds a task to the orchestrator's task queue.

        Args:
            task: The Task object to add.
        """
        self._task_queue.add_task(task)

    def process_goal(self, goal_description: str, initial_context: Optional[Dict[str, Any]] = None):
        """
        Processes a high-level goal by generating a plan and adding tasks to the queue.

        Args:
            goal_description: The description of the high-level goal.
            initial_context: Optional initial context for planning.
        """
        logging.info(f"Orchestrator received goal: '{goal_description}'. Generating plan...")
        plan_tasks = self._planner.generate_plan(goal_description, initial_context)
        logging.info(f"Planner generated {len(plan_tasks)} tasks.")
        for task in plan_tasks:
            self.add_task(task)
        logging.info("Generated tasks added to the queue.")

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
                agent_name = self._agent_names[self._next_agent_index]
                agent = self._agents[agent_name]

                logging.info(f"Assigning task {task.task_id} to agent {agent.get_name()}")
                processed_task = agent.process_task(task)
                logging.info(f"Task {processed_task.task_id} processed with status: {processed_task.status}")

                # Update the index for round-robin
                self._next_agent_index = (self._next_agent_index + 1) % len(self._agent_names)

                # Process messages for each agent
                for agent in self._agents.values():
                    messages = agent.receive_messages()
                    for message in messages:
                        agent.handle_message(message)

        logging.info("Orchestrator finished processing all tasks.")

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Create dummy LLM connectors
    # Create actual LLM connectors
    llm_connector_1 = GoogleGeminiConnector("gemini-pro") # Use a real Gemini model name
    llm_connector_2 = OpenAIChatGPTConnector("gpt-4") # Use a real OpenAI model name

    # Create a communication channel instance
    communication_channel = AgentCommunicationChannel()

    # Create basic agents, passing the communication channel, memory, and plugin manager
    # Note: Memory and PluginManager are not used by SimpleOrchestrator directly,
    # but are passed to agents during their creation.
    from src.memory.memory import Memory
    from src.plugins.plugin_manager import PluginManager

    memory = Memory() # Instantiate Memory
    plugin_manager = PluginManager() # Instantiate PluginManager

    agent_alpha = BasicAgent("AlphaAgent", llm_connector_1, communication_channel, memory, plugin_manager)
    agent_beta = BasicAgent("BetaAgent", llm_connector_2, communication_channel, memory, plugin_manager)

    # Create the orchestrator with the agents and a basic planner
    from src.planning.planner import BasicPlanner # Import BasicPlanner
    basic_planner = BasicPlanner()
    orchestrator = SimpleOrchestrator(agents=[agent_alpha, agent_beta], planner=basic_planner)

    # Instead of creating individual tasks, process a high-level goal
    high_level_goal = "Develop a simple task management system."
    orchestrator.process_goal(high_level_goal)

    # The tasks generated by process_goal are already added to the queue

    # Demonstrate task delegation (optional, can be removed or adapted)
    # delegation_task = Task("Delegated task example", input_data={"prompt": "This task was delegated."})
    # agent_alpha.delegate_task(delegation_task, "BetaAgent")

    # If using delegation, add the delegated task to the queue
    # orchestrator.add_task(delegation_task)

    # Run the orchestrator
    orchestrator.run()