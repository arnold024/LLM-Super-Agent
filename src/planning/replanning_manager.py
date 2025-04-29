from typing import Dict, Any, Optional

from src.planning.planner import AdvancedPlanner
from src.planning.plan_models import Plan
from src.memory.memory_interface import MemoryInterface

class ReplanningManager:
    """
    Manages the process of monitoring plan execution and triggering
    replanning or plan adjustments based on feedback.
    """

    def __init__(self, planner: AdvancedPlanner, memory_interface: MemoryInterface):
        """
        Initializes the ReplanningManager.

        Args:
            planner: An instance of an AdvancedPlanner implementation used for adjustments.
            memory_interface: Interface to access memory for context during replanning.
        """
        self._planner = planner
        self._memory = memory_interface
        print("ReplanningManager initialized.")

    def monitor_execution_step(self, current_plan: Plan, step_id: str, feedback: Dict[str, Any], current_state: Dict[str, Any]) -> Optional[Plan]:
        """
        Processes feedback for a specific step and decides if replanning is needed.

        Args:
            current_plan: The plan currently being executed.
            step_id: The ID of the step that just finished or produced feedback.
            feedback: Information about the step's execution (e.g., status, output, errors).
            current_state: The updated state of the system/environment after the step.

        Returns:
            An updated Plan object if replanning occurred, otherwise None.
        """
        print(f"ReplanningManager monitoring step: {step_id} with feedback: {feedback}")

        step = current_plan.get_step_by_id(step_id)
        if not step:
            print(f"Error: Step {step_id} not found in plan.")
            return None # Or raise error

        # Update step status based on feedback
        step.status = feedback.get("status", step.status)
        step.output_data = feedback.get("output_data", step.output_data)

        # Basic replanning trigger: if a step fails
        if step.status == "failed":
            print(f"Step {step_id} failed. Triggering plan adjustment...")
            try:
                adjusted_plan = self._planner.adjust_plan(
                    current_plan=current_plan,
                    feedback=feedback,
                    current_state=current_state,
                    memory_interface=self._memory
                )
                print("Plan adjustment completed.")
                return adjusted_plan
            except Exception as e:
                print(f"Error during plan adjustment: {e}")
                # Handle adjustment error (e.g., log, return original plan, raise)
                return current_plan # Return original plan on adjustment error for now
        else:
            print(f"Step {step_id} completed or in progress. No immediate replanning triggered.")
            # Potentially add more sophisticated triggers based on feedback content
            return None # No replanning needed based on this feedback

    def trigger_replan(self, current_plan: Plan, reason: str, current_state: Dict[str, Any]) -> Plan:
        """
        Explicitly triggers a replan or adjustment based on an external event or condition.

        Args:
            current_plan: The plan currently being executed.
            reason: A description of why replanning is needed.
            current_state: The current state of the system/environment.

        Returns:
            An updated Plan object.
        """
        print(f"ReplanningManager explicitly triggering replan for plan {current_plan.metadata.get('plan_id', 'N/A')}. Reason: {reason}")
        feedback = {"trigger": "explicit", "reason": reason}
        try:
            adjusted_plan = self._planner.adjust_plan(
                current_plan=current_plan,
                feedback=feedback,
                current_state=current_state,
                memory_interface=self._memory
            )
            print("Explicit plan adjustment completed.")
            return adjusted_plan
        except Exception as e:
            print(f"Error during explicit plan adjustment: {e}")
            return current_plan # Return original plan on error