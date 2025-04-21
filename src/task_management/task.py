import uuid
from typing import Any, Dict, Optional, List

class Task:
    """
    Represents a single task to be processed by the LLMSuperAgent.
    """

    def __init__(self,
                 description: str,
                 task_id: Optional[str] = None,
                 input_data: Optional[Dict[str, Any]] = None,
                 status: str = "pending",
                 assigned_llm: Optional[str] = None,
                 output_data: Optional[Dict[str, Any]] = None,
                 parent_task_id: Optional[str] = None, # Add parent task ID
                 sub_task_ids: Optional[List[str]] = None): # Add sub-task IDs
        """
        Initializes a new Task.

        Args:
            description: A brief description of the task.
            task_id: A unique identifier for the task. If None, a UUID will be generated.
            input_data: Optional dictionary containing input data for the task.
            status: The current status of the task (e.g., "pending", "in_progress", "completed", "failed").
            assigned_llm: The name of the LLM assigned to this task, if any.
            output_data: Optional dictionary containing output data from the task after completion.
            parent_task_id: Optional ID of the parent task if this is a sub-task.
            sub_task_ids: Optional list of IDs of sub-tasks created from this task.
        """
        self.task_id = task_id if task_id is not None else str(uuid.uuid4())
        self.description = description
        self.input_data = input_data if input_data is not None else {}
        self.status = status
        self.assigned_llm = assigned_llm
        self.output_data = output_data if output_data is not None else {}
        self.parent_task_id = parent_task_id
        self.sub_task_ids = sub_task_ids if sub_task_ids is not None else []

    def __repr__(self) -> str:
        return (f"Task(task_id='{self.task_id[:8]}...', description='{self.description[:50]}...', "
                f"status='{self.status}', assigned_llm='{self.assigned_llm}', "
                f"parent_id='{self.parent_task_id[:8] if self.parent_task_id else None}', " # Include parent_task_id
                f"sub_ids={len(self.sub_task_ids)}, " # Include sub_task_ids count
                f"input_data_keys={list(self.input_data.keys())}, "
                f"output_data_keys={list(self.output_data.keys())})")

    def update_status(self, new_status: str):
        """Updates the status of the task."""
        self.status = new_status

    def assign_llm(self, llm_name: str):
        """Assigns an LLM to the task."""
        self.assigned_llm = llm_name

    def add_input_data(self, key: str, value: Any):
        """Adds or updates input data for the task."""
        self.input_data[key] = value

    def add_output_data(self, key: str, value: Any):
        """Adds or updates output data for the task."""
        self.output_data[key] = value

    def add_sub_task_id(self, sub_task_id: str):
        """Adds a sub-task ID to the list of sub-tasks."""
        if sub_task_id not in self.sub_task_ids:
            self.sub_task_ids.append(sub_task_id)

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    task1 = Task("Analyze sentiment of customer reviews", input_data={"reviews": ["good", "bad"]})
    print(task1)
    task1.update_status("in_progress")
    task1.assign_llm("generic-llm")
    print(task1)
    task1.add_output_data("sentiment", "mixed")
    task1.update_status("completed")
    print(task1)

    print("-" * 20)

    task2 = Task("Summarize a document", description="Summarize the provided text.", task_id="summary-task-123")
    print(task2)

    print("-" * 20)

    # Example with parent/sub-tasks
    parent_task = Task("Process report and summarize findings")
    sub_task_1 = Task("Process report", parent_task_id=parent_task.task_id)
    sub_task_2 = Task("Summarize findings", parent_task_id=parent_task.task_id)
    parent_task.add_sub_task_id(sub_task_1.task_id)
    parent_task.add_sub_task_id(sub_task_2.task_id)

    print("Parent Task:")
    print(parent_task)
    print("Sub-task 1:")
    print(sub_task_1)
    print("Sub-task 2:")
    print(sub_task_2)