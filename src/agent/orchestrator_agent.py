from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from src.task_management.task import Task
from src.agent.agent import Agent
from src.agent.communication import AgentCommunicationChannel, AgentMessage
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager

class OrchestratorAgent(Agent):
    """
    The Orchestrator Agent is responsible for:
    - Interpreting the user's input
    - Decomposing it into one or more tasks
    - Deciding which agent, LLM, or tool should handle each task
    - Collecting and synthesizing the responses
    - Returning a coherent final output
    """

    def __init__(self, name: str, communication_channel: AgentCommunicationChannel, memory: Memory, plugin_manager: PluginManager):
        self._llm_connector = OpenAIChatGPTConnector("gpt-4")
        super().__init__(name, self._llm_connector, communication_channel, memory, plugin_manager)
        self._prompt_template = self._build_prompt_template()

    def _build_prompt_template(self):
        return """
You are the Orchestrator of a multi-agent AI system.
Your job is to:
- Analyze the user's request.
- Break it into specific tasks.
- Assign each task to the best-suited agent or tool:
    - GPT-4: general reasoning, complex planning.
    - Gemini: creativity, imaginative output.
    - Claude: ethical judgment, nuanced conversation.
    - Tool/API: if real-time data or integration is needed.
- Collect all results and return a unified, user-friendly response.

Provide your reasoning for each delegation clearly.

User request: {user_request}
"""

    def process_task(self, task: Task) -> Task:
        user_request = task.input_data.get("prompt", "")
        prompt = self._prompt_template.format(user_request=user_request)

        # Call the orchestrator LLM to get task breakdown and delegation plan
        response_text = self._llm_connector.generate_response(prompt)

        # For simplicity, assume response_text is a JSON string with task breakdown and assignments
        # In a real implementation, parse and validate this JSON
        # Here, we just store the response as output
        task.add_output_data("orchestration_plan", response_text)
        task.update_status("completed")
        return task

    def handle_message(self, message: AgentMessage):
        """
        Basic message handler for the orchestrator agent.
        This method can be expanded to process different message types and perform actions.

        Args:
            message: The AgentMessage object to handle.
        """
        print(f"Orchestrator '{self.name}' received message from {message.sender_id} of type {message.message_type}")
        # Placeholder: just print the message content
        print(f"Message payload: {message.payload}")