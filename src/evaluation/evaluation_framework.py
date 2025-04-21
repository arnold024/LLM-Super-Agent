import abc
from typing import Any, Dict, List, Optional
from src.task_management.task import Task

class EvaluationResult:
    """
    Represents the result of an evaluation.
    """
    def __init__(self,
                 score: float,
                 feedback: str,
                 details: Optional[Dict[str, Any]] = None):
        """
        Initializes an EvaluationResult.

        Args:
            score: A numerical score for the evaluation (e.g., 0.0 to 1.0).
            feedback: Textual feedback on the evaluated item.
            details: Optional dictionary for additional evaluation details.
        """
        self.score = score
        self.feedback = feedback
        self.details = details if details is not None else {}

    def __repr__(self) -> str:
        return (f"EvaluationResult(score={self.score}, feedback='{self.feedback[:50]}...', "
                f"details_keys={list(self.details.keys())})")

class Evaluator(abc.ABC):
    """
    Abstract base class for an evaluator.
    Evaluators are responsible for assessing the quality or suitability of something,
    such as an agent's output or a task decomposition.
    """

    @abc.abstractmethod
    def evaluate(self, item: Any, criteria: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """
        Evaluates an item based on specified criteria.

        Args:
            item: The item to be evaluated (e.g., a Task object, an agent's output string).
            criteria: Optional dictionary containing criteria for the evaluation.

        Returns:
            An EvaluationResult object.
        """
        pass

# A simple placeholder evaluator implementation
class BasicEvaluator(Evaluator):
    """
    A basic concrete implementation of the Evaluator class.
    This is a placeholder and performs a very simple evaluation.
    """

    def evaluate(self, item: Any, criteria: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """
        Performs a basic evaluation.

        Args:
            item: The item to be evaluated.
            criteria: Optional criteria (not used in this basic implementation).

        Returns:
            A placeholder EvaluationResult.
        """
        print(f"Performing basic evaluation on item: {type(item)}")
        # Placeholder logic: always return a score of 1.0 with generic feedback
        return EvaluationResult(
            score=1.0,
            feedback="Basic evaluation completed successfully.",
            details={"evaluated_item_type": str(type(item))}
        )

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    basic_evaluator = BasicEvaluator()

    # Evaluate a dummy task
    dummy_task = Task("Evaluate this task")
    evaluation_of_task = basic_evaluator.evaluate(dummy_task)
    print("\nEvaluation of Task:")
    print(evaluation_of_task)

    print("-" * 20)

    # Evaluate a dummy string output
    dummy_output = "This is a sample output string."
    evaluation_of_output = basic_evaluator.evaluate(dummy_output)
    print("\nEvaluation of String Output:")
    print(evaluation_of_output)