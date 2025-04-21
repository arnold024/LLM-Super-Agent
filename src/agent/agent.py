import abc
from typing import Optional, List
from src.llm_integration.llm_interface import LLMInterface
from src.task_management.task import Task
from src.agent.communication import AgentMessage, AgentCommunicationChannel # Import communication classes
from src.memory.memory import Memory # Import Memory class
from src.plugins.plugin_manager import PluginManager # Import PluginManager class

class Agent(abc.ABC):
    """
    Abstract base class for an LLMSuperAgent agent.
    Agents are responsible for processing tasks using an LLM, communicating with other agents, interacting with memory, and potentially using plugins.
    """

    def __init__(self, name: str, llm_connector: LLMInterface, communication_channel: AgentCommunicationChannel, memory: Memory, plugin_manager: PluginManager):
        """
        Initializes an Agent.

        Args:
            name: The name of the agent.
            llm_connector: An instance of a class implementing LLMInterface
                           to be used by this agent.
            communication_channel: The communication channel for inter-agent messaging.
            memory: The memory component for the agent to interact with.
            plugin_manager: The plugin manager for the agent to access plugins.
        """
        self.name = name
        self._llm_connector = llm_connector
        self._communication_channel = communication_channel
        self._memory = memory # Store the memory component
        self._plugin_manager = plugin_manager # Store the plugin manager

    @abc.abstractmethod
    def process_task(self, task: Task) -> Task:
        """
        Processes a given task using the agent's LLM connector.

        Args:
            task: The Task object to process.

        Returns:
            The updated Task object after processing.
        """
        pass

    def get_name(self) -> str:
        """
        Returns the name of the agent.
        """
        return self.name

    def get_llm_model_name(self) -> str:
        """
        Returns the name of the LLM model used by this agent.
        """
        return self._llm_connector.get_model_name()

    def send_message(self, recipient_id: str, message_type: str, payload: dict, task_id: Optional[str] = None):
        """
        Sends a message to another agent via the communication channel.

        Args:
            recipient_id: The ID of the agent to send the message to.
            message_type: The type of message.
            payload: The message content.
            task_id: Optional ID of the task related to the message.
        """
        message = AgentMessage(self.name, recipient_id, message_type, payload, task_id)
        self._communication_channel.send_message(message)

    def receive_messages(self) -> List[AgentMessage]:
        """
        Retrieves messages addressed to this agent from the communication channel.

        Returns:
            A list of AgentMessage objects.
        """
        return self._communication_channel.get_messages_for_recipient(self.name)

    def get_memory(self) -> Memory:
        """
        Returns the agent's memory component.
        """
        return self._memory

    def get_plugin_manager(self) -> PluginManager:
        """
        Returns the agent's plugin manager.
        """
        return self._plugin_manager

# Future methods for agent collaboration, memory interaction, etc., could be added here.