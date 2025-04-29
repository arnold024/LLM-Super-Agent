import pytest
from typing import Dict, Any

from src.planning.strategy_selector import StrategySelector
from src.planning.htn_planner import HTNPlanner
# Import other planners here if needed for future tests
# from src.planning.some_other_planner import SomeOtherPlanner

def test_strategy_selector_initialization():
    """Tests that StrategySelector can be initialized."""
    selector = StrategySelector()
    assert selector is not None
    assert "HTN" in selector._registered_planners # Verify HTN is registered

def test_strategy_selector_selects_htn_by_default():
    """
    Tests that StrategySelector selects the HTNPlanner by default
    based on the current implementation.
    """
    selector = StrategySelector()
    dummy_goal = "Test goal"
    dummy_state: Dict[str, Any] = {"key": "value"}

    selected_planner = selector.select_strategy(goal=dummy_goal, current_state=dummy_state)

    assert selected_planner is not None
    assert isinstance(selected_planner, HTNPlanner)

# Optional: Add tests for selecting other planners if/when implemented
# def test_strategy_selector_selects_other_planner():
#     """Tests selection of a different planner (requires implementation/mocking)."""
#     # Setup selector or mock conditions to select a different planner
#     selector = StrategySelector() # Modify initialization or state if needed
#     dummy_goal = "Goal requiring other planner"
#     dummy_state = {}
#     # selected_planner = selector.select_strategy(goal=dummy_goal, current_state=dummy_state)
#     # assert isinstance(selected_planner, SomeOtherPlanner)
#     pytest.skip("Test for other planner selection not implemented yet.")

# Optional: Add test for handling unregistered strategy
# def test_strategy_selector_raises_error_for_unregistered_strategy():
#     """Tests that an error is raised if the selection logic chooses an unregistered strategy."""
#     selector = StrategySelector()
#     # Mock the internal selection logic to return an invalid strategy name
#     with pytest.raises(ValueError, match="Unsupported planning strategy"):
#          # selector.select_strategy(...) # Call with mocked internal state
#          pass # Placeholder until mocking is implemented
#     pytest.skip("Test for unregistered strategy error not implemented yet.")