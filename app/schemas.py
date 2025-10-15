from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class GoalInput(BaseModel):
    """Input schema for goal description."""
    goal: str = Field(..., description="The goal description to break down into tasks")
    additional_context: Optional[str] = Field(None, description="Additional context or constraints")


class TaskResponse(BaseModel):
    """Response schema for individual tasks."""
    id: Optional[int] = None
    title: str
    description: str
    estimated_hours: float
    priority: str = "medium"
    dependencies: List[int] = []
    deadline_days_from_start: int
    status: str = "pending"
    category: Optional[str] = None
    skills_required: List[str] = []
    deliverables: List[str] = []


class TaskPlanResponse(BaseModel):
    """Response schema for task plans."""
    id: Optional[int] = None
    goal: str
    title: str
    description: str
    estimated_duration_days: int
    tasks: List[TaskResponse]
    created_at: Optional[datetime] = None


class TaskPlanCreate(BaseModel):
    """Schema for creating task plans."""
    goal: str
    title: str
    description: str
    estimated_duration_days: int
    tasks: List[dict]


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status."""
    status: str = Field(..., pattern="^(pending|in_progress|completed)$")