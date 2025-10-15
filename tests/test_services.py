import pytest
from app.services.task_planner import TaskPlannerService
from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_task_planner_service():
    """Test the task planner service."""
    llm_service = LLMService()
    planner = TaskPlannerService(llm_service)
    
    goal = "Create a simple website"
    plan = await planner.create_plan(goal)
    
    assert "title" in plan
    assert "description" in plan
    assert "tasks" in plan
    assert "estimated_duration_days" in plan
    assert len(plan["tasks"]) > 0
    
    # Check task structure
    task = plan["tasks"][0]
    assert "title" in task
    assert "description" in task
    assert "estimated_hours" in task
    assert "priority" in task
    assert "dependencies" in task
    assert "deadline_days_from_start" in task


@pytest.mark.asyncio
async def test_task_validation():
    """Test task validation in the planner service."""
    llm_service = LLMService()
    planner = TaskPlannerService(llm_service)
    
    # Test with invalid plan data
    invalid_plan = {
        "title": "Test Plan",
        "tasks": [
            {
                "title": "Task 1",
                "estimated_hours": -5,  # Invalid negative hours
                "priority": "invalid_priority",  # Invalid priority
                "dependencies": [5, 10],  # Invalid dependencies (future tasks)
                "deadline_days_from_start": -1  # Invalid negative deadline
            }
        ]
    }
    
    validated = planner._validate_plan(invalid_plan)
    
    task = validated["tasks"][0]
    assert task["estimated_hours"] >= 0.5  # Should be corrected
    assert task["priority"] == "medium"  # Should default to medium
    assert task["dependencies"] == []  # Should be empty (invalid deps removed)
    assert task["deadline_days_from_start"] >= 1  # Should be positive


def test_critical_path_calculation():
    """Test critical path calculation."""
    llm_service = LLMService()
    planner = TaskPlannerService(llm_service)
    
    tasks = [
        {"estimated_hours": 8, "dependencies": []},
        {"estimated_hours": 4, "dependencies": [0]},
        {"estimated_hours": 12, "dependencies": [0]},
        {"estimated_hours": 6, "dependencies": [1, 2]}
    ]
    
    critical_path = planner.calculate_critical_path(tasks)
    
    assert isinstance(critical_path, list)
    assert len(critical_path) > 0
    # Critical path should include task 3 (final task)
    assert 3 in critical_path