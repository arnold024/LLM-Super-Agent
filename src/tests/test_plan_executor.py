import pytest
from unittest.mock import MagicMock, call

from src.execution.plan_executor import PlanExecutor
from src.planning.plan_models import Plan, Step, ToolSpec
from src.plugins.plugin_manager import PluginManager # Assuming PluginManager is the tool registry


# TODO: Add test cases here
@pytest.fixture
def mock_plugin_manager():
    """Provides a mock PluginManager."""
    manager = MagicMock(spec=PluginManager)
    # Mock get_tool which is called by the executor
    manager.get_tool = MagicMock()
    return manager

def test_plan_executor_initialization(mock_plugin_manager):
    """Tests that PlanExecutor initializes correctly."""
    # Use 'tool_registry' argument name
    executor = PlanExecutor(tool_registry=mock_plugin_manager)
    assert executor.tool_registry == mock_plugin_manager
    assert isinstance(executor, PlanExecutor)
# --- Fixtures for Plan/Step Creation ---

@pytest.fixture
def simple_tool_spec():
    """Provides a simple ToolSpec."""
    # Use positional arguments for NamedTuple
    return ToolSpec(id="dummy_tool_id", name="dummy_tool", description="Dummy tool spec")

@pytest.fixture
def step_factory():
    """Factory fixture to create Step objects easily."""
    def _create_step(step_id, description="Test Step", tool_spec=None, prerequisites=None, status="pending", input_data=None):
        if tool_spec is None:
            # Use positional arguments for NamedTuple
            tool_spec = ToolSpec(id=f"tool_{step_id}_id", name=f"tool_{step_id}", description=f"Tool for step {step_id}")
        return Step(
            id=step_id, # Use 'id' instead of 'step_id' for Step dataclass field
            description=description,
            # Assign the tool ID, not the whole spec object
            assigned_agent_tool_id=tool_spec.id,
            prerequisites=prerequisites or [],
            status=status,
            input_data=input_data or {} # Allow passing input data
        )
    return _create_step

# --- Tests for Ready Step Identification ---

@pytest.mark.parametrize(
    "steps_data, expected_ready_ids",
    [
        ([], []), # No steps
        ([("step1", [], "pending")], ["step1"]), # Single pending step
        ([("step1", [], "completed")], []), # Single completed step
        ([("step1", [], "failed")], []), # Single failed step
        ([("step1", [], "running")], []), # Single running step
        ([ # Two independent pending steps
            ("step1", [], "pending"),
            ("step2", [], "pending"),
        ], ["step1", "step2"]),
        ([ # One depends on the other (both pending)
            ("step1", [], "pending"),
            ("step2", ["step1"], "pending"),
        ], ["step1"]),
        ([ # One depends on the other (first completed)
            ("step1", [], "completed"),
            ("step2", ["step1"], "pending"),
        ], ["step2"]),
        ([ # One depends on the other (first failed)
            ("step1", [], "failed"),
            ("step2", ["step1"], "pending"),
        ], []),
        ([ # One depends on the other (first running)
            ("step1", [], "running"),
            ("step2", ["step1"], "pending"),
        ], []),
        ([ # Complex dependencies
            ("step1", [], "completed"),
            ("step2", [], "pending"),
            ("step3", ["step1", "step2"], "pending"),
            ("step4", ["step1"], "pending"),
        ], ["step2", "step4"]),
         ([ # Depends on two completed
            ("step1", [], "completed"),
            ("step2", [], "completed"),
            ("step3", ["step1", "step2"], "pending"),
        ], ["step3"]),
        ([ # Depends on one completed, one pending
            ("step1", [], "completed"),
            ("step2", [], "pending"),
            ("step3", ["step1", "step2"], "pending"),
        ], ["step2"]), # Only step2 is ready initially
    ],
    ids=[
        "no_steps",
        "single_pending",
        "single_completed",
        "single_failed",
        "single_running",
        "two_independent_pending",
        "dependent_pending",
        "dependent_completed_prereq",
        "dependent_failed_prereq",
        "dependent_running_prereq",
        "complex_dependencies",
        "depends_on_two_completed",
        "depends_on_one_completed_one_pending",
    ]
)
def test_get_ready_steps(mock_plugin_manager, step_factory, steps_data, expected_ready_ids):
    """Tests the logic for identifying steps ready for execution."""
    steps = [step_factory(step_id=sid, prerequisites=prereqs, status=stat) for sid, prereqs, stat in steps_data]
    # Pass plan_id in metadata, add required 'goal'
    plan = Plan(goal="Identify Ready Steps", steps=steps, metadata={'plan_id': 'test_plan'})
    # Use 'tool_registry' argument name
    executor = PlanExecutor(tool_registry=mock_plugin_manager)

    # Accessing the private method for testing - adjust if name differs
    ready_steps = executor._get_ready_steps(plan)
    ready_step_ids = sorted([step.id for step in ready_steps])

    assert ready_step_ids == sorted(expected_ready_ids)
# --- Tests for Plan Execution ---

def test_execute_plan_success(mock_plugin_manager, step_factory):
    """Tests successful execution of a simple sequential plan."""
    # Arrange
    # Use positional args for ToolSpec, pass spec to factory
    tool_spec1 = ToolSpec(id="tool1_id", name="tool1", description="Tool 1")
    tool_spec2 = ToolSpec(id="tool2_id", name="tool2", description="Tool 2")
    step1 = step_factory(step_id="step1", tool_spec=tool_spec1, input_data={"arg": "a"})
    step2 = step_factory(step_id="step2", tool_spec=tool_spec2, input_data={"arg": "b"}, prerequisites=["step1"])
    # Pass plan_id in metadata, add required 'goal'
    plan = Plan(goal="Sequential Success", steps=[step1, step2], metadata={'plan_id': 'success_plan'})

    # Mock tool execution via get_tool
    mock_tool1 = MagicMock(return_value={"status": "success", "output": "output1"})
    mock_tool2 = MagicMock(return_value={"status": "success", "output": "output2"})
    mock_plugin_manager.get_tool.side_effect = lambda tool_id: mock_tool1 if tool_id == "tool1_id" else mock_tool2 if tool_id == "tool2_id" else MagicMock()

    # Use 'tool_registry' argument name
    executor = PlanExecutor(tool_registry=mock_plugin_manager)

    # Act
    result_plan = executor.execute_plan(plan)

    # Assert
    # Plan status
    assert result_plan.status == "completed"
    assert plan.status == "completed" # Check original plan object is updated

    # Step statuses (use get_step_by_id)
    assert plan.get_step_by_id("step1").status == "completed"
    assert plan.get_step_by_id("step2").status == "completed"
    assert plan.get_step_by_id("step1").output_data == {"status": "success", "output": "output1"}
    assert plan.get_step_by_id("step2").output_data == {"status": "success", "output": "output2"}


    # Tool invocation calls (check get_tool and the returned mocks)
    mock_plugin_manager.get_tool.assert_has_calls([call("tool1_id"), call("tool2_id")], any_order=False)
    mock_tool1.assert_called_once_with({"arg": "a"}) # Check input data passed to tool
    mock_tool2.assert_called_once_with({"arg": "b"}) # Check input data passed to tool
    assert mock_plugin_manager.get_tool.call_count == 2
def test_execute_plan_failure(mock_plugin_manager, step_factory):
    """Tests plan execution when a step fails."""
    # Arrange
    # Use positional args for ToolSpec, pass spec to factory
    tool_spec1 = ToolSpec(id="tool1_id", name="tool1", description="Tool 1")
    tool_spec2 = ToolSpec(id="tool2_id", name="tool2", description="Tool 2")
    tool_spec3 = ToolSpec(id="tool3_id", name="tool3", description="Tool 3")
    step1 = step_factory(step_id="step1", tool_spec=tool_spec1, input_data={"arg": "a"})
    step2 = step_factory(step_id="step2", tool_spec=tool_spec2, input_data={"arg": "b"}, prerequisites=["step1"])
    step3 = step_factory(step_id="step3", tool_spec=tool_spec3, input_data={"arg": "c"}, prerequisites=["step2"])
    # Pass plan_id in metadata, add required 'goal'
    plan = Plan(goal="Sequential Fail", steps=[step1, step2, step3], metadata={'plan_id': 'fail_plan'})

    # Mock tool execution via get_tool: step1 succeeds, step2 raises exception
    mock_tool1 = MagicMock(return_value={"status": "success", "output": "output1"})
    mock_tool2 = MagicMock(side_effect=Exception("Tool 2 failed intentionally"))
    mock_tool3 = MagicMock() # Should not be called
    mock_plugin_manager.get_tool.side_effect = lambda tool_id: mock_tool1 if tool_id == "tool1_id" else mock_tool2 if tool_id == "tool2_id" else mock_tool3 if tool_id == "tool3_id" else MagicMock()


    # Use 'tool_registry' argument name
    executor = PlanExecutor(tool_registry=mock_plugin_manager)

    # Act
    result_plan = executor.execute_plan(plan)

    # Assert
    # Plan status
    assert result_plan.status == "failed"
    assert plan.status == "failed"

    # Step statuses (use get_step_by_id)
    assert plan.get_step_by_id("step1").status == "completed"
    assert plan.get_step_by_id("step2").status == "failed"
    # Step 3 remains pending because its prerequisite (step2) failed
    assert plan.get_step_by_id("step3").status == "pending"
    assert plan.get_step_by_id("step1").output_data == {"status": "success", "output": "output1"}
    assert "error" in plan.get_step_by_id("step2").output_data # Check error info stored
    assert plan.get_step_by_id("step2").output_data["error"] == "Tool 2 failed intentionally"


    # Tool invocation calls (check get_tool and the returned mocks)
    mock_plugin_manager.get_tool.assert_has_calls([call("tool1_id"), call("tool2_id")], any_order=False)
    mock_tool1.assert_called_once_with({"arg": "a"})
    mock_tool2.assert_called_once_with({"arg": "b"})
    mock_tool3.assert_not_called() # Tool 3 should not have been called
    assert mock_plugin_manager.get_tool.call_count == 2 # Only first two tools retrieved
def test_execute_plan_prerequisites(mock_plugin_manager, step_factory):
    """Tests that steps are executed only after their prerequisites are met."""
    # Arrange
    # Use positional args for ToolSpec, pass spec to factory
    tool_spec_a = ToolSpec(id="toolA_id", name="toolA", description="Tool A")
    tool_spec_b = ToolSpec(id="toolB_id", name="toolB", description="Tool B")
    tool_spec_c = ToolSpec(id="toolC_id", name="toolC", description="Tool C")
    tool_spec_d = ToolSpec(id="toolD_id", name="toolD", description="Tool D")
    step_a = step_factory(step_id="stepA", tool_spec=tool_spec_a)
    step_b = step_factory(step_id="stepB", tool_spec=tool_spec_b, prerequisites=["stepA"])
    step_c = step_factory(step_id="stepC", tool_spec=tool_spec_c, prerequisites=["stepA"])
    step_d = step_factory(step_id="stepD", tool_spec=tool_spec_d) # Independent step
    # Pass plan_id in metadata, add required 'goal'
    plan = Plan(goal="Prerequisite Test", steps=[step_a, step_b, step_c, step_d], metadata={'plan_id': 'prereq_plan'})

    # Mock tool execution via get_tool to always succeed
    mock_tool_a = MagicMock(return_value={"status": "success", "output": "outputA"})
    mock_tool_b = MagicMock(return_value={"status": "success", "output": "outputB"})
    mock_tool_c = MagicMock(return_value={"status": "success", "output": "outputC"})
    mock_tool_d = MagicMock(return_value={"status": "success", "output": "outputD"})
    def side_effect_func(tool_id):
        if tool_id == "toolA_id": return mock_tool_a
        if tool_id == "toolB_id": return mock_tool_b
        if tool_id == "toolC_id": return mock_tool_c
        if tool_id == "toolD_id": return mock_tool_d
        return MagicMock()
    mock_plugin_manager.get_tool.side_effect = side_effect_func

    # Use 'tool_registry' argument name
    executor = PlanExecutor(tool_registry=mock_plugin_manager)

    # Act
    result_plan = executor.execute_plan(plan)

    # Assert
    # Plan status
    assert result_plan.status == "completed"
    assert plan.status == "completed"

    # Step statuses (use get_step_by_id)
    assert plan.get_step_by_id("stepA").status == "completed"
    assert plan.get_step_by_id("stepB").status == "completed"
    assert plan.get_step_by_id("stepC").status == "completed"
    assert plan.get_step_by_id("stepD").status == "completed"

    # Tool invocation calls - verify order using get_tool calls
    assert mock_plugin_manager.get_tool.call_count == 4
    mock_tool_a.assert_called_once_with({})
    mock_tool_b.assert_called_once_with({})
    mock_tool_c.assert_called_once_with({})
    mock_tool_d.assert_called_once_with({})

    # Check call order logic based on get_tool calls
    calls = mock_plugin_manager.get_tool.call_args_list
    call_ids = [c.args[0] for c in calls] # Extract the tool_id from each call

    try:
        idx_a = call_ids.index("toolA_id")
        idx_d = call_ids.index("toolD_id")
        idx_b = call_ids.index("toolB_id")
        idx_c = call_ids.index("toolC_id")
    except ValueError as e:
        pytest.fail(f"Expected tool ID not found in calls: {e}. Called IDs: {call_ids}")


    # Assert that B and C were called after A
    # Note: A and D could run in parallel, so we only check prerequisites
    assert idx_b > idx_a, f"Step B (index {idx_b}) called before Step A (index {idx_a})"
    assert idx_c > idx_a, f"Step C (index {idx_c}) called before Step A (index {idx_a})"
    # Cannot assert relative order of A and D, or B and C as they could be parallel