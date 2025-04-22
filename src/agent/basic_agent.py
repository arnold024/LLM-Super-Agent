from src.agent.agent import Agent
from src.llm_integration.llm_interface import LLMInterface
from src.task_management.task import Task
from src.task_management.task_executor import TaskExecutor
from src.evaluation.evaluation_framework import BasicEvaluator # Import BasicEvaluator
from src.memory.memory import Memory # Import Memory class
from src.plugins.plugin_manager import PluginManager # Import PluginManager class
from src.agent.communication import AgentCommunicationChannel, AgentMessage # Import AgentCommunicationChannel and AgentMessage

class BasicAgent(Agent):
    """
    A basic concrete implementation of the Agent class.
    This agent uses a TaskExecutor to process tasks and includes a basic feedback loop.
    """

    def __init__(self, name: str, llm_connector: LLMInterface, communication_channel: AgentCommunicationChannel, memory: Memory, plugin_manager: PluginManager, capabilities: list = None):
        """
        Initializes a BasicAgent.

        Args:
            name: The name of the agent.
            llm_connector: An instance of a class implementing LLMInterface.
            communication_channel: The communication channel for inter-agent messaging.
            memory: The memory component for the agent to interact with.
            plugin_manager: The plugin manager for the agent to access plugins.
            capabilities: A list of capabilities or task types the agent can handle.
        """
        super().__init__(name, llm_connector, communication_channel, memory, plugin_manager) # Pass communication_channel, memory, and plugin_manager to base class
        self._task_executor = TaskExecutor()
        self._evaluator = BasicEvaluator() # Instantiate the evaluator
        self._capabilities = capabilities or []

    def get_capabilities(self):
        """
        Returns the list of capabilities of the agent.
        """
        return self._capabilities

    def process_task(self, task: Task) -> Task:
        """
        Processes a given task using the agent's LLM connector via the TaskExecutor,
        and then evaluates the result.

        Args:
            task: The Task object to process.

        Returns:
            The updated Task object after processing.
        """
        print(f"Agent '{self.name}' starting to process task: {task.task_id}")
        processed_task = self._task_executor.execute_task(task, self._llm_connector)
        print(f"Agent '{self.name}' finished processing task: {task.task_id} with status: {processed_task.status}")

        # Basic feedback loop: Evaluate the processed task
        print(f"Agent '{self.name}' evaluating task result for: {processed_task.task_id}")
        evaluation_result = self._evaluator.evaluate(processed_task)
        print(f"Evaluation Result for {processed_task.task_id}: {evaluation_result}")

        # Basic feedback loop: Store the task's output data in memory
        memory_key = f"task_output_{processed_task.task_id}"
        self._memory.store(memory_key, processed_task.output_data)
        print(f"Agent '{self.name}' stored task output in memory with key: {memory_key}")

        # Perform memory consolidation after storing
        self._memory.consolidate(max_size=100)
        print(f"Agent '{self.name}' performed memory consolidation.")

        # Demonstrate memory search capability (basic example)
        search_query = "task output" # Example search query
        print(f"Agent '{self.name}' searching memory for: '{search_query}'")
        search_results = self._memory.search(search_query)
        print(f"Agent '{self.name}' memory search results for '{search_query}': {search_results}")

        # Basic adaptation mechanism (placeholder)
        self.adapt(evaluation_result, search_results)

        # In a more advanced system, the agent would use this evaluation_result
        # and search results to refine its approach, update memory, or communicate with other agents.

        return processed_task

    def adapt(self, evaluation_result, search_results):
        """
        A basic placeholder adaptation mechanism.
        This method can be expanded to modify agent behavior based on evaluation and memory search.

        Args:
            evaluation_result: The result of evaluating the last task.
            search_results: The results of searching memory related to the task.
        """
        print(f"Agent '{self.name}' adapting based on evaluation and memory search.")
        # Placeholder logic: just print the inputs
        print(f"Evaluation: {evaluation_result}")
        print(f"Memory Search Results: {search_results}")

    def handle_message(self, message: AgentMessage):
        """
        Basic message handler for the agent.
        This method can be expanded to process different message types and perform actions.

        Args:
            message: The AgentMessage object to handle.
        """
        print(f"Agent '{self.name}' received message from {message.sender_id} of type {message.message_type}")
        # Placeholder: just print the message content
        print(f"Message payload: {message.payload}")

    def delegate_task(self, task: Task, recipient_agent_id: str):
        """
        Delegates a task to another agent by sending a message.

        Args:
            task: The Task object to delegate.
            recipient_agent_id: The ID of the agent to delegate the task to.
        """
        message_payload = {
            "task_id": task.task_id,
            "description": task.description,
            "input_data": task.input_data
        }
        self.send_message(recipient_agent_id, "task_delegation", message_payload, task.task_id)
        print(f"Agent '{self.name}' delegated task {task.task_id} to agent {recipient_agent_id}")

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # This example requires a dummy LLMInterface implementation
    class DummyLLM(LLMInterface):
        def __init__(self, name):
            self._name = name

        def generate_response(self, prompt: str, **kwargs) -> str:
            print(f"DummyLLM '{self._name}' received prompt: {prompt}")
            print(f"DummyLLM received kwargs: {kwargs}")
            if "error_test" in kwargs:
                 raise Exception("Simulated LLM error")
            return f"Dummy response to '{prompt[:30]}...' from {self._name}"

        def get_model_name(self) -> str:
            return self._name

    # Create a dummy LLM connector
    dummy_llm_connector = DummyLLM("dummy-model-alpha")

    # Create a communication channel
    communication_channel = AgentCommunicationChannel()

    # Create a memory instance
    memory = Memory()

    # Create a plugin manager instance
    plugin_manager = PluginManager()

    # Create a BasicAgent instance, passing the communication channel, memory, and plugin manager
    basic_agent = BasicAgent("AlphaAgent", dummy_llm_connector, communication_channel, memory, plugin_manager)

    # Create a task
    task_to_process = Task("Ask the dummy LLM a question", input_data={"prompt": "Tell me a short story."})

    # Process the task using the agent
    completed_task = basic_agent.process_task(task_to_process)

    print("\nTask after processing:")
    print(completed_task)

    # Example with an error
    print("-" * 20)
    error_task = Task("Task that should fail", input_data={"prompt": "Cause an error", "error_test": True})
    failed_task = basic_agent.process_task(error_task)
    print("\nTask after processing (should be failed):")
    print(failed_task)
