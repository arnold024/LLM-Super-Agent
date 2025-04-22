import logging
from src.orchestrator.capability_based_orchestrator import CapabilityBasedOrchestrator
from src.agent.basic_agent import BasicAgent
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector
from src.agent.communication import AgentCommunicationChannel
from src.memory.memory import Memory
from src.plugins.plugin_manager import PluginManager
from src.task_management.task import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_multi_agent_task():
    # Setup communication channel, memory, and plugin manager
    communication_channel = AgentCommunicationChannel()
    memory = Memory()
    plugin_manager = PluginManager()

    # Create agents with capabilities
    gemini_connector = GoogleGeminiConnector("models/gemini-2.5-flash-preview-04-17")
    chatgpt_connector = OpenAIChatGPTConnector("gpt-4")

    agent_gemini = BasicAgent("GeminiAgent", gemini_connector, communication_channel, memory, plugin_manager, capabilities=["poetry"])
    agent_chatgpt = BasicAgent("ChatGPTAgent", chatgpt_connector, communication_channel, memory, plugin_manager, capabilities=["html"])

    # Create the orchestrator with the agents
    orchestrator = CapabilityBasedOrchestrator(agents=[agent_gemini, agent_chatgpt])

    # Create a main task that requires both poetry and html capabilities
    main_task = Task("Write a poem wrapped in HTML", input_data={"prompt": "Write a poem wrapped in HTML."})

    # Decompose the main task into subtasks manually for this test
    subtask_poem = Task("Write a poem", input_data={"prompt": "Write a poem.", "required_capability": "poetry"})
    # Pass the poem content from Gemini to ChatGPT for wrapping
    poem_content = memory.retrieve(f"task_output_{subtask_poem.task_id}")
    subtask_html = Task("Wrap content in HTML", input_data={"prompt": f"Wrap the following poem in HTML tags:\n{poem_content}", "required_capability": "html"})

    # Add subtasks to the orchestrator with required capabilities
    orchestrator.add_task(subtask_poem, capability="poetry")

    # Run the orchestrator to process the poem first
    orchestrator.run()

    # Retrieve the poem content from memory after processing
    poem_content = memory.retrieve(f"task_output_{subtask_poem.task_id}")["response"]

    # Update the HTML wrapping subtask with the actual poem content
    subtask_html = Task("Wrap content in HTML", input_data={"prompt": f"Wrap the following poem in HTML tags:\n{poem_content}", "required_capability": "html"})

    # Add the updated HTML wrapping subtask to the orchestrator
    orchestrator.add_task(subtask_html, capability="html")

    # Run the orchestrator
    orchestrator.run()

    # Output the results from memory
    for subtask in [subtask_poem, subtask_html]:
        memory_key = f"task_output_{subtask.task_id}"
        output = memory.retrieve(memory_key)
        print(f"\nOutput for subtask '{subtask.description}':")
        print(output)

if __name__ == "__main__":
    test_multi_agent_task()