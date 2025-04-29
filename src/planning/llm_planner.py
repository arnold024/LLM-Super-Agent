import uuid
import re
import logging
from typing import Dict, Any, List, Optional

from src.planning.planner import AdvancedPlanner
from src.planning.plan_models import Plan, Step, ToolSpec
from src.llm_integration.llm_interface import LLMInterface
from src.memory.memory_interface import MemoryInterface

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMPlanner(AdvancedPlanner):
    """
    A planner that uses an LLM to break down goals into steps.
    """

    def __init__(self, llm: LLMInterface):
        """
        Initializes the LLMPlanner.

        Args:
            llm: An instance of LLMInterface to interact with the language model.
        """
        if not isinstance(llm, LLMInterface):
            raise TypeError("llm must be an instance of LLMInterface")
        self._llm = llm
        logger.info(f"LLMPlanner initialized with LLM: {type(llm).__name__}")

    def generate_plan(self,
                      goal: str,
                      current_state: Dict[str, Any],
                      available_tools: List[ToolSpec],
                      memory_interface: MemoryInterface,
                      plan_history: Optional[List[Plan]] = None) -> Plan:
        """
        Generates a plan using an LLM to break down the goal.

        Args:
            goal: The high-level goal to achieve.
            current_state: The current state of the system (not heavily used by this planner yet).
            available_tools: A list of tools available for executing steps.
            memory_interface: Interface to access memory (not heavily used by this planner yet).
            plan_history: Optional history of previous plans.

        Returns:
            A Plan object containing the steps to achieve the goal.
        """
        plan_id = f"plan_{uuid.uuid4()}"
        logger.info(f"Generating plan {plan_id} for goal: {goal}")

        # --- 1. Craft Prompt ---
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description} (ID: {tool.id})" for tool in available_tools])
        prompt = f"""
You are an expert planning assistant. Your task is to break down the following high-level goal into a sequence of actionable steps.
You have the following tools available:
{tool_descriptions}

Goal: {goal}

Break down the goal into a numbered list of steps. For each step, clearly describe the action to be taken and suggest the most appropriate tool from the list above using the format '[Tool: tool_name]'.

Example Output Format:
1. First step description [Tool: tool_name_1]
2. Second step description [Tool: tool_name_2]
...

Generate the plan now:
"""

        # --- 2. Call LLM ---
        try:
            logger.debug(f"Sending prompt to LLM for plan {plan_id}:\n{prompt}")
            llm_response = self._llm.generate_response(prompt)
            logger.info(f"Received LLM response for plan {plan_id}")
            logger.debug(f"LLM Response:\n{llm_response}")
        except Exception as e:
            logger.error(f"Error calling LLM for plan {plan_id}: {e}", exc_info=True)
            return Plan(
                goal=goal,
                steps=[],
                metadata={
                    "plan_id": plan_id,
                    "strategy_used": "LLM",
                    "status": "failed",
                    "reason": f"LLM API call failed: {e}"
                }
            )

        # --- 3. Parse Response ---
        steps: List[Step] = []
        # Regex to find lines like "1. Description [Tool: tool_name]"
        step_pattern = re.compile(r"^\s*\d+\.\s*(.*?)\s*\[Tool:\s*(\w+)\s*\]\s*$", re.MULTILINE | re.IGNORECASE)
        parsed_steps = step_pattern.findall(llm_response)

        if not parsed_steps:
            logger.warning(f"Could not parse any steps from LLM response for plan {plan_id}. Response:\n{llm_response}")
            # Attempt a simpler parse if the main one fails
            simple_step_pattern = re.compile(r"^\s*\d+\.\s*(.*)", re.MULTILINE)
            simple_parsed_steps = simple_step_pattern.findall(llm_response)
            if simple_parsed_steps:
                 logger.info(f"Using simplified parsing for plan {plan_id}. Tool assignment will be missing.")
                 for i, description in enumerate(simple_parsed_steps):
                     step_id = f"step_{plan_id}_{i+1}"
                     prerequisites = [steps[-1].id] if steps else []
                     step = Step(
                         id=step_id,
                         description=description.strip(),
                         input_data={'goal': description.strip()}, # Placeholder input
                         assigned_agent_tool_id=None, # No tool parsed
                         status="pending",
                         prerequisites=prerequisites
                     )
                     steps.append(step)
            else:
                 return Plan(
                    goal=goal,
                    steps=[],
                    metadata={
                        "plan_id": plan_id,
                        "strategy_used": "LLM",
                        "status": "failed",
                        "reason": "Failed to parse steps from LLM response."
                    }
                 )


        else: # Main parsing logic
            tool_map = {tool.name.lower(): tool.id for tool in available_tools}
            for i, (description, tool_name) in enumerate(parsed_steps):
                step_id = f"step_{plan_id}_{i+1}"
                prerequisites = [steps[-1].id] if steps else []
                description = description.strip()
                tool_name = tool_name.strip().lower()

                # --- Tool Mapping ---
                assigned_tool_id = tool_map.get(tool_name)
                if not assigned_tool_id:
                    logger.warning(f"Plan {plan_id}, Step {i+1}: Tool '{tool_name}' suggested by LLM not found in available tools: {[t.name for t in available_tools]}.")

                # --- Input Data (Placeholder) ---
                input_data = {'goal': description} # Simple placeholder

                step = Step(
                    id=step_id,
                    description=description,
                    input_data=input_data,
                    assigned_agent_tool_id=assigned_tool_id,
                    status="pending",
                    prerequisites=prerequisites
                )
                steps.append(step)

        # --- 4. Create Plan ---
        if not steps:
             logger.warning(f"No steps generated for plan {plan_id} after parsing.")
             return Plan(
                 plan_id=plan_id,
                 goal=goal,
                 steps=[],
                 status="failed",
                 status_reason="No steps could be generated or parsed.",
                 strategy="LLM"
             )

        logger.info(f"Successfully generated plan {plan_id} with {len(steps)} steps.")
        return Plan(
            goal=goal,
            steps=steps,
            metadata={
                "plan_id": plan_id,
                "status": "ready",
                "strategy": "LLM"
            }
        )

    def adjust_plan(self,
                    plan: Plan,
                    feedback: Dict[str, Any],
                    current_state: Dict[str, Any],
                    available_tools: List[ToolSpec],
                    memory_interface: MemoryInterface,
                    plan_history: Optional[List[Plan]] = None) -> Plan:
        """
        Adjusts the plan based on feedback (e.g., step failure).

        Args:
            plan: The current plan to adjust.
            feedback: Feedback from the execution environment (e.g., {'status': 'failure', 'failed_step_id': 'step_xyz', 'reason': '...'}).
            current_state: The current state of the system.
            available_tools: List of available tools.
            memory_interface: Interface to access memory.
            plan_history: Optional history of previous plans.


        Returns:
            The adjusted Plan object.
        """
        logger.info(f"Adjusting plan {plan.plan_id} based on feedback: {feedback}")
        failed_step_id = feedback.get('failed_step_id')

        if failed_step_id and feedback.get('status') == "failed":
            plan.status = "failed"
            plan.status_reason = feedback.get('reason', f"Step {failed_step_id} failed.")
            logger.warning(f"Plan {plan.plan_id} marked as FAILED due to failure in step {failed_step_id}.")

            # Mark failed step and cancel subsequent dependent steps
            step_failed = False
            dependent_steps_to_cancel = set()
            steps_to_process = {failed_step_id}

            # Find all steps that depend directly or indirectly on the failed step
            while steps_to_process:
                current_failed_id = steps_to_process.pop()
                for step in plan.steps:
                    if current_failed_id in step.prerequisites:
                        if step.status not in ("completed", "failed", "cancelled"):
                             dependent_steps_to_cancel.add(step.step_id)
                             steps_to_process.add(step.step_id) # Process dependencies of this step too


            for step in plan.steps:
                if step.step_id == failed_step_id:
                    step.status = "failed"
                    step.result = feedback.get('reason', 'Step failed during execution.')
                    step_failed = True
                elif step.step_id in dependent_steps_to_cancel:
                     step.status = "cancelled"
                     step.result = f"Cancelled due to failure of prerequisite step {failed_step_id} or its dependencies."
                     logger.info(f"Step {step.step_id} in plan {plan.plan_id} cancelled due to dependency failure.")


            if not step_failed:
                 logger.error(f"Failed step ID '{failed_step_id}' provided in feedback not found in plan {plan.plan_id}.")
                 # Optionally revert plan status if the step wasn't found? Or keep as failed?
                 # For now, keep as failed as feedback indicated failure.
                 plan.status_reason = f"Step {failed_step_id} reported as failed but not found in plan."


        else:
            logger.info(f"No adjustment needed for plan {plan.plan_id} based on feedback.")
            # Potentially update plan status if feedback indicates success?
            # For now, only handle failure adjustments.

        return plan