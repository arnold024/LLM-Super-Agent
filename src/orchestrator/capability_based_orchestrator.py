import logging
from typing import List, Dict, Any, Optional
from src.task_management.task import Task
from src.task_management.task_queue import TaskQueue
from src.agent.agent import Agent

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CapabilityBasedOrchestrator:
    """
    An orchestrator that assigns tasks to agents based on their declared capabilities.
    """

    def __init__(self, agents: List[Agent]):
        """
        Initializes the CapabilityBasedOrchestrator.

        Args:
            agents: A list of Agent instances available to the orchestrator.
        """
        self._task_queue = TaskQueue()
        self._agents: Dict[str, Agent] = {agent.get_name(): agent for agent in agents}
        self._agent_capabilities: Dict[str, List[str]] = {}
        self._initialize_agent_capabilities()
        logging.info(f"CapabilityBasedOrchestrator initialized with agents: {list(self._agents.keys())}")

    def _initialize_agent_capabilities(self):
        """
        Initialize the capabilities for each agent.
        For this example, we assume each agent has a method get_capabilities() returning a list of strings.
        """
        for agent_name, agent in self._agents.items():
            if hasattr(agent, 'get_capabilities'):
                self._agent_capabilities[agent_name] = agent.get_capabilities()
            else:
                self._agent_capabilities[agent_name] = []
            logging.info(f"Agent '{agent_name}' capabilities: {self._agent_capabilities[agent_name]}")

    def add_task(self, task: Task, capability: Optional[str] = None):
        """
        Adds a task to the queue with an optional required capability.

        Args:
            task: The Task object to add.
            capability: The required capability for the task (optional).
        """
        task.input_data['required_capability'] = capability
        self._task_queue.add_task(task)

    def run(self):
        """
        Runs the orchestrator, assigning tasks to agents based on capabilities.
        """
        logging.info("CapabilityBasedOrchestrator started.")
        while not self._task_queue.is_empty():
            task = self._task_queue.get_next_task()
            if task:
                required_capability = task.input_data.get('required_capability')
                # Remove 'required_capability' from kwargs before passing to LLM
                if 'required_capability' in task.input_data:
                    del task.input_data['required_capability']
                assigned_agent = self._select_agent_for_task(required_capability)
                if not assigned_agent:
                    logging.error(f"No agent found with capability '{required_capability}' for task {task.task_id}")
                    task.update_status("failed")
                    task.add_output_data("error", f"No agent with capability '{required_capability}'")
                    continue

                logging.info(f"Assigning task {task.task_id} to agent {assigned_agent.get_name()}")
                processed_task = assigned_agent.process_task(task)
                logging.info(f"Task {processed_task.task_id} processed with status: {processed_task.status}")

                # Process messages for each agent
                for agent in self._agents.values():
                    messages = agent.receive_messages()
                    for message in messages:
                        agent.handle_message(message)

        logging.info("CapabilityBasedOrchestrator finished processing all tasks.")

    def _select_agent_for_task(self, capability: Optional[str]) -> Optional[Agent]:
        """
        Selects an agent that has the required capability.

        Args:
            capability: The required capability for the task.

        Returns:
            An Agent instance or None if no suitable agent is found.
        """
        if capability is None:
            # If no capability specified, assign to any agent (round-robin or first)
            return next(iter(self._agents.values()), None)

        for agent_name, capabilities in self._agent_capabilities.items():
            if capability in capabilities:
                return self._agents[agent_name]

        return None