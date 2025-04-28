import queue
from typing import Optional
from src.task_management.task import Task

class TaskQueue:
    """
    A simple queue for managing tasks.
    """

    def __init__(self):
        """
        Initializes an empty TaskQueue.
        """
        self._queue = queue.Queue()

    def add_task(self, task: Task):
        """
        Adds a task to the queue.

        Args:
            task: The Task object to add.
        """
        self._queue.put(task)
        print(f"Task added to queue: {task.task_id}")

    def get_next_task(self) -> Optional[Task]:
        """
        Retrieves the next task from the queue.

        Returns:
            The next Task object, or None if the queue is empty.
        """
        try:
            task = self._queue.get_nowait()
            print(f"Task retrieved from queue: {task.task_id}")
            return task
        except queue.Empty:
            print("Task queue is empty.")
            return None

    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            True if the queue is empty, False otherwise.
        """
        return self._queue.empty()

    def qsize(self) -> int:
        """
        Returns the number of tasks in the queue.
        """
        return self._queue.qsize()

    def get_all_tasks(self) -> List[Task]:
        """
        Returns a list of all tasks currently in the queue without removing them.
        Note: This accesses the internal queue implementation and should be used with caution.
        """
        # Access the internal deque and convert it to a list
        return list(self._queue.queue)

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    task_queue = TaskQueue()

    task1 = Task("Process data file A")
    task2 = Task("Generate report B")

    task_queue.add_task(task1)
    task_queue.add_task(task2)

    print(f"Queue size: {task_queue.qsize()}")

    next_task = task_queue.get_next_task()
    if next_task:
        print(f"Processing task: {next_task.description}")

    print(f"Queue size: {task_queue.qsize()}")

    next_task = task_queue.get_next_task()
    if next_task:
        print(f"Processing task: {next_task.description}")

    print(f"Queue size: {task_queue.qsize()}")

    next_task = task_queue.get_next_task()
    if next_task:
        print(f"Processing task: {next_task.description}")