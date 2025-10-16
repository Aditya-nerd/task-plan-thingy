from typing import Dict, Any, List
from app.services.llm_service import LLMService


class TaskPlannerService:
    """Service for creating and managing task plans."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def create_plan(self, goal: str) -> Dict[str, Any]:
        """
        Create a comprehensive task plan from a goal.
        
        Args:
            goal: The goal description
            
        Returns:
            Dict containing the structured task plan
        """
        # Generate task breakdown using LLM
        plan_data = await self.llm_service.generate_task_breakdown(goal)
        
        # Validate and enhance the plan
        validated_plan = self._validate_plan(plan_data)
        
        # Add task sequencing and optimization
        optimized_plan = self._optimize_task_sequence(validated_plan)
        
        return optimized_plan

    # Backwards-compatible alias for older call sites
    async def generate_plan(self, goal: str) -> Dict[str, Any]:
        """Alias to maintain backward compatibility with older callers."""
        return await self.create_plan(goal)
    
    def _validate_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean up the generated plan.
        
        Args:
            plan_data: Raw plan data from LLM
            
        Returns:
            Validated plan data
        """
        # Ensure required fields exist
        validated = {
            "title": plan_data.get("title", "Task Plan"),
            "description": plan_data.get("description", "Generated task plan"),
            "estimated_duration_days": max(1, plan_data.get("estimated_duration_days", 14)),
            "tasks": []
        }
        
        # Validate each task
        tasks = plan_data.get("tasks", [])
        for i, task in enumerate(tasks):
            validated_task = {
                "title": task.get("title", f"Task {i+1}"),
                "description": task.get("description", "Task description"),
                "estimated_hours": max(0.5, float(task.get("estimated_hours", 4.0))),
                "priority": self._validate_priority(task.get("priority", "medium")),
                "dependencies": self._validate_dependencies(task.get("dependencies", []), i),
                "deadline_days_from_start": max(1, int(task.get("deadline_days_from_start", i+1)))
            }
            validated["tasks"].append(validated_task)
        
        return validated
    
    def _validate_priority(self, priority: str) -> str:
        """Validate task priority."""
        valid_priorities = ["low", "medium", "high", "critical"]
        return priority.lower() if priority.lower() in valid_priorities else "medium"
    
    def _validate_dependencies(self, dependencies: List[int], current_index: int) -> List[int]:
        """Validate task dependencies to prevent circular references."""
        # Filter out invalid dependencies (self-references and future tasks)
        valid_deps = [
            dep for dep in dependencies 
            if isinstance(dep, int) and 0 <= dep < current_index
        ]
        return valid_deps
    
    def _optimize_task_sequence(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize task sequencing for better project flow.
        
        Args:
            plan_data: Validated plan data
            
        Returns:
            Optimized plan data
        """
        tasks = plan_data["tasks"]
        
        # Sort tasks by priority and dependencies for better scheduling
        priority_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        # Calculate task complexity scores
        for i, task in enumerate(tasks):
            task["complexity_score"] = (
                priority_weights.get(task["priority"], 2) * 2 +
                len(task["dependencies"]) +
                min(task["estimated_hours"] / 4, 5)  # Cap hours influence
            )
        
        # Ensure deadlines are realistic based on dependencies
        for i, task in enumerate(tasks):
            if task["dependencies"]:
                max_dep_deadline = max(
                    tasks[dep]["deadline_days_from_start"] 
                    for dep in task["dependencies"]
                )
                # Ensure current task starts after dependencies with buffer
                min_start = max_dep_deadline + 1
                task["deadline_days_from_start"] = max(
                    task["deadline_days_from_start"], 
                    min_start + max(1, int(task["estimated_hours"] / 8))
                )
        
        # Update overall project duration based on latest task deadline
        if tasks:
            max_deadline = max(task["deadline_days_from_start"] for task in tasks)
            plan_data["estimated_duration_days"] = max(
                plan_data["estimated_duration_days"], 
                max_deadline
            )
        
        return plan_data
    
    def calculate_critical_path(self, tasks: List[Dict[str, Any]]) -> List[int]:
        """
        Calculate the critical path through the tasks.
        
        Args:
            tasks: List of task dictionaries
            
        Returns:
            List of task indices representing the critical path
        """
        # Simple critical path calculation
        # In a full implementation, this would use proper CPM algorithm
        
        task_finish_times = {}
        
        # Calculate earliest finish time for each task
        for i, task in enumerate(tasks):
            earliest_start = 0
            if task["dependencies"]:
                earliest_start = max(
                    task_finish_times.get(dep, 0) 
                    for dep in task["dependencies"]
                )
            
            duration = task["estimated_hours"] / 8  # Convert hours to days
            task_finish_times[i] = earliest_start + duration
        
        # Find the longest path (simplified critical path)
        critical_tasks = []
        current_task = max(task_finish_times.keys(), key=lambda x: task_finish_times[x])
        
        while current_task is not None:
            critical_tasks.append(current_task)
            # Find the dependency with the latest finish time
            deps = tasks[current_task]["dependencies"]
            if deps:
                current_task = max(deps, key=lambda x: task_finish_times[x])
            else:
                current_task = None
        
        return list(reversed(critical_tasks))