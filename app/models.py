from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TaskPlan(Base):
    """Task plan model representing a goal broken down into tasks."""
    __tablename__ = "task_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    goal = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    estimated_duration_days = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to tasks
    tasks = relationship("Task", back_populates="plan", cascade="all, delete-orphan")


class Task(Base):
    """Individual task model within a task plan."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("task_plans.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    estimated_hours = Column(Float)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    dependencies = Column(JSON, default=list)  # List of task IDs this task depends on
    deadline_days_from_start = Column(Integer)  # Days from project start
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    category = Column(String(50))  # research, design, development, testing, marketing, etc.
    skills_required = Column(JSON, default=list)  # Required skills for the task
    deliverables = Column(JSON, default=list)  # Expected deliverables
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to task plan
    plan = relationship("TaskPlan", back_populates="tasks")