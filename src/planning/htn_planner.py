import uuid
from typing import List, Dict, Any, Optional, Tuple, Callable

from src.planning.planner import AdvancedPlanner
from src.planning.plan_models import Plan, Step, ToolSpec
from src.memory.memory_interface import MemoryInterface
from src.llm_integration.llm_interface import LLMInterface

# Define types for clarity
Task = Any # Can be a string name, a tuple, etc.
State = Dict[str, Any]
Method = Callable[[State, Task], Optional[List[Task]]] # Returns subtasks or None if not applicable
Operator = Callable[[State, Task], Optional[State]] # Represents primitive actions, returns new state if applicable (or just confirms applicability)

class HTNPlanner(AdvancedPlanner):
    """
    A planner implementation based on Hierarchical Task Networks (HTN).
    It decomposes high-level tasks into smaller, manageable steps (primitive operators).
    """

    def __init__(self, llm_connector: Optional[LLMInterface] = None):
        """
        Initializes the HTNPlanner.
        """
        self._llm = llm_connector
        self._methods: Dict[str, List[Method]] = {}
        self._operators: Dict[str, Operator] = {}
        self._define_simple_coffee_domain() # Load domain knowledge
        print("HTNPlanner initialized with simple coffee domain.")
        if self._llm:
            print(f"Using LLM: {self._llm.get_model_name()} for potential decomposition assistance.")

    def _define_simple_coffee_domain(self):
        """Defines a basic HTN domain for making coffee."""

        # --- Operators (Primitive Actions) ---
        def op_get_water(state: State, task: Task) -> Optional[State]:
            # In a real scenario, check preconditions (e.g., have container)
            # and apply effects (e.g., state['has_water'] = True)
            print(f"Executing primitive: {task}")
            # For this example, just confirm applicability
            return state # Placeholder: Assume always applicable and state doesn't change visibly here

        def op_add_coffee(state: State, task: Task) -> Optional[State]:
            print(f"Executing primitive: {task}")
            return state

        def op_brew_coffee(state: State, task: Task) -> Optional[State]:
            print(f"Executing primitive: {task}")
            return state

        self._operators = {
            "get_water": op_get_water,
            "add_coffee_grounds": op_add_coffee,
            "brew": op_brew_coffee,
        }

        # --- Methods (Decomposition Logic) ---
        def method_make_coffee_simple(state: State, task: Task) -> Optional[List[Task]]:
            # This method applies if the goal is 'make_coffee'
            # It decomposes into a sequence of primitive operators.
            # In a real system, methods would have preconditions.
            print(f"Applying method 'method_make_coffee_simple' to task: {task}")
            return ["get_water", "add_coffee_grounds", "brew"]

        # Register methods for the 'make_coffee' task
        self._methods["make_coffee"] = [method_make_coffee_simple]


    def is_primitive(self, task: Task) -> bool:
        """Checks if a task is a primitive operator."""
        # Check if the task name (assuming string) exists in the operators dictionary
        return isinstance(task, str) and task in self._operators

    def _decompose(self, task: Task, state: State) -> Optional[List[Task]]:
        """
        Attempts to decompose a non-primitive task using applicable methods.
        Returns a list of subtasks if successful, None otherwise.
        """
        if self.is_primitive(task):
            # Primitive tasks cannot be decomposed further by methods
            print(f"Task '{task}' is primitive, cannot decompose.")
            return None # Indicate it's primitive and no decomposition needed here

        print(f"Attempting to decompose task: {task}")
        if isinstance(task, str) and task in self._methods:
            applicable_methods = self._methods[task]
            for method in applicable_methods:
                # In a real system, check method preconditions against the state here
                # For now, assume the first method found is applicable
                subtasks = method(state, task)
                if subtasks is not None:
                    print(f"Decomposition successful using method {method.__name__}: {subtasks}")
                    return subtasks # Return the first successful decomposition
            print(f"No applicable method found for task: {task}")
            return None # No suitable method found
        else:
            print(f"Task '{task}' is not recognized as a compound task with defined methods.")
            return None


    def generate_plan(self,
                      goal: str,
                      current_state: Dict[str, Any],
                      available_tools: List[ToolSpec], # Note: Not used in this simplified version
                      memory_interface: MemoryInterface, # Note: Not used in this simplified version
                      plan_history: Optional[List[Plan]] = None) -> Plan:
        """
        Generates a plan using HTN decomposition with iterative, depth-first processing.
        """
        print(f"HTNPlanner generating plan for goal: '{goal}'")
        plan_id = str(uuid.uuid4())
        plan_steps_in_order: List[Step] = [] # Store steps as they are finalized
        step_counter = 0
        last_step_id: Optional[str] = None

        agenda: List[Task] = [goal] # Tasks to be processed (acts like a stack due to list insertion)

        while agenda:
            current_task = agenda.pop(0) # Process tasks FIFO (effectively depth-first due to insertion)

            if self.is_primitive(current_task):
                print(f"Processing primitive task: {current_task}")
                step_id = f"step_{plan_id}_{step_counter}"
                step_counter += 1
                # --- Find matching tool for the primitive task ---
                assigned_tool_id: Optional[str] = None
                found_tool = False
                for tool in available_tools:
                    # Simple matching by name for now
                    if tool.name == current_task:
                        assigned_tool_id = tool.id
                        found_tool = True
                        print(f"  Mapping primitive task '{current_task}' to tool ID: {assigned_tool_id}")
                        break # Stop searching once found

                if not found_tool:
                    # Option A: Warn and leave as None
                    print(f"  Warning: No matching tool found in available_tools for primitive task '{current_task}'. assigned_agent_tool_id will be None.")
                # --- End tool finding ---

                new_step = Step(
                    id=step_id,
                    description=f"Execute primitive action: {current_task}",
                    prerequisites=[last_step_id] if last_step_id else [],
                    assigned_agent_tool_id=assigned_tool_id, # Use the found ID or None
                    input_data={"task": current_task} # Basic input
                )
                plan_steps_in_order.append(new_step)
                last_step_id = step_id # Update the last step for sequential dependency
            else:
                # Try to decompose the compound task
                subtasks = self._decompose(current_task, current_state)
                if subtasks:
                    print(f"Decomposed '{current_task}' into: {subtasks}")
                    # Add the subtasks to the *front* of the agenda in their original order
                    # This ensures depth-first expansion
                    agenda = subtasks + agenda
                else:
                    # If decomposition returns None AND the task is not primitive, it's an error
                    print(f"Error: Could not decompose non-primitive task '{current_task}'. Aborting plan generation.")
                    return Plan(
                        goal=goal,
                        steps=[],
                        metadata={"plan_id": plan_id, "strategy_used": "HTN", "status": "failed", "reason": f"Cannot decompose task: {current_task}"}
                    )

        # Check if any steps were generated
        if not plan_steps_in_order:
             print(f"Warning: No plan steps generated for goal '{goal}'. The goal might be primitive or decomposition failed immediately.")
             status = "failed" if not self.is_primitive(goal) else "success_empty" # Distinguish no-op from failure
             reason = "Goal is primitive or no decomposition possible." if self.is_primitive(goal) else "Decomposition failed."
             return Plan(goal=goal, steps=[], metadata={"plan_id": plan_id, "strategy_used": "HTN", "status": status, "reason": reason})


        plan = Plan(
            goal=goal,
            steps=plan_steps_in_order,
            metadata={"plan_id": plan_id, "strategy_used": "HTN", "status": "success"}
        )
        print(f"HTNPlanner generated plan with {len(plan.steps)} steps.")
        return plan


    def adjust_plan(self,
                    current_plan: Plan,
                    feedback: Dict[str, Any],
                    current_state: Dict[str, Any], # Not used in this basic version
                    memory_interface: MemoryInterface # Not used in this basic version
                    ) -> Plan:
        """
        Adjusts the plan based on feedback, specifically handling failed steps.
        Marks the failed step and cancels all subsequent dependent steps.
        """
        print(f"HTNPlanner adjusting plan {current_plan.metadata.get('plan_id', 'N/A')} based on feedback: {feedback}")

        failed_step_id = feedback.get('failed_step_id')

        if not failed_step_id:
            print("No failed_step_id in feedback. Returning original plan.")
            return current_plan

        # Find the failed step
        failed_step = current_plan.get_step_by_id(failed_step_id)
        if not failed_step:
            print(f"Error: Failed step ID '{failed_step_id}' not found in the plan. Returning original plan.")
            # Optionally update metadata to indicate adjustment error
            current_plan.metadata['status'] = 'adjustment_error'
            current_plan.metadata['error_reason'] = f"Failed step ID '{failed_step_id}' not found."
            return current_plan

        print(f"Found failed step: {failed_step.id} - {failed_step.description}")
        failed_step.status = "failed"
        current_plan.metadata['status'] = 'failed' # Update plan status
        current_plan.metadata['failure_reason'] = feedback.get('reason', 'Step failed')
        current_plan.metadata['failed_step_id'] = failed_step_id

        # Find and cancel subsequent steps
        steps_to_cancel = set()
        queue = [failed_step_id] # Start BFS from the failed step

        processed_for_deps = set() # Avoid infinite loops in cyclic dependencies (though unlikely here)

        while queue:
            current_dep_id = queue.pop(0)
            if current_dep_id in processed_for_deps:
                continue
            processed_for_deps.add(current_dep_id)

            for step in current_plan.steps:
                # If a step depends on the current_dep_id and is not already failed/cancelled
                if current_dep_id in step.prerequisites and step.status not in ["failed", "cancelled"]:
                    if step.id not in steps_to_cancel:
                        steps_to_cancel.add(step.id)
                        queue.append(step.id) # Add dependent step to the queue to find its dependents

        if steps_to_cancel:
            print(f"Cancelling subsequent steps: {steps_to_cancel}")
            for step_id_to_cancel in steps_to_cancel:
                step_to_cancel = current_plan.get_step_by_id(step_id_to_cancel)
                if step_to_cancel:
                    step_to_cancel.status = "cancelled"
                    step_to_cancel.output_data = {"reason": f"Cancelled due to failure of prerequisite step {failed_step_id}"} # Add reason
        else:
            print("No subsequent steps found to cancel.")


        print(f"Plan adjusted. Final status: {current_plan.metadata['status']}")
        return current_plan

# Note: _decompose method was previously defined below adjust_plan, moved it up for better structure.