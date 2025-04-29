import sys
import os
import logging
from typing import List, Dict, Any, Optional

# Add the src directory to the Python path to enable absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Remove old Task and TaskQueue imports if no longer needed directly
# from src.task_management.task import Task
# from src.task_management.task_queue import TaskQueue
# from src.agent.agent import Agent # Keep if agents list is kept, remove otherwise
from src.llm_integration.llm_interface import LLMInterface
# from src.agent.basic_agent import BasicAgent # Remove if not used in example
from src.planning.planner import AdvancedPlanner # Import AdvancedPlanner instead of Planner
from src.planning.plan_models import Plan, Step # Import Plan and Step
from src.planning.strategy_selector import StrategySelector # Import StrategySelector
from src.execution.plan_executor import PlanExecutor # Import PlanExecutor
from src.plugins.plugin_manager import PluginManager # Import PluginManager
from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
from src.llm_integration.openai_chatgpt_connector import OpenAIChatGPTConnector

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimpleOrchestrator:
    """
    A simple orchestrator that manages a task queue and a pool of agents
    to execute tasks sequentially.
    Refactored to use AdvancedPlanner, StrategySelector, PlanExecutor, and Plan objects.
    """

    def __init__(self, plugin_manager: PluginManager, llm_connector: LLMInterface, memory_interface: Optional[Any] = None): # Added llm_connector
        """
        Initializes the SimpleOrchestrator.

        Args:
            plugin_manager: Manages available tools/plugins for plan execution.
            llm_connector: The LLM connector instance to be used by planners requiring it.
            memory_interface: Interface for accessing relevant memory/state (optional).
        """
        # Removed: self._task_queue = TaskQueue()
        # Removed: self._communication_channel = AgentCommunicationChannel()
        # Removed: self._planner = planner
        # Removed agent storage and routing logic
        # self._agents: Dict[str, Agent] = {agent.get_name(): agent for agent in agents}
        # self._agent_names = list(self._agents.keys())
        # self._next_agent_index = 0

        # Prepare configurations for planners that need specific arguments
        planner_configs = {
            "LLM": {"llm": llm_connector}
            # Add configs for other planners like HTN if they need specific init args
        }

        self._strategy_selector = StrategySelector(planner_configs=planner_configs) # Instantiate StrategySelector with configs
        self._plugin_manager = plugin_manager # Store PluginManager (acts as tool registry)
        self._plan_executor = PlanExecutor(tool_registry=self._plugin_manager) # Instantiate PlanExecutor
        self._memory_interface = memory_interface # Store memory interface (optional)

        logging.info("SimpleOrchestrator initialized with StrategySelector and PlanExecutor.")

    # Removed add_task method
    # def add_task(self, task: Task): ...

    def process_goal(self, goal_description: str, current_state: Optional[Dict[str, Any]] = None, plan_history: Optional[List[Plan]] = None) -> Optional[Plan]:
        """
        Processes a high-level goal by selecting a planner, generating a plan.

        Args:
            goal_description: The description of the high-level goal.
            current_state: The current state of the system/environment (optional).
            plan_history: History of previous plans (optional).

        Returns:
            The generated Plan object, or None if planning fails.
        """
        logging.info(f"Orchestrator received goal: '{goal_description}'. Selecting planner and generating plan...")
        # Use StrategySelector to get a planner (assuming a method like select_planner exists)
        # This might need adjustment based on StrategySelector's actual interface
        planner: AdvancedPlanner = self._strategy_selector.select_strategy(goal=goal_description, current_state={}) # Example selection, corrected method call

        if not planner:
            logging.error("StrategySelector failed to select a planner.")
            return None

        # Gather necessary inputs for the planner
        available_tools = [] # TODO: Implement proper ToolSpec retrieval from PluginManager
        # Use provided memory interface or None
        memory_interface = self._memory_interface
        # Use provided current_state or a placeholder
        current_state = current_state if current_state is not None else {}
        # Use provided plan_history or None
        plan_history = plan_history if plan_history is not None else []

        try:
            plan = planner.generate_plan(
                goal=goal_description,
                current_state=current_state,
                available_tools=available_tools,
                memory_interface=memory_interface,
                plan_history=plan_history
            )
            if plan:
                logging.info(f"Planner generated plan with {len(plan.steps)} steps.")
            else:
                logging.warning("Planner returned None (no plan generated).")
            return plan
        except Exception as e:
            logging.error(f"Error during plan generation: {e}", exc_info=True)
            return None

    def run(self, plan: Plan):
        """
        Executes a given plan using the PlanExecutor.

        Args:
            plan: The Plan object to execute.
        """
        if not plan:
            logging.warning("Orchestrator received an empty plan. Nothing to execute.")
            return

        logging.info(f"Orchestrator starting execution of plan {plan.metadata.get('plan_id', 'N/A')}...")
        try:
            # PlanExecutor handles the step-by-step execution
            execution_result = self._plan_executor.execute_plan(plan)
            logging.info(f"Plan {plan.metadata.get('plan_id', 'N/A')} execution finished. Result: {execution_result}")
            # TODO: Handle execution result (e.g., success, failure, partial completion)
        except Exception as e:
            logging.error(f"Error during plan execution: {e}", exc_info=True)
            # TODO: Implement error handling/replanning logic if needed

    # Removed get_tasks method
    # def get_tasks(self) -> List[Task]: ...

    # Removed search_memory method (memory access should be handled via planner/executor context)
    # def search_memory(self, query: str, **kwargs) -> List[Dict[str, Any]]: ...

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Setup necessary components
    from src.memory.memory import Memory
    from src.plugins.plugin_manager import PluginManager
    # Import a specific planner if needed for StrategySelector or direct use (e.g., HTNPlanner)
    # from src.planning.htn_planner import HTNPlanner

    memory = Memory() # Instantiate Memory
    plugin_manager = PluginManager() # Instantiate PluginManager
    # TODO: Register some dummy tools/plugins with the plugin_manager for testing
    # plugin_manager.register_plugin(...)

    # Removed agent instantiation as they are not directly passed to the orchestrator anymore
    # agent_alpha = BasicAgent(...)
    # agent_beta = BasicAgent(...)

    # Removed BasicPlanner instantiation
    # basic_planner = BasicPlanner()

    # Instantiate the refactored orchestrator
    # Pass plugin_manager and optionally memory
    orchestrator = SimpleOrchestrator(plugin_manager=plugin_manager, memory_interface=memory)

    # Process a high-level goal to generate a plan
    high_level_goal = "Develop a simple task management system."
    # Provide placeholders for state, history etc. as needed by the planner selected by StrategySelector
    generated_plan = orchestrator.process_goal(
        goal_description=high_level_goal,
        current_state={}, # Placeholder
        plan_history=[] # Placeholder
    )

    # Execute the generated plan
    if generated_plan:
        orchestrator.run(plan=generated_plan)
    else:
        logging.error("Failed to generate a plan for the goal.")