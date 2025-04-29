import logging
from typing import List, Any, Optional, Dict

# Assuming Plan and Step models are defined in src.planning.plan_models
# Adjust the import path if necessary
from src.planning.plan_models import Plan, Step

# Placeholder for PluginManager/ToolRegistry - adjust import as needed
# from src.plugins.plugin_manager import PluginManager
class PluginManager: # Placeholder
    def get_tool(self, tool_id: str) -> Any:
        # Placeholder implementation: Return a dummy function
        logging.warning(f"Using placeholder PluginManager.get_tool for tool_id: {tool_id}")
        def dummy_tool(input_data: Any) -> Dict[str, Any]:
            print(f"Executing dummy tool '{tool_id}' with input: {input_data}")
            return {"result": f"dummy output for {tool_id}", "status": "success"}
        return dummy_tool

# Placeholder for AdvancedPlanner - adjust import as needed
# from src.planning.planner import AdvancedPlanner # Assuming base class or interface
class AdvancedPlanner: # Placeholder
    def adjust_plan(self, plan: Plan, feedback: Dict[str, Any]) -> Plan:
        logging.warning(f"Using placeholder AdvancedPlanner.adjust_plan")
        # Placeholder: Simply mark the plan as failed if adjustment is needed
        plan.status = "failed" # Or a specific 'needs_adjustment' status if defined
        return plan

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlanExecutor:
    """
    Orchestrates the execution of a Plan object by managing step dependencies,
    invoking tools/agents, and handling results.
    """
    def __init__(self, tool_registry: PluginManager, planner: Optional[AdvancedPlanner] = None):
        """
        Initializes the PlanExecutor.

        Args:
            tool_registry: An instance capable of resolving tool IDs to executable tools.
                           Expected to have a `get_tool(tool_id: str) -> Callable` method.
            planner: An optional AdvancedPlanner instance for handling plan adjustments on failure.
                     Expected to have an `adjust_plan(plan: Plan, feedback: Dict) -> Plan` method.
        """
        if not hasattr(tool_registry, 'get_plugin') or not callable(getattr(tool_registry, 'get_plugin')):
            raise TypeError("tool_registry must have a 'get_plugin' method")
        if planner and not hasattr(planner, 'adjust_plan'):
             raise TypeError("planner must have an 'adjust_plan' method if provided")

        self.tool_registry = tool_registry
        self.planner = planner
        self.logger = logging.getLogger(__name__)

    def execute_plan(self, plan: Plan) -> Plan:
        """
        Executes the given plan sequentially based on step dependencies.

        Args:
            plan: The Plan object to execute.

        Returns:
            The updated Plan object with final statuses and outputs.
        """
        self.logger.info(f"Starting execution of plan: {plan.metadata.get('plan_id', 'N/A')}")
        plan.status = "running" # Mark plan as running

        # Ensure all steps start as pending unless already completed/failed externally
        for step in plan.steps:
            if step.status not in ["completed", "failed", "skipped"]:
                 step.status = "pending"

        executed_steps_in_iteration = True # Flag to detect cycles or stalls
        while self._has_pending_steps(plan) and executed_steps_in_iteration:
            executed_steps_in_iteration = False
            ready_steps = self._get_ready_steps(plan)

            if not ready_steps and self._has_pending_steps(plan):
                 # Check if there are blocked steps due to failures
                 if any(s.status == "failed" for s in plan.steps):
                     self.logger.warning(f"Plan execution halted. Some steps failed, blocking remaining pending steps.")
                     plan.status = "failed" # Mark plan as failed if steps failed and blocked others
                     break # Exit loop if steps failed and nothing is ready
                 else:
                     # This might indicate a cycle or an issue in prerequisite logic
                     self.logger.error(f"Plan execution stalled: No ready steps found, but pending steps remain. Check for cycles or prerequisite issues.")
                     plan.status = "failed" # Consider it failed due to stall
                     break # Exit loop due to stall

            for step in ready_steps:
                self.logger.info(f"Executing step: {step.id} ({step.description})")
                step.status = "running"
                executed_steps_in_iteration = True
                try:
                    result = self._execute_step(step)
                    self._handle_step_result(step, result, plan)
                except Exception as e:
                    self.logger.error(f"Error executing step {step.id}: {e}", exc_info=True)
                    self._handle_step_result(step, e, plan, is_exception=True)

                # If a step failed and no planner is available, or planner failed to adjust, stop.
                if step.status == "failed" and (not self.planner or plan.status == "failed"):
                     self.logger.error(f"Step {step.id} failed. Halting plan execution.")
                     plan.status = "failed"
                     return plan # Return immediately on critical failure

        # Final plan status check
        if plan.status == "running": # If not already marked failed
             if all(s.status == "completed" or s.status == "skipped" for s in plan.steps):
                 plan.status = "completed"
                 self.logger.info(f"Plan {plan.metadata.get('plan_id', 'N/A')} completed successfully.")
             elif self._has_pending_steps(plan):
                 # Should not happen if loop logic is correct, but as a safeguard
                 self.logger.warning(f"Plan {plan.plan_id} finished with pending steps. Marking as failed.")
                 plan.status = "failed"
             else: # Some steps failed, but loop completed
                 plan.status = "failed"
                 self.logger.warning(f"Plan {plan.plan_id} finished with failed steps.")

        return plan

    def _has_pending_steps(self, plan: Plan) -> bool:
        """Checks if there are any steps in the plan with PENDING status."""
        return any(step.status == "pending" for step in plan.steps)

    def _get_ready_steps(self, plan: Plan) -> List[Step]:
        """
        Identifies steps that are PENDING and whose prerequisites are met (COMPLETED).

        Args:
            plan: The Plan object.

        Returns:
            A list of Step objects that are ready to be executed.
        """
        ready_steps = []
        step_status_map = {step.id: step.status for step in plan.steps}

        for step in plan.steps:
            if step.status == "pending":
                prerequisites_met = True
                if step.prerequisites:
                    for prereq_id in step.prerequisites:
                        prereq_status = step_status_map.get(prereq_id)
                        # Prerequisite must be completed. If it failed or is pending/running, the step isn't ready.
                        if prereq_status != "completed":
                            prerequisites_met = False
                            # If a prerequisite failed, this step might become implicitly failed or skipped later,
                            # but for now, it's just not ready.
                            if prereq_status == "failed":
                                self.logger.debug(f"Step {step.id} prerequisite {prereq_id} failed.")
                            break # No need to check other prerequisites for this step
                
                if prerequisites_met:
                    ready_steps.append(step)
                    
        self.logger.debug(f"Found {len(ready_steps)} ready steps: {[s.id for s in ready_steps]}")
        return ready_steps

    def _execute_step(self, step: Step) -> Any:
        """
        Invokes the tool associated with the step.

        Args:
            step: The Step object to execute.

        Returns:
            The result from the tool execution.

        Raises:
            Exception: If the tool cannot be found or execution fails.
        """
        if not step.assigned_agent_tool_id:
            raise ValueError(f"Step {step.id} has no assigned_agent_tool_id.")

        self.logger.debug(f"Invoking tool '{step.assigned_agent_tool_id}' for step {step.id}")
        
        # Use the helper method to invoke the tool
        return self._invoke_tool(step.assigned_agent_tool_id, step.input_data)


    def _invoke_tool(self, tool_id: str, input_data: Any) -> Any:
        """
        Helper method to look up and execute a tool by its ID.

        Args:
            tool_id: The ID of the tool to invoke.
            input_data: The input data to pass to the tool.

        Returns:
            The result of the tool execution.

        Raises:
            ValueError: If the tool ID is not found.
            Exception: Propagates exceptions from the tool execution.
        """
        try:
            tool = self.tool_registry.get_plugin(tool_id)
            if not callable(tool):
                 raise TypeError(f"Resolved tool '{tool_id}' is not callable.")
            self.logger.debug(f"Executing tool '{tool_id}' with input: {input_data}")
            # Assuming tools might return complex objects or dicts
            result = tool(input_data) 
            return result
        except Exception as e:
            self.logger.error(f"Failed to find or execute tool '{tool_id}': {e}", exc_info=True)
            # Re-raise to be caught by the main execution loop
            raise


    def _handle_step_result(self, step: Step, result: Any, plan: Plan, is_exception: bool = False):
        """
        Updates the step status and output based on the execution result or exception.
        Optionally triggers plan adjustment if a planner is configured.

        Args:
            step: The Step that was executed.
            result: The result returned by the tool, or the Exception object if execution failed.
            plan: The overall Plan object.
            is_exception: Flag indicating if the result is an Exception.
        """
        if is_exception:
            step.status = "failed"
            step.output_data = {"error": str(result), "details": repr(result)} # Store error info
            self.logger.warning(f"Step {step.id} failed due to exception: {result}")

            # Trigger replanning/adjustment if planner is available
            if self.planner:
                self.logger.info(f"Attempting plan adjustment due to failure in step {step.id}.")
                try:
                    feedback = {"failed_step_id": step.id, "error": str(result)}
                    # The planner might modify the plan in place or return a new one
                    # For simplicity, assume it modifies in place or we replace the reference
                    adjusted_plan = self.planner.adjust_plan(plan, feedback)
                    # If planner returns a new object, we might need to handle it,
                    # but current design implies modification or status update on the original plan.
                    # If adjust_plan marks the plan as failed, execution will halt.
                    if adjusted_plan.status == "failed":
                         self.logger.warning(f"Planner marked plan {plan.plan_id} as failed after adjustment attempt.")
                         # Ensure the main loop knows the plan failed overall
                         plan.status = "failed"
                except Exception as planner_ex:
                    self.logger.error(f"Planner failed to adjust plan after step {step.id} failure: {planner_ex}", exc_info=True)
                    # If planner fails, the plan execution should probably halt critically.
                    plan.status = "failed"

        else:
            # Assuming successful execution implies the tool returns meaningful output
            step.status = "completed"
            step.output_data = result # Store the successful result
            self.logger.info(f"Step {step.id} completed successfully.")
            # Potentially log result summary if needed: self.logger.debug(f"Step {step.id} result: {result}")