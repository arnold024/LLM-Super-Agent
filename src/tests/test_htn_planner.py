import pytest
from src.planning.htn_planner import HTNPlanner
from src.planning.plan_models import Plan, Step, ToolSpec

# Placeholder values for unused parameters
DUMMY_STATE = {}
DUMMY_MEMORY = None

# Sample tools for testing
SAMPLE_TOOLS = [
    ToolSpec(id="tool-water-001", name="get_water", description="Fetches water."),
    ToolSpec(id="tool-grounds-002", name="add_coffee_grounds", description="Adds grounds."),
    ToolSpec(id="tool-brew-003", name="brew", description="Brews the coffee."),
]

@pytest.fixture
def planner():
    """Fixture to create an HTNPlanner instance."""
    return HTNPlanner()

def test_planner_initialization(planner):
    """Test that the HTNPlanner initializes correctly."""
    assert isinstance(planner, HTNPlanner)
    # Check if the default methods and operators are loaded
    assert "make_coffee" in planner._methods # Check internal methods
    assert "get_water" in planner._operators # Check internal operators

def test_generate_plan_make_coffee_success(planner):
    """Test generating a plan for the 'make_coffee' task."""
    goal = "make_coffee"
    plan = planner.generate_plan(goal, DUMMY_STATE, SAMPLE_TOOLS, DUMMY_MEMORY)

    assert isinstance(plan, Plan)
    assert plan.metadata.get("status") == "success"
    assert len(plan.steps) == 3

    # Check step descriptions
    assert plan.steps[0].description == "Execute primitive action: get_water"
    assert plan.steps[1].description == "Execute primitive action: add_coffee_grounds"
    assert plan.steps[2].description == "Execute primitive action: brew"

    # Check prerequisites (sequential execution)
    assert plan.steps[0].prerequisites == [] # First step has no prerequisites
    assert plan.steps[1].prerequisites == [plan.steps[0].id]
    assert plan.steps[2].prerequisites == [plan.steps[1].id]

    # Check assigned tool IDs
    assert plan.steps[0].assigned_agent_tool_id == "tool-water-001"
    assert plan.steps[1].assigned_agent_tool_id == "tool-grounds-002"
    assert plan.steps[2].assigned_agent_tool_id == "tool-brew-003"

def test_generate_plan_primitive_goal(planner):
    """Test generating a plan for a goal that is already a primitive action."""
    goal = "get_water"
    # Ensure the tool for the primitive goal exists
    primitive_tools = [t for t in SAMPLE_TOOLS if t.name == goal]
    plan = planner.generate_plan(goal, DUMMY_STATE, primitive_tools, DUMMY_MEMORY)

    assert isinstance(plan, Plan)
    assert plan.metadata.get("status") == "success"
    assert len(plan.steps) == 1
    assert plan.steps[0].description == f"Execute primitive action: {goal}"
    assert plan.steps[0].prerequisites == []
    assert plan.steps[0].assigned_agent_tool_id == primitive_tools[0].id # Check tool ID

def test_generate_plan_unknown_goal(planner):
    """Test generating a plan for an unknown or non-decomposable goal."""
    goal = "make_tea" # Assuming 'make_tea' is not in the domain
    plan = planner.generate_plan(goal, DUMMY_STATE, SAMPLE_TOOLS, DUMMY_MEMORY) # Tools don't matter here

    assert isinstance(plan, Plan)
    assert plan.metadata.get("status") == "failed"
    assert len(plan.steps) == 0
    assert "Cannot decompose task" in plan.metadata.get("reason", "") # Check for the correct failure reason


def test_generate_plan_missing_tool(planner):
    """Test generating a plan when a required tool is missing."""
    goal = "make_coffee"
    # Provide tools, but missing the 'brew' tool
    missing_tools = [
        ToolSpec(id="tool-water-001", name="get_water", description="Fetches water."),
        ToolSpec(id="tool-grounds-002", name="add_coffee_grounds", description="Adds grounds."),
        # Missing: ToolSpec(id="tool-brew-003", name="brew", description="Brews the coffee."),
    ]
    plan = planner.generate_plan(goal, DUMMY_STATE, missing_tools, DUMMY_MEMORY)

    assert isinstance(plan, Plan)
    # Plan should still succeed according to Option A (warning and None)
    assert plan.metadata.get("status") == "success"
    assert len(plan.steps) == 3

    # Check assigned tool IDs - 'brew' step should have None
    assert plan.steps[0].assigned_agent_tool_id == "tool-water-001"
    assert plan.steps[1].assigned_agent_tool_id == "tool-grounds-002"
    assert plan.steps[2].assigned_agent_tool_id is None # Tool for 'brew' was missing
def test_adjust_plan_step_failure(planner):
    """Test adjusting the plan when a step fails."""
    goal = "make_coffee"
    # 1. Generate an initial plan
    initial_plan = planner.generate_plan(goal, DUMMY_STATE, SAMPLE_TOOLS, DUMMY_MEMORY)
    assert initial_plan.metadata.get("status") == "success"
    assert len(initial_plan.steps) == 3
    step0_id = initial_plan.steps[0].id # get_water
    step1_id = initial_plan.steps[1].id # add_coffee_grounds
    step2_id = initial_plan.steps[2].id # brew

    # Simulate step 0 completing (optional but makes state clearer)
    # initial_plan.get_step_by_id(step0_id).status = "completed"

    # 2. Define feedback for a failed middle step
    failed_step_id = step1_id
    feedback = {
        'failed_step_id': failed_step_id,
        'reason': 'Ran out of coffee grounds'
    }

    # 3. Call adjust_plan
    adjusted_plan = planner.adjust_plan(initial_plan, feedback, DUMMY_STATE, DUMMY_MEMORY)

    # 4. Assertions
    assert isinstance(adjusted_plan, Plan)

    # Check plan metadata
    assert adjusted_plan.metadata.get("status") == "failed"
    assert adjusted_plan.metadata.get("failed_step_id") == failed_step_id
    assert adjusted_plan.metadata.get("failure_reason") == 'Ran out of coffee grounds'

    # Check step statuses
    step0 = adjusted_plan.get_step_by_id(step0_id)
    step1 = adjusted_plan.get_step_by_id(step1_id)
    step2 = adjusted_plan.get_step_by_id(step2_id)

    assert step0 is not None
    assert step1 is not None
    assert step2 is not None

    assert step0.status == "pending" # Step 0 was not affected
    assert step1.status == "failed" # Step 1 is marked as failed
    assert step2.status == "cancelled" # Step 2 depends on Step 1 and should be cancelled
    assert "Cancelled due to failure" in step2.output_data.get("reason", "")

def test_adjust_plan_no_failure(planner):
    """Test adjust_plan when feedback indicates no failure."""
    goal = "make_coffee"
    initial_plan = planner.generate_plan(goal, DUMMY_STATE, SAMPLE_TOOLS, DUMMY_MEMORY)
    initial_plan_copy = Plan( # Create a copy for comparison
        goal=initial_plan.goal,
        steps=[s for s in initial_plan.steps], # Shallow copy steps
        metadata=initial_plan.metadata.copy()
    )

    feedback = {'status': 'in_progress', 'last_completed_step': initial_plan.steps[0].id}

    adjusted_plan = planner.adjust_plan(initial_plan, feedback, DUMMY_STATE, DUMMY_MEMORY)

    # Assert the plan is unchanged
    assert adjusted_plan.metadata == initial_plan_copy.metadata # Metadata should be same
    assert len(adjusted_plan.steps) == len(initial_plan_copy.steps)
    for i, step in enumerate(adjusted_plan.steps):
        assert step.id == initial_plan_copy.steps[i].id
        assert step.status == initial_plan_copy.steps[i].status # Statuses should be unchanged

def test_adjust_plan_invalid_failed_id(planner):
    """Test adjust_plan with an invalid failed_step_id."""
    goal = "make_coffee"
    initial_plan = planner.generate_plan(goal, DUMMY_STATE, SAMPLE_TOOLS, DUMMY_MEMORY)
    feedback = {'failed_step_id': 'invalid-step-id'}

    adjusted_plan = planner.adjust_plan(initial_plan, feedback, DUMMY_STATE, DUMMY_MEMORY)

    # Assert the plan status indicates an error during adjustment
    assert adjusted_plan.metadata.get("status") == "adjustment_error"
    assert "not found" in adjusted_plan.metadata.get("error_reason", "")