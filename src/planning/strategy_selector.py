from typing import Dict, Any, Type
import logging

from src.planning.planner import AdvancedPlanner
from src.planning.htn_planner import HTNPlanner
from src.planning.llm_planner import LLMPlanner # Added import
# Import other planner implementations here as they are created
# from .some_other_planner import SomeOtherPlanner

logger = logging.getLogger(__name__)

class StrategySelector:
    """
    Selects the appropriate planning strategy (and corresponding planner implementation)
    based on the goal, current state, or other context.
    """

    def __init__(self, planner_configs: Dict[str, Dict[str, Any]] = None):
        """
        Initializes the StrategySelector.

        Args:
            planner_configs: Optional configuration for different planners.
                             Example: {"HTN": {"llm_connector": llm_instance}, "LLM": {"llm_connector": llm_instance}}
        """
        self._planner_configs = planner_configs or {}
        # Register available planner types/classes
        self._registered_planners: Dict[str, Type[AdvancedPlanner]] = {
            "HTN": HTNPlanner,
            "LLM": LLMPlanner, # Added LLMPlanner
            # "OTHER": SomeOtherPlanner,
        }
        logger.info("StrategySelector initialized.")
        logger.info(f"Registered planners: {list(self._registered_planners.keys())}")

    def select_strategy(self, goal: str, current_state: Dict[str, Any]) -> AdvancedPlanner:
        """
        Selects and instantiates the appropriate planner based on the context.

        Args:
            goal: The goal description.
            current_state: The current state or context.

        Returns:
            An instantiated AdvancedPlanner implementation.
        """
        logger.info(f"Selecting planning strategy for goal: '{goal}'")

        # TODO: Implement more sophisticated selection logic based on goal, state, etc.
        # For now, default to HTNPlanner if available.
        selected_strategy_name = "LLM" # Default strategy changed to LLM

        if selected_strategy_name in self._registered_planners:
            planner_class = self._registered_planners[selected_strategy_name]
            config = self._planner_configs.get(selected_strategy_name, {})
            try:
                # Instantiate the planner with its specific configuration
                planner_instance = planner_class(**config)
                logger.info(f"Selected strategy: {selected_strategy_name} -> Instantiated {planner_class.__name__}")
                return planner_instance
            except Exception as e:
                logger.error(f"Failed to instantiate planner {planner_class.__name__} with config {config}: {e}", exc_info=True)
                raise ValueError(f"Could not instantiate planner for strategy '{selected_strategy_name}'") from e
        else:
            logger.error(f"No registered planner found for the selected strategy: {selected_strategy_name}")
            raise ValueError(f"Unsupported planning strategy: {selected_strategy_name}")

# Example Usage (can be removed or moved to tests)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # Example: No specific config needed for HTNPlanner in its current form
    selector = StrategySelector()

    # Example: If HTNPlanner needed an LLM connector
    # from src.llm_integration.google_gemini_connector import GoogleGeminiConnector
    # gemini_connector = GoogleGeminiConnector("gemini-pro")
    # configs = {"HTN": {"llm_connector": gemini_connector}}
    # selector_with_config = StrategySelector(planner_configs=configs)

    try:
        test_goal = "Organize a surprise party"
        test_state = {"budget": 500, "guest_count": 20}
        selected_planner = selector.select_strategy(test_goal, test_state)
        print(f"\nSuccessfully selected planner: {type(selected_planner).__name__}")

        # You could then use the planner instance:
        # plan = selected_planner.generate_plan(test_goal, test_state, [], None) # Assuming MemoryInterface is None for example
        # print(f"\nGenerated plan (placeholder): {plan}")

    except ValueError as e:
        print(f"\nError selecting strategy: {e}")
    except Exception as e:
         print(f"\nAn unexpected error occurred: {e}")