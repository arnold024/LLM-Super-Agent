import logging
from typing import Dict, Any
from src.task_management.task import Task
from src.llm_integration.llm_interface import LLMInterface

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaskExecutor:
    """
    Executes a single task using a provided LLM connector.
    """

    def execute_task(self, task: Task, llm_connector: LLMInterface) -> Task:
        """
        Executes the given task using the specified LLM connector.

        Args:
            task: The Task object to execute.
            llm_connector: An instance of a class implementing LLMInterface.

        Returns:
            The updated Task object after execution.
        """
        logging.info(f"Starting execution for task: {task.task_id} with LLM: {llm_connector.get_model_name()}")
        task.update_status("in_progress")
        task.assign_llm(llm_connector.get_model_name())

        try:
            # Assuming the task's input_data contains the necessary prompt or parameters
            prompt = task.input_data.get("prompt")
            if not prompt:
                raise ValueError("Task input_data must contain a 'prompt' key.")

            # Pass all input_data as kwargs to the LLM connector, excluding 'prompt'
            llm_kwargs = {k: v for k, v in task.input_data.items() if k != "prompt"}

            response = llm_connector.generate_response(prompt=prompt, **llm_kwargs)

            task.add_output_data("response", response)
            task.update_status("completed")
            logging.info(f"Task completed successfully: {task.task_id}")

        except Exception as e:
            task.update_status("failed")
            task.add_output_data("error", str(e))
            logging.error(f"Task execution failed for {task.task_id}: {e}")

        return task

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # This example requires a dummy LLMInterface implementation
    class DummyLLM(LLMInterface):
        def __init__(self, name):
            self._name = name

        def generate_response(self, prompt: str, **kwargs) -> str:
            print(f"DummyLLM '{self._name}' received prompt: {prompt}")
            print(f"DummyLLM received kwargs: {kwargs}")
            if "error_test" in kwargs:
                 raise Exception("Simulated LLM error")
            return f"Dummy response to '{prompt[:30]}...' from {self._name}"

        def get_model_name(self) -> str:
            return self._name

    executor = TaskExecutor()
    dummy_llm = DummyLLM("dummy-model-1")

    # Test a successful task
    task1 = Task("Get a simple response", input_data={"prompt": "What is the capital of France?"})
    completed_task1 = executor.execute_task(task1, dummy_llm)
    print(completed_task1)

    print("-" * 20)

    # Test a task with missing prompt
    task2 = Task("Task with no prompt")
    completed_task2 = executor.execute_task(task2, dummy_llm)
    print(completed_task2)

    print("-" * 20)

    # Test a task with simulated LLM error
    task3 = Task("Task with simulated error", input_data={"prompt": "Generate something complex", "error_test": True})
    completed_task3 = executor.execute_task(task3, dummy_llm)
    print(completed_task3)