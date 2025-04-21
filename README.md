# LLMSuperAgent (Phase 1 MVP)

This is the initial MVP of the LLMSuperAgent project, focusing on the core orchestration engine.

## Project Goal

To develop a dynamic, AI-powered orchestration platform that integrates multiple LLMs and external APIs to solve complex, multi-domain user problems in real-time.

## Phase 1 Deliverables Achieved

- Functional core orchestration engine (basic sequential execution).
- Basic API integration framework (abstract interface and placeholder connector).
- Rudimentary task management (Task, TaskQueue, TaskExecutor).
- Basic agent abstraction (Agent base class and BasicAgent implementation).

## Current Functionality

The current implementation provides a basic framework to:
1. Define tasks (`src/task_management/task.py`).
2. Add tasks to a queue (`src/task_management/task_queue.py`).
3. Execute tasks using an LLM connector (`src/task_management/task_executor.py`).
4. Define agents that use LLM connectors to process tasks (`src/agent/agent.py`, `src/agent/basic_agent.py`).
5. Orchestrate the sequential execution of tasks from the queue using available agents (`src/orchestrator/simple_orchestrator.py`).
6. Manage API keys from environment variables (`src/llm_integration/api_key_manager.py`).
7. Provides an abstract interface for LLM connectors (`src/llm_integration/llm_interface.py`) and a generic placeholder implementation (`src/llm_integration/generic_llm_connector.py`).

## How to Run the Example

The `simple_orchestrator.py` file contains an example usage block (`if __name__ == "__main__":`) that demonstrates how to create agents with dummy LLM connectors, add tasks to the orchestrator, and run the orchestration process.

To run this example:

1. Ensure you have Python installed.
2. Install the `python-dotenv` package: `pip install python-dotenv` (This is needed by `api_key_manager.py`, although the current example doesn't strictly require it as it uses a dummy connector).
3. Navigate to the project's root directory in your terminal.
4. Execute the `simple_orchestrator.py` file: `python src/orchestrator/simple_orchestrator.py`

This will run the example, demonstrating tasks being added to the queue and processed sequentially by the basic agents using the dummy LLM connectors.

## Next Steps (Phase 2)

Phase 2 will focus on enabling collaborative reasoning and evaluation between LLM agents.

## Project Plan

Refer to `./memory-bank/LLMSuperAgent_Plan.md` for the detailed project plan.