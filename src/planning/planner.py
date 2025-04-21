import abc
from typing import List, Dict, Any, Optional
from src.task_management.task import Task

class Planner(abc.ABC):
    """
    Abstract base class for a planner.
    Planners are responsible for generating sequences of tasks or actions
    to achieve a specific goal.
    """

    @abc.abstractmethod
    def generate_plan(self, goal_description: str, initial_context: Optional[Dict[str, Any]] = None) -> List[Task]:
        """
        Generates a plan (a list of tasks) to achieve a given goal.

        Args:
            goal_description: A description of the goal to achieve.
            initial_context: Optional initial context or information for planning.

        Returns:
            A list of Task objects representing the plan.
        """
        pass

    @abc.abstractmethod
    def adjust_plan(self, current_plan: List[Task], feedback: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Task]:
        """
        Adjusts an existing plan based on feedback and current context.

        Args:
            current_plan: The current list of Task objects representing the plan.
            feedback: Feedback received (e.g., from evaluation, agent communication).
            context: Optional current context or information for adjustment.

        Returns:
            An updated list of Task objects representing the adjusted plan.
        """
        pass

# A simple placeholder planner implementation
class BasicPlanner(Planner):
    """
    A basic concrete implementation of the Planner class.
    This is a placeholder and generates a very simple, fixed plan.
    """

    def generate_plan(self, goal_description: str, initial_context: Optional[Dict[str, Any]] = None) -> List[Task]:
        """
        Generates a placeholder plan based on the goal description.

        Args:
            goal_description: A description of the goal.
            initial_context: Optional initial context (not used in this basic implementation).

        Returns:
            A list of placeholder Task objects.
        """
        print(f"BasicPlanner generating plan for goal: '{goal_description}'")

        # Basic placeholder planning logic:
        # Create a fixed list of tasks based on the goal description.
        # In a real system, this would involve complex reasoning and potentially LLM calls.

        plan_tasks = []
        task1 = Task(f"Understand the goal: {goal_description}")
        task2 = Task("Gather relevant information")
        task3 = Task("Formulate a response or solution")
        task4 = Task("Review and refine the result")

        plan_tasks.append(task1)
        plan_tasks.append(task2)
        plan_tasks.append(task3)
        plan_tasks.append(task4)

        print(f"BasicPlanner generated {len(plan_tasks)} tasks.")
        return plan_tasks

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    basic_planner = BasicPlanner()

    goal = "Write a comprehensive report on climate change impacts."
    plan = basic_planner.generate_plan(goal)

    print("\nGenerated Plan:")
    for task in plan:
        print(task)