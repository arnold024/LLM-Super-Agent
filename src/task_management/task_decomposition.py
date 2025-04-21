from typing import List, Optional
from src.task_management.task import Task

class TaskDecomposer:
    """
    A basic task decomposer that can break down a complex task into simpler sub-tasks.
    This is a placeholder for more sophisticated decomposition strategies.
    """

    def decompose(self, task: Task) -> List[Task]:
        """
        Decomposes a task into a list of sub-tasks.

        Args:
            task: The Task object to decompose.

        Returns:
            A list of new Task objects representing the sub-tasks.
            Returns a list containing the original task if no decomposition is performed.
        """
        print(f"Attempting to decompose task: {task.task_id} - '{task.description}'")

        # Basic placeholder decomposition logic:
        # If the task description contains " and ", split it into two sub-tasks.
        if " and " in task.description:
            sub_descriptions = task.description.split(" and ", 1)
            sub_tasks = []
            for i, desc in enumerate(sub_descriptions):
                # Create new tasks with a reference to the parent task
                sub_task = Task(
                    description=desc.strip(),
                    input_data=task.input_data, # Inherit input data for simplicity
                    parent_task_id=task.task_id # Set the parent task ID
                )
                task.add_sub_task_id(sub_task.task_id) # Add sub-task ID to the parent task
                print(f"  Created sub-task {sub_task.task_id}: '{sub_task.description}' (Parent: {sub_task.parent_task_id[:8]}...)")
                sub_tasks.append(sub_task)
            return sub_tasks
        else:
            print(f"  No decomposition applied for task: {task.task_id}")
            return [task] # Return the original task if no decomposition

# Example usage (for testing purposes, can be removed later)
# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    decomposer = TaskDecomposer()

    # Example 1: Task that can be decomposed
    complex_task = Task("Analyze data and generate report", input_data={"data": [1, 2, 3]})
    print("Original complex task:")
    print(complex_task)

    sub_tasks = decomposer.decompose(complex_task)
    print("\nSub-tasks created from complex task:")
    for st in sub_tasks:
        print(st)

    print("\nOriginal complex task after decomposition (should have sub_task_ids):")
    print(complex_task) # Print the original task again to show updated sub_task_ids

    print("-" * 20)

    # Example 2: Task that cannot be decomposed by this logic
    simple_task = Task("Write a poem about nature")
    print("Original simple task:")
    print(simple_task)

    sub_tasks_simple = decomposer.decompose(simple_task)
    print("\nSub-tasks from simple task:")
    for st in sub_tasks_simple:
        print(st)

    print("\nOriginal simple task after decomposition (should have no sub_task_ids):")
    print(simple_task)