from typing import List, Dict, Any, Optional, NamedTuple
from dataclasses import dataclass, field

# Define ToolSpec - represents available tools/agents
# Using NamedTuple for simplicity, could be a dataclass if more complexity needed
class ToolSpec(NamedTuple):
    """Specification for an available tool or agent."""
    id: str
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None

@dataclass
class Step:
    """Represents a single step within a plan."""
    id: str
    description: str
    prerequisites: List[str] = field(default_factory=list) # List of Step IDs this step depends on
    assigned_agent_tool_id: Optional[str] = None # ID of the agent or tool assigned
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict) # To store results after execution
    status: str = "pending" # e.g., pending, running, completed, failed

@dataclass
class Plan:
    """Represents a structured plan to achieve a goal."""
    goal: str
    steps: List[Step] = field(default_factory=list)
    # Dependencies represented within Step.prerequisites
    # Assignments represented within Step.assigned_agent_tool_id
    metadata: Dict[str, Any] = field(default_factory=dict) # e.g., plan_id, timestamp, strategy_used

    def get_step_by_id(self, step_id: str) -> Optional[Step]:
        """Helper method to find a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_ready_steps(self) -> List[Step]:
        """Returns steps whose prerequisites are met (completed)."""
        ready_steps = []
        completed_step_ids = {step.id for step in self.steps if step.status == "completed"}
        for step in self.steps:
            if step.status == "pending":
                # Check if all prerequisites are in the completed set
                if all(prereq_id in completed_step_ids for prereq_id in step.prerequisites):
                    ready_steps.append(step)
        return ready_steps

    def get_next_steps(self) -> List[Step]:
        """
        Identifies the next steps to be executed.
        These are pending steps with no pending prerequisites.
        """
        next_steps = []
        pending_or_running_step_ids = {step.id for step in self.steps if step.status in ["pending", "running"]}
        for step in self.steps:
            if step.status == "pending":
                # Check if any prerequisite is still pending or running
                has_pending_prereqs = any(prereq_id in pending_or_running_step_ids for prereq_id in step.prerequisites)
                if not has_pending_prereqs:
                    next_steps.append(step)
        return next_steps